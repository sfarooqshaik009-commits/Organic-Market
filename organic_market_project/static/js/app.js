// ============================================================
// ORGANIC MARKET - FRONTEND JAVASCRIPT
// ============================================================

// Configuration: Your Bank UPI ID & Store Name
const STORE_UPI_ID = "6302189220@axl";
const STORE_NAME = "OrganicMarket";

let products = [];
let cart = [];
let currentCategory = 'all';
let selectedReviewProductId = null;

// Track active chosen weight variant per product
// Default: 1 kg
let selectedVariants = {};


// ============================================================
// CSRF HELPER
// ============================================================

function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');

        for (let cookie of cookies) {
            cookie = cookie.trim();

            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }

    return cookieValue;
}


// ============================================================
// COMMON FETCH HEADERS
// ============================================================

function getJsonHeaders() {
    const csrfToken = getCookie('csrftoken');

    const headers = {
        'Content-Type': 'application/json'
    };

    if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
    }

    return headers;
}


// ============================================================
// PRODUCT IMAGE HANDLING
// ============================================================

function getProductImage(item) {
    if (
        item.image &&
        item.image.trim() !== '' &&
        !item.image.includes('photo-1592924357228-91a4daadcfea')
    ) {
        return item.image.trim();
    }

    const name = (item.name || '').toLowerCase();
    const cat = (
        item.category ||
        item.category_name ||
        ''
    ).toLowerCase();

    if (name.includes('spinach') || name.includes('palak')) {
        return 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?auto=format&fit=crop&w=400&q=80';
    }

    if (name.includes('carrot') || name.includes('gajar')) {
        return 'https://images.unsplash.com/photo-1598170845058-12ef4a457939?auto=format&fit=crop&w=400&q=80';
    }

    if (name.includes('broccoli')) {
        return 'https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?auto=format&fit=crop&w=400&q=80';
    }

    if (name.includes('tomato') || name.includes('tamatar')) {
        return 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=400&q=80';
    }

    if (name.includes('apple')) {
        return 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=400&q=80';
    }

    if (name.includes('banana')) {
        return 'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?auto=format&fit=crop&w=400&q=80';
    }

    if (name.includes('strawberr')) {
        return 'https://images.unsplash.com/photo-1464965911861-746a04b4bca6?auto=format&fit=crop&w=400&q=80';
    }

    if (name.includes('blueberr')) {
        return 'https://images.unsplash.com/photo-1498557850523-fd3d118b962e?auto=format&fit=crop&w=400&q=80';
    }

    if (name.includes('kiwi') || name.includes('kivi')) {
        return 'https://images.unsplash.com/photo-1585059819970-07f9760f3316?auto=format&fit=crop&w=400&q=80';
    }

    if (name.includes('orange')) {
        return 'https://images.unsplash.com/photo-1547514701-42782101795e?auto=format&fit=crop&w=400&q=80';
    }

    if (
        name.includes('vermicompost') ||
        name.includes('compost') ||
        name.includes('manure')
    ) {
        return 'https://images.unsplash.com/photo-1628352081506-83c43123ed6d?auto=format&fit=crop&w=400&q=80';
    }

    if (
        name.includes('neem') ||
        name.includes('oil') ||
        name.includes('cake') ||
        name.includes('bone')
    ) {
        return 'https://images.unsplash.com/photo-1615485290382-441e4d049cb5?auto=format&fit=crop&w=400&q=80';
    }

    if (cat.includes('fruit')) {
        return 'https://images.unsplash.com/photo-1610832958506-aa56368176cf?auto=format&fit=crop&w=400&q=80';
    }

    if (cat.includes('fertilizer')) {
        return 'https://images.unsplash.com/photo-1585314062340-f1a5a7c9328d?auto=format&fit=crop&w=400&q=80';
    }

    return 'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=400&q=80';
}


// ============================================================
// LOAD PRODUCTS FROM DJANGO
// ============================================================

function loadDatabaseProducts() {
    try {
        const djangoDataElement =
            document.getElementById('django-products-data');

        if (
            djangoDataElement &&
            djangoDataElement.textContent.trim()
        ) {
            const dbData = JSON.parse(
                djangoDataElement.textContent
            );

            if (Array.isArray(dbData) && dbData.length > 0) {
                products = dbData.map(p => ({
                    id: p.id,
                    name: p.name || "Organic Product",

                    category: String(
                        p.category_name ||
                        p.category ||
                        'vegetables'
                    )
                        .toLowerCase()
                        .trim(),

                    base_price: parseFloat(
                        p.base_price ||
                        p.price ||
                        0
                    ),

                    image: getProductImage(p),

                    desc:
                        p.description ||
                        'Fresh organic product directly from local farms.',

                    avg_rating:
                        parseFloat(p.avg_rating || 5.0),

                    total_reviews:
                        parseInt(p.total_reviews || 0, 10),

                    stock_qty:
                        parseInt(p.stock_qty || 0, 10)
                }));

                // Initialize default unit selection
                products.forEach(p => {
                    if (!selectedVariants[p.id]) {
                        selectedVariants[p.id] = {
                            label: '1 kg',
                            factor: 1.0
                        };
                    }
                });
            }
        }
    } catch (e) {
        console.error(
            "❌ Error loading products:",
            e
        );
    }
}


// ============================================================
// TOAST MESSAGE
// ============================================================

function showToast(message) {
    let toast =
        document.getElementById('toast-notification');

    if (!toast) {
        toast = document.createElement('div');

        toast.id = 'toast-notification';

        toast.style.cssText = `
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%) translateY(20px);
            background-color: #2e7d32;
            color: #ffffff;
            padding: 12px 24px;
            border-radius: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.25);
            font-weight: 600;
            font-size: 0.95rem;
            z-index: 2000;
            opacity: 0;
            transition: opacity 0.3s ease,
                        transform 0.3s ease;
            pointer-events: none;
        `;

        document.body.appendChild(toast);
    }

    toast.textContent = message;

    toast.style.opacity = '1';

    toast.style.transform =
        'translateX(-50%) translateY(0)';

    if (toast.timeoutId) {
        clearTimeout(toast.timeoutId);
    }

    toast.timeoutId = setTimeout(() => {
        toast.style.opacity = '0';

        toast.style.transform =
            'translateX(-50%) translateY(20px)';
    }, 2500);
}


// ============================================================
// SEARCH
// ============================================================

function handleSearchInput(e) {
    const query =
        e.target.value.trim().toLowerCase();

    const hero =
        document.getElementById('hero-banner');

    if (hero) {
        hero.style.display =
            query.length > 0
                ? 'none'
                : (currentCategory === 'all'
                    ? 'block'
                    : 'none');
    }

    renderProducts(
        currentCategory,
        query
    );
}


// ============================================================
// RATINGS
// ============================================================

function renderStars(rating) {
    const safeRating =
        parseFloat(rating) || 0;

    const fullStars =
        Math.floor(safeRating);

    let starsHtml =
        '★'.repeat(fullStars);

    if (safeRating - fullStars >= 0.5) {
        starsHtml += '½';
    }

    return starsHtml;
}


// ============================================================
// UNIT / WEIGHT CHANGE
// ============================================================

function handleUnitChange(productId, selectElem) {
    const selectedOption =
        selectElem.options[
            selectElem.selectedIndex
        ];

    const factor =
        parseFloat(selectedOption.value);

    const label =
        selectedOption.text
            .split(' - ')[0]
            .trim();

    selectedVariants[productId] = {
        label: label,
        factor: factor
    };

    const product =
        products.find(
            p => p.id === productId
        );

    if (product) {
        const calculatedPrice =
            (
                product.base_price *
                factor
            ).toFixed(2);

        const priceElem =
            document.getElementById(
                `price-tag-${productId}`
            );

        if (priceElem) {
            priceElem.textContent =
                `₹${calculatedPrice}`;
        }
    }
}


// ============================================================
// RENDER PRODUCTS
// ============================================================

function renderProducts(
    category = 'all',
    searchQuery = ''
) {
    const grid =
        document.getElementById('product-grid');

    if (!grid) return;

    grid.innerHTML = '';

    currentCategory = category;

    const selectedCategory =
        String(category)
            .toLowerCase()
            .trim()
            .replace(/s$/, '');

    const cleanSearchQuery =
        String(searchQuery)
            .toLowerCase()
            .trim();

    const filtered =
        products.filter(p => {
            const pName =
                String(p.name)
                    .toLowerCase();

            const pCat =
                String(p.category)
                    .toLowerCase()
                    .trim()
                    .replace(/s$/, '');

            const pDesc =
                String(p.desc)
                    .toLowerCase();

            const matchesCategory =
                selectedCategory === 'all' ||
                pCat.includes(selectedCategory) ||
                selectedCategory.includes(pCat);

            const matchesSearch =
                cleanSearchQuery === '' ||
                pName.includes(cleanSearchQuery) ||
                pDesc.includes(cleanSearchQuery) ||
                pCat.includes(cleanSearchQuery);

            return (
                matchesCategory &&
                matchesSearch
            );
        });

    if (filtered.length === 0) {
        grid.innerHTML = `
            <div style="
                grid-column: 1/-1;
                text-align: center;
                color: #666;
                padding: 3rem;
            ">
                <p style="
                    font-size: 1.2rem;
                    font-weight: bold;
                    margin-bottom: 0.5rem;
                ">
                    No products found
                </p>

                <p style="
                    font-size: 0.9rem;
                ">
                    Try searching for something else
                    like Spinach, Apple, or Compost.
                </p>
            </div>
        `;

        return;
    }

    filtered.forEach(p => {
        const currentVariant =
            selectedVariants[p.id] || {
                label: '1 kg',
                factor: 1.0
            };

        const displayPrice =
            (
                p.base_price *
                currentVariant.factor
            ).toFixed(2);

        const card =
            document.createElement('div');

        card.className = 'card';

        card.innerHTML = `
            <img
                src="${p.image}"
                alt="${p.name}"
                class="card-img"
                onerror="
                    this.src='https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=400&q=80'
                "
            >

            <div class="card-body">

                <div>
                    <h3 class="card-title">
                        ${p.name}
                    </h3>

                    <div
                        class="rating-badge"
                        onclick="openReviewsModal(${p.id})"
                    >
                        <span class="stars">
                            ${renderStars(
                                p.avg_rating || 5.0
                            )}
                        </span>

                        <strong>
                            ${(p.avg_rating || 5.0).toFixed(1)}
                        </strong>

                        <span class="review-count">
                            (${p.total_reviews || 0} reviews)
                        </span>
                    </div>

                    <p class="card-desc">
                        ${p.desc}
                    </p>
                </div>

                <div style="margin-bottom: 0.8rem;">

                    <label
                        style="
                            font-size: 0.8rem;
                            font-weight: bold;
                            color: #555;
                            display: block;
                            margin-bottom: 0.2rem;
                        "
                    >
                        Select Quantity / Weight:
                    </label>

                    <select
                        onchange="
                            handleUnitChange(${p.id}, this)
                        "
                        style="
                            width: 100%;
                            padding: 0.4rem;
                            border: 1.5px solid #2e7d32;
                            border-radius: 4px;
                            font-weight: 600;
                            color: #1b5e20;
                            background: #fff;
                            cursor: pointer;
                        "
                    >
                        <option
                            value="1.0"
                            ${
                                currentVariant.factor === 1.0
                                    ? 'selected'
                                    : ''
                            }
                        >
                            1 kg -
                            (₹${p.base_price.toFixed(2)})
                        </option>

                        <option
                            value="0.5"
                            ${
                                currentVariant.factor === 0.5
                                    ? 'selected'
                                    : ''
                            }
                        >
                            500g (½ kg) -
                            (₹${(
                                p.base_price * 0.5
                            ).toFixed(2)})
                        </option>

                        <option
                            value="0.25"
                            ${
                                currentVariant.factor === 0.25
                                    ? 'selected'
                                    : ''
                            }
                        >
                            250g (¼ kg) -
                            (₹${(
                                p.base_price * 0.25
                            ).toFixed(2)})
                        </option>

                        <option
                            value="2.0"
                            ${
                                currentVariant.factor === 2.0
                                    ? 'selected'
                                    : ''
                            }
                        >
                            2 kg Family Pack -
                            (₹${(
                                p.base_price * 2.0
                            ).toFixed(2)})
                        </option>
                    </select>
                </div>

                <div class="card-footer">

                    <span
                        class="price"
                        id="price-tag-${p.id}"
                    >
                        ₹${displayPrice}
                    </span>

                    <button
                        class="btn"
                        onclick="addToCart(${p.id})"
                    >
                        + Add to Cart
                    </button>

                </div>

            </div>
        `;

        grid.appendChild(card);
    });
}


// ============================================================
// CATEGORY FILTER
// ============================================================

function filterCategory(cat) {
    const sectionTitle =
        document.getElementById(
            'section-title'
        );

    if (sectionTitle) {
        sectionTitle.textContent =
            cat.charAt(0).toUpperCase() +
            cat.slice(1);
    }

    const searchInput =
        document.getElementById(
            'search-input'
        );

    if (searchInput) {
        searchInput.value = '';
    }

    const hero =
        document.getElementById(
            'hero-banner'
        );

    if (hero) {
        hero.style.display = 'none';
    }

    renderProducts(cat, '');
}


// ============================================================
// HOME
// ============================================================

function showHome() {
    const sectionTitle =
        document.getElementById(
            'section-title'
        );

    if (sectionTitle) {
        sectionTitle.textContent =
            'All Organic Products';
    }

    const searchInput =
        document.getElementById(
            'search-input'
        );

    if (searchInput) {
        searchInput.value = '';
    }

    const hero =
        document.getElementById(
            'hero-banner'
        );

    if (hero) {
        hero.style.display = 'block';
    }

    renderProducts('all', '');
}


// ============================================================
// ADD TO CART
// ============================================================

function addToCart(productId) {
    const product =
        products.find(
            p => p.id === productId
        );

    if (!product) {
        showToast('❌ Product not found.');
        return;
    }

    const variant =
        selectedVariants[productId] || {
            label: '1 kg',
            factor: 1.0
        };

    const itemPrice =
        parseFloat(
            (
                product.base_price *
                variant.factor
            ).toFixed(2)
        );

    const cartItemId =
        `${productId}-${variant.label}`;

    const existing =
        cart.find(
            item =>
                item.cartItemId === cartItemId
        );

    if (existing) {
        existing.qty += 1;
    } else {
        cart.push({
            cartItemId: cartItemId,
            id: product.id,
            name: product.name,
            unitLabel: variant.label,
            price: itemPrice,
            image: product.image,
            qty: 1
        });
    }

    updateCartUI();

    showToast(
        `🛒 ${product.name} (${variant.label}) added to cart!`
    );
}


// ============================================================
// CART UI
// ============================================================

function updateCartUI() {
    const cartItems =
        document.getElementById(
            'cart-items'
        );

    const cartCount =
        document.getElementById(
            'cart-count'
        );

    const cartTotal =
        document.getElementById(
            'cart-total'
        );

    const checkoutBtn =
        document.getElementById(
            'checkout-btn'
        );

    const totalQty =
        cart.reduce(
            (sum, item) =>
                sum + item.qty,
            0
        );

    const totalPrice =
        cart.reduce(
            (sum, item) =>
                sum +
                (
                    item.price *
                    item.qty
                ),
            0
        );

    if (cartCount) {
        cartCount.textContent =
            totalQty;
    }

    if (cartTotal) {
        cartTotal.textContent =
            `₹${totalPrice.toFixed(2)}`;
    }

    if (!cartItems) return;

    if (cart.length === 0) {
        cartItems.innerHTML = `
            <p
                class="empty-msg"
                style="
                    text-align: center;
                    color: #777;
                    margin-top: 2rem;
                "
            >
                Your cart is empty.
            </p>
        `;

        if (checkoutBtn) {
            checkoutBtn.disabled = true;
        }

        return;
    }

    if (checkoutBtn) {
        checkoutBtn.disabled = false;
    }

    cartItems.innerHTML =
        cart.map(item => `
            <div class="cart-item">

                <img
                    src="${item.image}"
                    alt="${item.name}"
                >

                <div style="flex-grow: 1;">

                    <strong
                        style="
                            display: block;
                            color: #1b5e20;
                        "
                    >
                        ${item.name}
                    </strong>

                    <span
                        style="
                            font-size: 0.8rem;
                            background: #e8f5e9;
                            color: #2e7d32;
                            padding: 2px 6px;
                            border-radius: 4px;
                            font-weight: bold;
                        "
                    >
                        ${item.unitLabel}
                    </span>

                    <div
                        style="
                            font-size: 0.85rem;
                            color: #555;
                            margin-top: 2px;
                        "
                    >
                        ₹${item.price.toFixed(2)}
                        × ${item.qty}
                        =
                        ₹${(
                            item.price *
                            item.qty
                        ).toFixed(2)}
                    </div>

                </div>

                <div
                    class="qty-controls"
                    style="
                        display: flex;
                        align-items: center;
                        gap: 0.3rem;
                    "
                >

                    <button
                        onclick="
                            changeQty(
                                '${item.cartItemId}',
                                -1
                            )
                        "
                    >
                        -
                    </button>

                    <span
                        style="
                            font-weight: bold;
                            min-width: 18px;
                            text-align: center;
                        "
                    >
                        ${item.qty}
                    </span>

                    <button
                        onclick="
                            changeQty(
                                '${item.cartItemId}',
                                1
                            )
                        "
                    >
                        +
                    </button>

                </div>

            </div>
        `).join('');
}


// ============================================================
// CHANGE CART QUANTITY
// ============================================================

function changeQty(cartItemId, delta) {
    const item =
        cart.find(
            i =>
                i.cartItemId === cartItemId
        );

    if (!item) return;

    item.qty += delta;

    if (item.qty <= 0) {
        cart =
            cart.filter(
                i =>
                    i.cartItemId !==
                    cartItemId
            );
    }

    updateCartUI();
}


// ============================================================
// TOGGLE CART
// ============================================================

function toggleCart() {
    const sidebar =
        document.getElementById(
            'cart-sidebar'
        );

    const overlay =
        document.getElementById(
            'cart-overlay'
        );

    if (sidebar) {
        sidebar.classList.toggle(
            'active'
        );
    }

    if (overlay) {
        overlay.classList.toggle(
            'active'
        );
    }
}


// ============================================================
// REVIEWS
// ============================================================

function setRating(rating) {
    const ratingInput =
        document.getElementById(
            'rev-rating'
        );

    if (ratingInput) {
        ratingInput.value = rating;
    }

    const stars =
        document.querySelectorAll(
            '#star-selector span'
        );

    stars.forEach(
        (star, index) => {
            if (index < rating) {
                star.classList.add(
                    'selected'
                );
            } else {
                star.classList.remove(
                    'selected'
                );
            }
        }
    );
}


async function openReviewsModal(productId) {
    selectedReviewProductId =
        productId;

    const product =
        products.find(
            p => p.id === productId
        );

    if (!product) return;

    const modalProductName =
        document.getElementById(
            'modal-product-name'
        );

    if (modalProductName) {
        modalProductName.textContent =
            `⭐ ${product.name} Reviews`;
    }

    setRating(5);

    try {
        const res =
            await fetch(
                `/api/reviews/${productId}/`
            );

        const data =
            await res.json();

        if (data.success) {
            const avgRating =
                parseFloat(
                    data.avg_rating || 0
                );

            const avgRatingElement =
                document.getElementById(
                    'modal-avg-rating'
                );

            if (avgRatingElement) {
                avgRatingElement.innerHTML = `
                    Average Rating:
                    <strong
                        style="color: #2e7d32;"
                    >
                        ${avgRating.toFixed(1)} ★
                    </strong>
                    (${data.total_reviews || 0} reviews)
                `;
            }

            const container =
                document.getElementById(
                    'reviews-list-container'
                );

            if (!container) return;

            if (
                !data.reviews ||
                data.reviews.length === 0
            ) {
                container.innerHTML = `
                    <p
                        style="
                            color: #777;
                            font-size: 0.9rem;
                        "
                    >
                        No reviews yet.
                        Be the first to review
                        this organic produce!
                    </p>
                `;
            } else {
                container.innerHTML =
                    data.reviews.map(
                        r => `
                            <div class="review-card">

                                <div
                                    style="
                                        display: flex;
                                        justify-content: space-between;
                                        align-items: center;
                                        margin-bottom: 0.2rem;
                                    "
                                >
                                    <strong
                                        style="
                                            color: #1b5e20;
                                        "
                                    >
                                        ${r.user_name}
                                    </strong>

                                    <span
                                        style="
                                            color: #fbc02d;
                                            font-weight: bold;
                                        "
                                    >
                                        ${'★'.repeat(
                                            parseInt(
                                                r.rating,
                                                10
                                            ) || 0
                                        )}
                                    </span>

                                </div>

                                <p
                                    style="
                                        font-size: 0.9rem;
                                        color: #444;
                                        margin-bottom: 0.2rem;
                                    "
                                >
                                    "${r.comment}"
                                </p>

                                <small
                                    style="
                                        color: #888;
                                        font-size: 0.75rem;
                                    "
                                >
                                    ${r.created_at}
                                </small>

                            </div>
                        `
                    ).join('');
            }
        }
    } catch (e) {
        console.error(
            "Error fetching reviews:",
            e
        );
    }

    const modal =
        document.getElementById(
            'reviews-modal'
        );

    if (modal) {
        modal.style.display = 'flex';
    }
}


function closeReviewsModal() {
    const modal =
        document.getElementById(
            'reviews-modal'
        );

    if (modal) {
        modal.style.display = 'none';
    }

    const form =
        document.getElementById(
            'review-form'
        );

    if (form) {
        form.reset();
    }

    selectedReviewProductId =
        null;
}


async function submitReviewForm(e) {
    e.preventDefault();

    if (!selectedReviewProductId) {
        return;
    }

    const userNameElement =
        document.getElementById(
            'rev-name'
        );

    const ratingElement =
        document.getElementById(
            'rev-rating'
        );

    const commentElement =
        document.getElementById(
            'rev-comment'
        );

    const userName =
        userNameElement
            ? userNameElement.value.trim()
            : '';

    const rating =
        ratingElement
            ? ratingElement.value
            : '';

    const comment =
        commentElement
            ? commentElement.value.trim()
            : '';

    if (!rating) {
        alert(
            'Please select a rating.'
        );
        return;
    }

    if (!comment) {
        alert(
            'Please enter your review.'
        );
        return;
    }

    try {
        const response =
            await fetch(
                `/api/reviews/${selectedReviewProductId}/submit/`,
                {
                    method: 'POST',

                    headers:
                        getJsonHeaders(),

                    body: JSON.stringify({
                        user_name:
                            userName,
                        rating:
                            rating,
                        comment:
                            comment
                    })
                }
            );

        const result =
            await response.json();

        if (response.status === 401) {
            alert(
                'Please log in before submitting a review.'
            );
            return;
        }

        if (result.success) {
            showToast(
                "⭐ Thank you for your review!"
            );

            const targetProd =
                products.find(
                    p =>
                        p.id ===
                        selectedReviewProductId
                );

            if (targetProd) {
                targetProd.avg_rating =
                    parseFloat(
                        result.avg_rating
                    );

                targetProd.total_reviews =
                    parseInt(
                        result.total_reviews,
                        10
                    );
            }

            renderProducts(
                currentCategory
            );

            await openReviewsModal(
                selectedReviewProductId
            );

            if (commentElement) {
                commentElement.value =
                    '';
            }
        } else {
            alert(
                'Review failed: ' +
                (
                    result.error ||
                    'Unable to submit review.'
                )
            );
        }
    } catch (err) {
        console.error(
            "Error submitting review:",
            err
        );

        alert(
            'Unable to submit review. Please try again.'
        );
    }
}


// ============================================================
// PAYMENT METHOD
// ============================================================

function handlePaymentMethodChange() {
    const paymentElement =
        document.getElementById(
            'cust-payment'
        );

    if (!paymentElement) return;

    const paymentMethod =
        paymentElement.value;

    const upiBox =
        document.getElementById(
            'upi-payment-box'
        );

    const cardBox =
        document.getElementById(
            'card-payment-box'
        );

    if (paymentMethod === 'UPI') {
        if (upiBox) {
            upiBox.style.display =
                'block';
        }

        if (cardBox) {
            cardBox.style.display =
                'none';
        }

        generateUpiQrCode();

    } else if (paymentMethod === 'Card') {

        if (upiBox) {
            upiBox.style.display =
                'none';
        }

        if (cardBox) {
            cardBox.style.display =
                'block';
        }

    } else {

        if (upiBox) {
            upiBox.style.display =
                'none';
        }

        if (cardBox) {
            cardBox.style.display =
                'none';
        }
    }
}


// ============================================================
// UPI QR CODE
// ============================================================

function generateUpiQrCode() {
    const totalPrice =
        cart.reduce(
            (sum, item) =>
                sum +
                (
                    item.price *
                    item.qty
                ),
            0
        );

    const storeUpiText =
        document.getElementById(
            'store-upi-id'
        );

    if (storeUpiText) {
        storeUpiText.textContent =
            STORE_UPI_ID;
    }

    const upiUri =
        `upi://pay?pa=${encodeURIComponent(
            STORE_UPI_ID
        )}&pn=${encodeURIComponent(
            STORE_NAME
        )}&am=${totalPrice.toFixed(
            2
        )}&cu=INR`;

    const qrImgUrl =
        `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(
            upiUri
        )}`;

    const qrElement =
        document.getElementById(
            'upi-qr-code'
        );

    if (qrElement) {
        qrElement.src =
            qrImgUrl;
    }
}


// ============================================================
// OPEN BILLING
// ============================================================

function openBilling() {
    if (cart.length === 0) {
        showToast(
            '🛒 Your cart is empty.'
        );
        return;
    }

    const summaryBox =
        document.getElementById(
            'billing-summary-items'
        );

    const billingTotal =
        document.getElementById(
            'billing-total'
        );

    const totalPrice =
        cart.reduce(
            (sum, item) =>
                sum +
                (
                    item.price *
                    item.qty
                ),
            0
        );

    if (summaryBox) {
        summaryBox.innerHTML =
            cart.map(
                i => `
                    <div
                        style="
                            display: flex;
                            justify-content: space-between;
                            margin-bottom: 0.4rem;
                            font-size: 0.95rem;
                        "
                    >
                        <span>
                            ${i.name}
                            [${i.unitLabel}]
                            (×${i.qty})
                        </span>

                        <strong>
                            ₹${(
                                i.price *
                                i.qty
                            ).toFixed(2)}
                        </strong>
                    </div>
                `
            ).join('');
    }

    if (billingTotal) {
        billingTotal.textContent =
            `₹${totalPrice.toFixed(2)}`;
    }

    toggleCart();

    handlePaymentMethodChange();

    const modal =
        document.getElementById(
            'billing-modal'
        );

    if (modal) {
        modal.style.display = 'flex';
    }
}


// ============================================================
// CLOSE BILLING
// ============================================================

function closeBilling() {
    const modal =
        document.getElementById(
            'billing-modal'
        );

    if (modal) {
        modal.style.display = 'none';
    }
}


// ============================================================
// CANCEL PAYMENT
// ============================================================

function cancelPayment() {
    if (
        confirm(
            "Are you sure you want to cancel payment? Items will stay in your cart."
        )
    ) {
        closeBilling();

        const form =
            document.getElementById(
                'billing-form'
            );

        if (form) {
            form.reset();
        }

        showToast(
            "⚠️ Payment canceled. Items are still in your cart."
        );
    }
}


// ============================================================
// PROCESS ORDER
// ============================================================
// IMPORTANT:
// We DO NOT send total_amount or order_items anymore.
//
// The backend now receives:
//
// {
//     name,
//     phone,
//     address,
//     payment_method,
//     transaction_id,
//     items: [
//         {
//             product_id: 1,
//             quantity: 2
//         }
//     ]
// }
//
// Django calculates the real total using database prices.
// ============================================================

async function processOrder(e) {
    e.preventDefault();

    if (cart.length === 0) {
        alert(
            'Your cart is empty.'
        );
        return;
    }

    const nameElement =
        document.getElementById(
            'cust-name'
        );

    const phoneElement =
        document.getElementById(
            'cust-phone'
        );

    const addressElement =
        document.getElementById(
            'cust-address'
        );

    const paymentElement =
        document.getElementById(
            'cust-payment'
        );

    const name =
        nameElement
            ? nameElement.value.trim()
            : '';

    const phone =
        phoneElement
            ? phoneElement.value.trim()
            : '';

    const address =
        addressElement
            ? addressElement.value.trim()
            : '';

    const paymentMethod =
        paymentElement
            ? paymentElement.value
            : '';

    if (!name) {
        alert(
            'Please enter your name.'
        );
        return;
    }

    if (!phone) {
        alert(
            'Please enter your phone number.'
        );
        return;
    }

    if (!address) {
        alert(
            'Please enter your delivery address.'
        );
        return;
    }

    if (!paymentMethod) {
        alert(
            'Please select a payment method.'
        );
        return;
    }

    // --------------------------------------------
    // Payment reference
    // --------------------------------------------

    let transactionId = '';

    if (paymentMethod === 'UPI') {
        const utrElement =
            document.getElementById(
                'upi-utr'
            );

        const utrInput =
            utrElement
                ? utrElement.value.trim()
                : '';

        if (!utrInput) {
            alert(
                'Please enter your UPI UTR / Transaction Reference number after paying.'
            );
            return;
        }

        transactionId =
            utrInput;

    } else if (paymentMethod === 'Card') {

        const cardElement =
            document.getElementById(
                'card-num'
            );

        const cardNum =
            cardElement
                ? cardElement.value.trim()
                : '';

        if (!cardNum) {
            alert(
                'Please enter your Card details.'
            );
            return;
        }

        transactionId =
            `CARD-REF-${Date.now()}`;

    } else {

        transactionId =
            'COD-ORDER';
    }


    // --------------------------------------------
    // IMPORTANT:
    // Send product IDs + quantities only.
    //
    // Backend will:
    // 1. Find products from database
    // 2. Read current database prices
    // 3. Validate stock
    // 4. Calculate total
    // 5. Reduce stock
    // 6. Create order
    // --------------------------------------------

    const orderItems =
        cart.map(item => ({
            product_id: item.id,
            quantity: item.qty
        }));


    // Safety check
    const invalidItem =
        orderItems.some(
            item =>
                !Number.isInteger(
                    Number(item.product_id)
                ) ||
                !Number.isInteger(
                    Number(item.quantity)
                ) ||
                Number(item.quantity) <= 0
        );

    if (invalidItem) {
        alert(
            'Invalid cart item detected. Please refresh the page and try again.'
        );
        return;
    }


    // --------------------------------------------
    // NEW SECURE PAYLOAD
    // --------------------------------------------

    const payload = {
        name: name,
        phone: phone,
        address: address,
        payment_method: paymentMethod,
        transaction_id: transactionId,

        // THIS IS THE IMPORTANT PART
        items: orderItems
    };


    // Disable submit button while processing
    const submitButton =
        e.submitter ||
        document.querySelector(
            '#billing-form button[type="submit"]'
        );

    const originalButtonText =
        submitButton
            ? submitButton.textContent
            : '';

    if (submitButton) {
        submitButton.disabled =
            true;

        submitButton.textContent =
            'Processing...';
    }


    try {
        const response =
            await fetch(
                '/api/place-order/',
                {
                    method: 'POST',

                    headers:
                        getJsonHeaders(),

                    body:
                        JSON.stringify(
                            payload
                        )
                }
            );


        // Try to parse JSON safely
        let result;

        try {
            result =
                await response.json();
        } catch (jsonError) {
            console.error(
                'Invalid server response:',
                jsonError
            );

            alert(
                'The server returned an invalid response. Please try again.'
            );

            return;
        }


        // --------------------------------------------
        // HTTP ERROR HANDLING
        // --------------------------------------------

        if (!response.ok) {

            if (response.status === 403) {
                alert(
                    'Security verification failed (CSRF). Please refresh the page and try again.'
                );
                return;
            }

            if (response.status === 400) {
                alert(
                    'Order failed: ' +
                    (
                        result.error ||
                        'Please check your order details.'
                    )
                );
                return;
            }

            if (response.status === 401) {
                alert(
                    'Please log in before placing an order.'
                );
                return;
            }

            alert(
                'Order failed: ' +
                (
                    result.error ||
                    'Server error. Please try again.'
                )
            );

            return;
        }


        // --------------------------------------------
        // SUCCESS
        // --------------------------------------------

        if (result.success) {

            // Prefer server-calculated total.
            const serverTotal =
                parseFloat(
                    result.total_amount
                );

            const displayTotal =
                Number.isFinite(
                    serverTotal
                )
                    ? serverTotal.toFixed(2)
                    : cart.reduce(
                        (sum, item) =>
                            sum +
                            (
                                item.price *
                                item.qty
                            ),
                        0
                    ).toFixed(2);


            alert(
                `🎉 PAYMENT SUCCESSFUL & ORDER PLACED!

Order ID: #${result.order_id}

Name: ${name}

Total Paid: ₹${displayTotal}

Payment Method: ${paymentMethod}

Reference / UTR: ${transactionId}

Delivery Address:
${address}

Thank you for buying organic products with us!`
            );


            // Clear cart only after successful order
            cart = [];

            updateCartUI();

            closeBilling();


            const billingForm =
                document.getElementById(
                    'billing-form'
                );

            if (billingForm) {
                billingForm.reset();
            }


            showToast(
                "✅ Payment successful! Order placed."
            );


            // Reset payment boxes
            const upiBox =
                document.getElementById(
                    'upi-payment-box'
                );

            const cardBox =
                document.getElementById(
                    'card-payment-box'
                );

            if (upiBox) {
                upiBox.style.display =
                    'none';
            }

            if (cardBox) {
                cardBox.style.display =
                    'none';
            }

        } else {

            alert(
                'Order submission failed: ' +
                (
                    result.error ||
                    'Unknown error.'
                )
            );
        }

    } catch (err) {

        console.error(
            'Error placing order:',
            err
        );

        alert(
            'Unable to connect to the server. Please check your internet connection and try again.'
        );

    } finally {

        // Re-enable submit button
        if (submitButton) {
            submitButton.disabled =
                false;

            submitButton.textContent =
                originalButtonText ||
                'Place Order';
        }
    }
}


// ============================================================
// INITIALIZE APPLICATION
// ============================================================

document.addEventListener(
    'DOMContentLoaded',
    () => {

        loadDatabaseProducts();

        renderProducts('all');

        updateCartUI();

        // Set default payment UI
        handlePaymentMethodChange();
    }
);