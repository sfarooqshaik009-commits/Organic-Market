import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

from .models import Category, Product, Order, Review
from .serializers import CategorySerializer, ProductSerializer


def send_admin_order_notification(order):
    """Sends an email notification to the store owner with the packing list."""
    try:
        subject = f"📦 NEW ORDER #{order.id} - Pack Items Immediately!"
        message_body = (
            f"🔔 New Order Received on OrganicMarket!\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📦 ORDER DETAILS (#{order.id})\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Customer Name : {order.customer_name}\n"
            f"📞 Phone Number   : {order.phone}\n"
            f"📍 Delivery Address:\n{order.address}\n\n"
            f"🛒 ITEMS TO PACK:\n{order.order_items}\n\n"
            f"💰 Total Amount   : ₹{order.total_amount}\n"
            f"💳 Payment Method : {order.payment_method}\n"
            f"🔖 Ref / UTR No.  : {order.transaction_id}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🚚 Open Driver Dashboard: http://127.0.0.1:8000/driver/dashboard/"
        )

        admin_email = getattr(settings, 'STORE_ADMIN_EMAIL', '')
        sender_email = getattr(settings, 'EMAIL_HOST_USER', admin_email)

        if admin_email and 'your_store_email' not in admin_email:
            send_mail(
                subject=subject,
                message=message_body,
                from_email=sender_email,
                recipient_list=[admin_email],
                fail_silently=False,
            )
        else:
            print("\n" + "="*50)
            print(f"📦 NEW ORDER RECEIVED TO PACK! (#{order.id})")
            print(f"Customer: {order.customer_name} ({order.phone})")
            print(f"Address : {order.address}")
            print(f"Items   : {order.order_items}")
            print("="*50 + "\n")
    except Exception as e:
        print(f"❌ Failed to send admin email notification: {e}")


def send_order_notification_sms(order, domain_url):
    """Sends automated SMS notification to customer via Twilio."""
    if not TWILIO_AVAILABLE:
        return

    try:
        account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        twilio_number = getattr(settings, 'TWILIO_PHONE_NUMBER', '')

        if not account_sid or 'your_account_sid' in account_sid:
            return

        client = Client(account_sid, auth_token)
        tracking_url = f"{domain_url}/my-orders/"

        message_body = (
            f"🎉 Thank you for your order with OrganicMarket!\n\n"
            f"📦 Order ID: #{order.id}\n"
            f"💰 Total Amount: ₹{order.total_amount}\n"
            f"💳 Payment Method: {order.payment_method}\n\n"
            f"🚚 Track your delivery driver live here: {tracking_url}"
        )

        phone = order.phone.strip()
        if not phone.startswith('+'):
            phone = f"+91{phone}"

        client.messages.create(
            body=message_body,
            from_=twilio_number,
            to=phone
        )
    except Exception as e:
        print(f"❌ Failed to send Twilio notification: {e}")


def home_view(request):
    """Fetches all available products with unit metrics and review ratings."""
    products_qs = Product.objects.filter(is_available=True).select_related('category').prefetch_related('reviews').order_by('id')

    seen_names = set()
    db_products = []

    for p in products_qs:
        clean_name = p.name.strip().lower()
        if clean_name not in seen_names:
            seen_names.add(clean_name)
            db_products.append({
                'id': p.id,
                'name': p.name.strip(),
                'category_name': p.category.name.lower() if p.category else 'vegetables',
                'base_price': float(p.price),  # 1 kg / 1 unit base price
                'price': float(p.price),
                'stock_qty': p.stock_qty,
                'image': p.image.strip() if p.image else '',
                'description': p.description.strip() if p.description else 'Fresh organic produce directly from local farms.',
                'avg_rating': p.average_rating,
                'total_reviews': p.total_reviews
            })

    return render(request, 'index.html', {'db_products': db_products})

# --- FARMER / SELLER PRODUCE PORTAL VIEWS ---

@login_required
def farmer_dashboard_view(request):
    """Renders the farmer inventory dashboard."""
    farmer_products = Product.objects.filter(farmer=request.user).select_related('category').order_by('-created_at')
    categories = Category.objects.all()
    
    total_listed = farmer_products.count()
    active_listings = farmer_products.filter(is_available=True).count()
    
    context = {
        'farmer_products': farmer_products,
        'categories': categories,
        'total_listed': total_listed,
        'active_listings': active_listings
    }
    return render(request, 'farmer_dashboard.html', context)


@csrf_exempt
@login_required
def add_farmer_product(request):
    """API to add new harvested produce directly from the farmer portal."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            category_id = data.get('category_id')
            category = get_object_or_404(Category, id=category_id)

            product = Product.objects.create(
                farmer=request.user,
                category=category,
                name=data.get('name').strip(),
                price=float(data.get('price')),
                stock_qty=int(data.get('stock_qty', 50)),
                image=data.get('image', '').strip(),
                description=data.get('description', '').strip() or '100% freshly harvested organic produce.',
                is_available=True
            )

            return JsonResponse({'success': True, 'message': f'"{product.name}" listed successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


@csrf_exempt
@login_required
def toggle_product_status(request, product_id):
    """Toggles active/out of stock status for a farmer's product."""
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id, farmer=request.user)
            product.is_available = not product.is_available
            product.save()
            return JsonResponse({'success': True, 'is_available': product.is_available})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False}, status=405)


@csrf_exempt
@login_required
def delete_farmer_product(request, product_id):
    """Deletes a produce listing owned by the farmer."""
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id, farmer=request.user)
            product.delete()
            return JsonResponse({'success': True, 'message': 'Produce listing deleted successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False}, status=405)


# --- REVIEWS, ORDERS & DRIVER GPS VIEWS ---

@csrf_exempt
def submit_review(request, product_id):
    """Submits a customer rating and review for a product."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product = get_object_or_404(Product, id=product_id)
            
            user_name = data.get('user_name', 'Verified Customer').strip() or 'Verified Customer'
            rating = int(data.get('rating', 5))
            comment = data.get('comment', '').strip()

            if not comment:
                return JsonResponse({'success': False, 'error': 'Comment cannot be empty.'}, status=400)

            Review.objects.create(
                product=product,
                user_name=user_name,
                rating=rating,
                comment=comment
            )

            return JsonResponse({
                'success': True,
                'avg_rating': product.average_rating,
                'total_reviews': product.total_reviews,
                'message': 'Review submitted successfully!'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False}, status=405)


def get_product_reviews(request, product_id):
    """Fetches all reviews for a product."""
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    
    reviews_data = [{
        'user_name': r.user_name,
        'rating': r.rating,
        'comment': r.comment,
        'created_at': r.created_at.strftime('%b %d, %Y')
    } for r in reviews]

    return JsonResponse({
        'success': True,
        'product_name': product.name,
        'avg_rating': product.average_rating,
        'total_reviews': product.total_reviews,
        'reviews': reviews_data
    })


@csrf_exempt
def place_order(request):
    """API endpoint to receive and store customer orders."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                customer_name=data.get('name'),
                phone=data.get('phone'),
                address=data.get('address'),
                payment_method=data.get('payment_method'),
                transaction_id=data.get('transaction_id', ''),
                total_amount=data.get('total_amount'),
                order_items=data.get('order_items'),
                status='Pending',
                dest_latitude=13.5501,
                dest_longitude=78.5026
            )

            send_admin_order_notification(order)
            domain_url = request.build_absolute_uri('/')[:-1]
            send_order_notification_sms(order, domain_url)

            return JsonResponse({'success': True, 'order_id': order.id, 'message': 'Order placed successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


@login_required
def orders_view(request):
    """Renders user order history."""
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {'orders': user_orders})


def driver_dashboard_view(request):
    """List available orders for delivery agents."""
    available_orders = Order.objects.filter(status__in=['Pending', 'Accepted', 'Out for Delivery']).order_by('-created_at')
    return render(request, 'driver_dashboard.html', {'orders': available_orders})


@csrf_exempt
def accept_order(request, order_id):
    """Driver accepts an order to start delivery."""
    if request.method == 'POST':
        try:
            order = get_object_or_404(Order, id=order_id)
            order.status = 'Out for Delivery'
            order.save()
            return JsonResponse({'success': True, 'redirect_url': f'/driver/{order.id}/'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False}, status=405)


def driver_portal_view(request, order_id):
    """Driver mobile tracking and navigation page."""
    order = get_object_or_404(Order, id=order_id)
    if order.status != 'Out for Delivery':
        order.status = 'Out for Delivery'
        order.save()
    return render(request, 'driver_tracking.html', {'order': order})


@csrf_exempt
def update_driver_location(request):
    """Receives live GPS updates from driver."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order = Order.objects.get(id=data.get('order_id'))
            order.driver_latitude = float(data.get('latitude'))
            order.driver_longitude = float(data.get('longitude'))
            order.status = 'Out for Delivery'
            order.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False}, status=405)


def get_driver_location(request, order_id):
    """Returns live driver coordinates to customer map."""
    try:
        order = Order.objects.get(id=order_id)
        return JsonResponse({
            'success': True,
            'status': order.status,
            'latitude': order.driver_latitude,
            'longitude': order.driver_longitude
        })
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found'}, status=404)


def register_view(request):
    """User registration view."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer