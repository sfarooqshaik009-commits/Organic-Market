
import json
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from rest_framework import viewsets

try:
    from twilio.rest import Client

    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

from .models import Category, Order, Product, Review
from .serializers import CategorySerializer, ProductSerializer


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def parse_json_body(request):
    """
    Safely parse JSON request body.
    Returns:
        (data, error_response)
    """
    try:
        if not request.body:
            return {}, None

        data = json.loads(request.body)

        if not isinstance(data, dict):
            return None, JsonResponse(
                {
                    "success": False,
                    "error": "Request body must be a JSON object.",
                },
                status=400,
            )

        return data, None

    except json.JSONDecodeError:
        return None, JsonResponse(
            {
                "success": False,
                "error": "Invalid JSON request body.",
            },
            status=400,
        )


def clean_string(value, field_name, required=True, max_length=None):
    """
    Normalize and validate a string value.
    """
    if value is None:
        value = ""

    value = str(value).strip()

    if required and not value:
        raise ValueError(f"{field_name} is required.")

    if max_length and len(value) > max_length:
        raise ValueError(
            f"{field_name} cannot exceed {max_length} characters."
        )

    return value


def parse_decimal(value, field_name, minimum=Decimal("0")):
    """
    Safely convert a value to Decimal.
    """
    if value is None or value == "":
        raise ValueError(f"{field_name} is required.")

    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"Invalid {field_name}.")

    if number < minimum:
        raise ValueError(
            f"{field_name} cannot be less than {minimum}."
        )

    return number


def parse_integer(value, field_name, minimum=0):
    """
    Safely convert a value to integer.
    """
    if value is None or value == "":
        raise ValueError(f"{field_name} is required.")

    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid {field_name}.")

    if number < minimum:
        raise ValueError(
            f"{field_name} cannot be less than {minimum}."
        )

    return number


def normalize_phone(phone):
    """
    Normalize Indian phone numbers.

    Examples:
        9876543210 -> +919876543210
        +919876543210 -> +919876543210
        919876543210 -> +919876543210
    """
    phone = clean_string(
        phone,
        "Phone number",
        required=True,
        max_length=20,
    )

    digits = "".join(character for character in phone if character.isdigit())

    if phone.startswith("+"):
        normalized = f"+{digits}"
    elif len(digits) == 10:
        normalized = f"+91{digits}"
    elif len(digits) == 12 and digits.startswith("91"):
        normalized = f"+{digits}"
    else:
        raise ValueError(
            "Please enter a valid Indian phone number."
        )

    if len(normalized) != 13 or not normalized.startswith("+91"):
        raise ValueError(
            "Please enter a valid 10-digit Indian phone number."
        )

    return normalized


def is_driver(request):
    """
    Determines whether the logged-in user is allowed to use
    driver functionality.

    Staff/superusers are automatically allowed.

    You can later replace this with a dedicated Driver model
    or Django group.
    """
    if not request.user.is_authenticated:
        return False

    if request.user.is_staff or request.user.is_superuser:
        return True

    return request.user.groups.filter(
        name__iexact="Driver"
    ).exists()


def get_public_domain(request):
    """
    Build the current site's absolute base URL.
    """
    return request.build_absolute_uri("/").rstrip("/")


# ============================================================
# EMAIL / SMS NOTIFICATIONS
# ============================================================

def send_admin_order_notification(order):
    """
    Send an email notification to the store owner.

    Email failures do NOT prevent the order from being created.
    """
    try:
        subject = (
            f"📦 NEW ORDER #{order.id} - "
            f"Pack Items Immediately!"
        )

        message_body = (
            f"🔔 New Order Received on OrganicMarket!\n\n"
            f"========================================\n"
            f"📦 ORDER DETAILS (#{order.id})\n"
            f"========================================\n"
            f"👤 Customer Name : {order.customer_name}\n"
            f"📞 Phone Number  : {order.phone}\n"
            f"📍 Delivery Address:\n{order.address}\n\n"
            f"🛒 ITEMS TO PACK:\n"
            f"{order.order_items}\n\n"
            f"💰 Total Amount   : ₹{order.total_amount}\n"
            f"💳 Payment Method : {order.payment_method}\n"
            f"🔖 Ref / UTR No.  : "
            f"{order.transaction_id or 'N/A'}\n"
            f"========================================\n\n"
            f"🚚 Driver Dashboard:\n"
            f"/driver/dashboard/"
        )

        admin_email = getattr(
            settings,
            "STORE_ADMIN_EMAIL",
            "",
        )

        sender_email = getattr(
            settings,
            "EMAIL_HOST_USER",
            "",
        ) or admin_email

        if (
            admin_email
            and sender_email
            and "your_store_email" not in admin_email
        ):
            send_mail(
                subject=subject,
                message=message_body,
                from_email=sender_email,
                recipient_list=[admin_email],
                fail_silently=False,
            )
        else:
            print("\n" + "=" * 60)
            print(
                f"📦 NEW ORDER RECEIVED TO PACK! "
                f"(#{order.id})"
            )
            print(
                f"Customer: {order.customer_name} "
                f"({order.phone})"
            )
            print(f"Address : {order.address}")
            print(f"Items   : {order.order_items}")
            print(
                f"Total   : ₹{order.total_amount}"
            )
            print("=" * 60 + "\n")

    except Exception as exc:
        print(
            "❌ Failed to send admin email notification: "
            f"{exc}"
        )


def send_order_notification_sms(order, domain_url):
    """
    Send customer SMS through Twilio.

    SMS failures do NOT prevent the order from being created.
    """
    if not TWILIO_AVAILABLE:
        return

    try:
        account_sid = getattr(
            settings,
            "TWILIO_ACCOUNT_SID",
            "",
        )

        auth_token = getattr(
            settings,
            "TWILIO_AUTH_TOKEN",
            "",
        )

        twilio_number = getattr(
            settings,
            "TWILIO_PHONE_NUMBER",
            "",
        )

        if not account_sid or not auth_token or not twilio_number:
            return

        if "your_account_sid" in account_sid:
            return

        if "your_auth_token" in auth_token:
            return

        tracking_url = f"{domain_url}/my-orders/"

        message_body = (
            "🎉 Thank you for your order with "
            "OrganicMarket!\n\n"
            f"📦 Order ID: #{order.id}\n"
            f"💰 Total: ₹{order.total_amount}\n"
            f"💳 Payment: {order.payment_method}\n\n"
            f"🚚 Track your order:\n{tracking_url}"
        )

        client = Client(
            account_sid,
            auth_token,
        )

        client.messages.create(
            body=message_body,
            from_=twilio_number,
            to=order.phone,
        )

    except Exception as exc:
        print(
            "❌ Failed to send Twilio notification: "
            f"{exc}"
        )


# ============================================================
# HOME / PRODUCT DISPLAY
# ============================================================

@require_GET
def home_view(request):
    """
    Display all available products.
    """
    products_qs = (
        Product.objects
        .filter(is_available=True)
        .select_related("category")
        .prefetch_related("reviews")
        .order_by("id")
    )

    seen_names = set()
    db_products = []

    for product in products_qs:
        clean_name = product.name.strip().lower()

        if clean_name in seen_names:
            continue

        seen_names.add(clean_name)

        db_products.append(
            {
                "id": product.id,
                "name": product.name.strip(),
                "category_name": (
                    product.category.name.lower()
                    if product.category
                    else "vegetables"
                ),
                "base_price": float(product.price),
                "price": float(product.price),
                "stock_qty": product.stock_qty,
                "image": (
                    product.image.strip()
                    if product.image
                    else ""
                ),
                "description": (
                    product.description.strip()
                    if product.description
                    else (
                        "Fresh organic produce directly "
                        "from local farms."
                    )
                ),
                "avg_rating": product.average_rating,
                "total_reviews": product.total_reviews,
            }
        )

    return render(
        request,
        "index.html",
        {
            "db_products": db_products,
        },
    )


# ============================================================
# FARMER / SELLER PORTAL
# ============================================================

@login_required
@require_GET
def farmer_dashboard_view(request):
    """
    Render farmer inventory dashboard.
    """
    farmer_products = (
        Product.objects
        .filter(farmer=request.user)
        .select_related("category")
        .order_by("-created_at")
    )

    categories = Category.objects.all().order_by("name")

    total_listed = farmer_products.count()

    active_listings = farmer_products.filter(
        is_available=True
    ).count()

    context = {
        "farmer_products": farmer_products,
        "categories": categories,
        "total_listed": total_listed,
        "active_listings": active_listings,
    }

    return render(
        request,
        "farmer_dashboard.html",
        context,
    )


@login_required
@require_POST
def add_farmer_product(request):
    """
    Add a new product from the farmer portal.
    """
    data, error_response = parse_json_body(request)

    if error_response:
        return error_response

    try:
        category_id = data.get("category_id")

        if not category_id:
            raise ValueError(
                "Product category is required."
            )

        category = get_object_or_404(
            Category,
            id=category_id,
        )

        name = clean_string(
            data.get("name"),
            "Product name",
            required=True,
            max_length=200,
        )

        price = parse_decimal(
            data.get("price"),
            "price",
        )

        stock_qty = parse_integer(
            data.get("stock_qty", 50),
            "stock quantity",
        )

        image = clean_string(
            data.get("image", ""),
            "Image URL",
            required=False,
            max_length=500,
        )

        description = clean_string(
            data.get("description", ""),
            "Description",
            required=False,
        )

        if not description:
            description = (
                "100% freshly harvested "
                "organic produce."
            )

        product = Product.objects.create(
            farmer=request.user,
            category=category,
            name=name,
            price=price,
            stock_qty=stock_qty,
            image=image or None,
            description=description,
            is_available=stock_qty > 0,
        )

        return JsonResponse(
            {
                "success": True,
                "message": (
                    f'"{product.name}" '
                    "listed successfully!"
                ),
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "price": float(product.price),
                    "stock_qty": product.stock_qty,
                    "is_available": (
                        product.is_available
                    ),
                },
            },
            status=201,
        )

    except ValueError as exc:
        return JsonResponse(
            {
                "success": False,
                "error": str(exc),
            },
            status=400,
        )

    except Exception as exc:
        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Unable to create product."
                ),
            },
            status=500,
        )


@login_required
@require_POST
def toggle_product_status(request, product_id):
    """
    Toggle availability of a farmer's own product.
    """
    product = get_object_or_404(
        Product,
        id=product_id,
        farmer=request.user,
    )

    if product.stock_qty <= 0:
        product.is_available = False
    else:
        product.is_available = not product.is_available

    product.save(
        update_fields=["is_available"]
    )

    return JsonResponse(
        {
            "success": True,
            "is_available": product.is_available,
        }
    )


@login_required
@require_POST
def delete_farmer_product(request, product_id):
    """
    Delete a product belonging to the logged-in farmer.
    """
    product = get_object_or_404(
        Product,
        id=product_id,
        farmer=request.user,
    )

    product.delete()

    return JsonResponse(
        {
            "success": True,
            "message": (
                "Produce listing deleted "
                "successfully."
            ),
        }
    )


# ============================================================
# REVIEWS
# ============================================================

@require_POST
def submit_review(request, product_id):
    """
    Submit a product review.

    A user must be logged in to submit a review.
    """
    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Please log in before "
                    "submitting a review."
                ),
            },
            status=401,
        )

    data, error_response = parse_json_body(request)

    if error_response:
        return error_response

    try:
        product = get_object_or_404(
            Product,
            id=product_id,
        )

        user_name = clean_string(
            data.get(
                "user_name",
                request.user.get_full_name()
                or request.user.username,
            ),
            "Name",
            required=True,
            max_length=100,
        )

        rating = parse_integer(
            data.get("rating", 5),
            "rating",
            minimum=1,
        )

        if rating > 5:
            raise ValueError(
                "Rating must be between 1 and 5."
            )

        comment = clean_string(
            data.get("comment"),
            "Comment",
            required=True,
        )

        Review.objects.create(
            product=product,
            user_name=user_name,
            rating=rating,
            comment=comment,
        )

        return JsonResponse(
            {
                "success": True,
                "avg_rating": product.average_rating,
                "total_reviews": product.total_reviews,
                "message": (
                    "Review submitted "
                    "successfully!"
                ),
            },
            status=201,
        )

    except ValueError as exc:
        return JsonResponse(
            {
                "success": False,
                "error": str(exc),
            },
            status=400,
        )

    except Exception:
        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Unable to submit review."
                ),
            },
            status=500,
        )


@require_GET
def get_product_reviews(request, product_id):
    """
    Return reviews for a product.
    """
    product = get_object_or_404(
        Product,
        id=product_id,
    )

    reviews = product.reviews.all()

    reviews_data = [
        {
            "user_name": review.user_name,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": (
                review.created_at.strftime(
                    "%b %d, %Y"
                )
            ),
        }
        for review in reviews
    ]

    return JsonResponse(
        {
            "success": True,
            "product_name": product.name,
            "avg_rating": product.average_rating,
            "total_reviews": product.total_reviews,
            "reviews": reviews_data,
        }
    )


# ============================================================
# ORDER CREATION
# ============================================================

@require_POST
def place_order(request):
    """
    Create a customer order.

    IMPORTANT:
    The server calculates the order total from the
    submitted product IDs and quantities instead of
    trusting total_amount sent by JavaScript.
    """
    data, error_response = parse_json_body(request)

    if error_response:
        return error_response

    try:
        customer_name = clean_string(
            data.get("name"),
            "Customer name",
            required=True,
            max_length=150,
        )

        phone = normalize_phone(
            data.get("phone")
        )

        address = clean_string(
            data.get("address"),
            "Delivery address",
            required=True,
        )

        payment_method = clean_string(
            data.get("payment_method"),
            "Payment method",
            required=True,
            max_length=50,
        )

        transaction_id = clean_string(
            data.get("transaction_id", ""),
            "Transaction ID",
            required=False,
            max_length=100,
        )

        # ----------------------------------------------------
        # Accept multiple common cart formats.
        # ----------------------------------------------------

        raw_items = data.get("items")

        if raw_items is None:
            raw_items = data.get("cart")

        if raw_items is None:
            raw_items = data.get("products")

        # If the frontend only sends order_items as a
        # formatted string, we cannot securely calculate
        # the price from it.
        if not isinstance(raw_items, list):
            return JsonResponse(
                {
                    "success": False,
                    "error": (
                        "Cart items are missing. "
                        "Please send an items array."
                    ),
                },
                status=400,
            )

        if not raw_items:
            return JsonResponse(
                {
                    "success": False,
                    "error": (
                        "Your cart is empty."
                    ),
                },
                status=400,
            )

        # ----------------------------------------------------
        # Normalize cart items.
        # ----------------------------------------------------

        normalized_items = []

        for item in raw_items:
            if not isinstance(item, dict):
                raise ValueError(
                    "Invalid cart item."
                )

            product_id = (
                item.get("product_id")
                or item.get("id")
            )

            quantity = (
                item.get("quantity")
                if item.get("quantity") is not None
                else item.get("qty")
            )

            if not product_id:
                raise ValueError(
                    "Cart item is missing product ID."
                )

            quantity = parse_integer(
                quantity,
                "quantity",
                minimum=1,
            )

            if quantity > 100:
                raise ValueError(
                    "Maximum quantity per product "
                    "is 100."
                )

            normalized_items.append(
                {
                    "product_id": product_id,
                    "quantity": quantity,
                }
            )

        # ----------------------------------------------------
        # Atomic transaction.
        # ----------------------------------------------------

        with transaction.atomic():

            product_ids = [
                item["product_id"]
                for item in normalized_items
            ]

            products = (
                Product.objects
                .select_for_update()
                .select_related("category")
                .filter(
                    id__in=product_ids,
                    is_available=True,
                )
            )

            products_by_id = {
                product.id: product
                for product in products
            }

            if len(products_by_id) != len(
                set(product_ids)
            ):
                raise ValueError(
                    "One or more products are "
                    "unavailable or do not exist."
                )

            total_amount = Decimal("0.00")
            order_lines = []

            for item in normalized_items:
                product = products_by_id[
                    int(item["product_id"])
                ]

                quantity = item["quantity"]

                if product.stock_qty < quantity:
                    raise ValueError(
                        f"Only {product.stock_qty} "
                        f"units of '{product.name}' "
                        "are available."
                    )

                line_total = (
                    product.price
                    * Decimal(quantity)
                )

                total_amount += line_total

                order_lines.append(
                    f"{product.name} x {quantity} "
                    f"@ ₹{product.price} = "
                    f"₹{line_total:.2f}"
                )

            # ------------------------------------------------
            # Decrease inventory.
            # ------------------------------------------------

            for item in normalized_items:
                product = products_by_id[
                    int(item["product_id"])
                ]

                quantity = item["quantity"]

                product.stock_qty -= quantity

                if product.stock_qty <= 0:
                    product.stock_qty = 0
                    product.is_available = False

                product.save(
                    update_fields=[
                        "stock_qty",
                        "is_available",
                    ]
                )

            # ------------------------------------------------
            # Optional delivery coordinates.
            #
            # These must come from the frontend only if
            # they are actual coordinates supplied by the
            # customer/map system.
            # ------------------------------------------------

            dest_latitude = None
            dest_longitude = None

            if data.get("dest_latitude") not in (
                None,
                "",
            ):
                try:
                    dest_latitude = float(
                        data["dest_latitude"]
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    raise ValueError(
                        "Invalid destination latitude."
                    )

            if data.get("dest_longitude") not in (
                None,
                "",
            ):
                try:
                    dest_longitude = float(
                        data["dest_longitude"]
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    raise ValueError(
                        "Invalid destination longitude."
                    )

            # ------------------------------------------------
            # Create order.
            # ------------------------------------------------

            order = Order.objects.create(
                user=(
                    request.user
                    if request.user.is_authenticated
                    else None
                ),
                customer_name=customer_name,
                phone=phone,
                address=address,
                payment_method=payment_method,
                transaction_id=transaction_id,
                total_amount=total_amount,
                order_items="\n".join(
                    order_lines
                ),
                status="Pending",
                dest_latitude=dest_latitude,
                dest_longitude=dest_longitude,
            )

        # ----------------------------------------------------
        # Notifications happen AFTER successful transaction.
        # ----------------------------------------------------

        send_admin_order_notification(order)

        domain_url = get_public_domain(request)

        send_order_notification_sms(
            order,
            domain_url,
        )

        return JsonResponse(
            {
                "success": True,
                "order_id": order.id,
                "total_amount": float(
                    order.total_amount
                ),
                "message": (
                    "Order placed successfully!"
                ),
            },
            status=201,
        )

    except ValueError as exc:
        return JsonResponse(
            {
                "success": False,
                "error": str(exc),
            },
            status=400,
        )

    except Exception as exc:
        print(
            "❌ Order creation error:",
            exc,
        )

        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Unable to place order. "
                    "Please try again."
                ),
            },
            status=500,
        )


# ============================================================
# CUSTOMER ORDERS
# ============================================================

@login_required
@require_GET
def orders_view(request):
    """
    Display only the logged-in user's orders.
    """
    user_orders = (
        Order.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )

    return render(
        request,
        "orders.html",
        {
            "orders": user_orders,
        },
    )


# ============================================================
# DRIVER DASHBOARD
# ============================================================

@login_required
@require_GET
def driver_dashboard_view(request):
    """
    Driver dashboard.

    Only staff/superusers or users in the Driver group
    can access it.
    """
    if not is_driver(request):
        return JsonResponse(
            {
                "success": False,
                "error": (
                    "You are not authorized "
                    "to access the driver dashboard."
                ),
            },
            status=403,
        )

    available_orders = (
        Order.objects
        .filter(
            status__in=[
                "Pending",
                "Accepted",
                "Out for Delivery",
            ]
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "driver_dashboard.html",
        {
            "orders": available_orders,
        },
    )


@login_required
@require_POST
def accept_order(request, order_id):
    """
    Driver accepts a pending order.

    Uses select_for_update() so two drivers cannot
    simultaneously accept the same pending order.
    """
    if not is_driver(request):
        return JsonResponse(
            {
                "success": False,
                "error": "Driver access required.",
            },
            status=403,
        )

    try:
        with transaction.atomic():

            order = (
                Order.objects
                .select_for_update()
                .get(id=order_id)
            )

            if order.status != "Pending":
                return JsonResponse(
                    {
                        "success": False,
                        "error": (
                            "This order is no longer "
                            "available for acceptance."
                        ),
                        "status": order.status,
                    },
                    status=409,
                )

            order.status = "Out for Delivery"

            order.save(
                update_fields=["status"]
            )

        return JsonResponse(
            {
                "success": True,
                "order_id": order.id,
                "status": order.status,
                "redirect_url": (
                    f"/driver/{order.id}/"
                ),
            }
        )

    except Order.DoesNotExist:
        return JsonResponse(
            {
                "success": False,
                "error": "Order not found.",
            },
            status=404,
        )


@login_required
@require_GET
def driver_portal_view(request, order_id):
    """
    Driver mobile tracking page.
    """
    if not is_driver(request):
        return JsonResponse(
            {
                "success": False,
                "error": "Driver access required.",
            },
            status=403,
        )

    order = get_object_or_404(
        Order,
        id=order_id,
    )

    if order.status == "Pending":
        order.status = "Out for Delivery"

        order.save(
            update_fields=["status"]
        )

    return render(
        request,
        "driver_tracking.html",
        {
            "order": order,
        },
    )


# ============================================================
# DRIVER GPS
# ============================================================

@login_required
@require_POST
def update_driver_location(request):
    """
    Receive live GPS coordinates from an authorized driver.
    """
    if not is_driver(request):
        return JsonResponse(
            {
                "success": False,
                "error": "Driver access required.",
            },
            status=403,
        )

    data, error_response = parse_json_body(request)

    if error_response:
        return error_response

    try:
        order_id = data.get("order_id")

        if not order_id:
            raise ValueError(
                "Order ID is required."
            )

        latitude = float(
            data.get("latitude")
        )

        longitude = float(
            data.get("longitude")
        )

        # Validate GPS range.
        if not -90 <= latitude <= 90:
            raise ValueError(
                "Invalid latitude."
            )

        if not -180 <= longitude <= 180:
            raise ValueError(
                "Invalid longitude."
            )

        order = get_object_or_404(
            Order,
            id=order_id,
        )

        if order.status == "Completed":
            return JsonResponse(
                {
                    "success": False,
                    "error": (
                        "This order has already "
                        "been completed."
                    ),
                },
                status=409,
            )

        order.driver_latitude = latitude
        order.driver_longitude = longitude
        order.status = "Out for Delivery"

        order.save(
            update_fields=[
                "driver_latitude",
                "driver_longitude",
                "status",
            ]
        )

        return JsonResponse(
            {
                "success": True,
                "latitude": latitude,
                "longitude": longitude,
                "status": order.status,
            }
        )

    except (TypeError, ValueError):
        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Invalid GPS coordinates."
                ),
            },
            status=400,
        )


@require_GET
def get_driver_location(request, order_id):
    """
    Return driver location to the customer.

    A customer can only access their own order.
    Staff/driver users can access orders for tracking.
    """
    order = get_object_or_404(
        Order,
        id=order_id,
    )

    if request.user.is_authenticated:

        allowed = (
            request.user.is_staff
            or request.user.is_superuser
            or order.user_id == request.user.id
            or is_driver(request)
        )

        if not allowed:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Access denied.",
                },
                status=403,
            )

    else:
        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Please log in to track "
                    "your order."
                ),
            },
            status=401,
        )

    return JsonResponse(
        {
            "success": True,
            "status": order.status,
            "latitude": order.driver_latitude,
            "longitude": order.driver_longitude,
            "destination_latitude": (
                order.dest_latitude
            ),
            "destination_longitude": (
                order.dest_longitude
            ),
        }
    )


# ============================================================
# AUTHENTICATION
# ============================================================

def register_view(request):
    """
    User registration.
    """
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = UserCreationForm(
            request.POST
        )

        if form.is_valid():
            user = form.save()

            login(
                request,
                user,
            )

            return redirect("home")

    else:
        form = UserCreationForm()

    return render(
        request,
        "register.html",
        {
            "form": form,
        },
    )


# ============================================================
# REST FRAMEWORK API VIEWSETS
# ============================================================

class CategoryViewSet(
    viewsets.ReadOnlyModelViewSet
):
    """
    Read-only category API.
    """
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer


class ProductViewSet(
    viewsets.ReadOnlyModelViewSet
):
    """
    Read-only product API.
    """
    queryset = (
        Product.objects
        .filter(is_available=True)
        .select_related("category", "farmer")
        .prefetch_related("reviews")
        .order_by("-created_at")
    )

    serializer_class = ProductSerializer

