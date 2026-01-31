window.addEventListener("load", function () {

    /* ========= THEME TOGGLE ========= */
    const toggleBtn = document.getElementById('themeToggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const body = document.body;
            const isDark = body.classList.contains('bg-gray-900');

            body.classList.toggle('bg-gray-900', !isDark);
            body.classList.toggle('text-gray-200', !isDark);
            body.classList.toggle('bg-gray-100', isDark);
            body.classList.toggle('text-gray-800', isDark);

            localStorage.setItem('theme', !isDark ? 'dark' : 'light');
        });

        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('bg-gray-900', 'text-gray-200');
            document.body.classList.remove('bg-gray-100', 'text-gray-800');
        } else {
            document.body.classList.add('bg-gray-100', 'text-gray-800');
            document.body.classList.remove('bg-gray-900', 'text-gray-200');
        }
    }

    /* ========= ADD TO CART ========= */
    const cartCount = document.getElementById('cart-count');
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            var productID = btn.dataset.product;
            var action = 'add';
            console.log('productID:', productID, 'Action:', action);
            console.log('User:', user);

            if (!isAuthenticated) {
                addCookieItem(productID, action);
            } else {
                updateUserOrder(productID, action);
            }
        });
    });

    /* ========= SESSION CART (GUEST) ========= */
    function addCookieItem(productId, action) {
        console.log('User is not authenticated');

        fetch(`/update_session_cart/?product_id=${productId}&action=${action}`, {
            method: 'GET',
        })
            .then(response => response.json())
            .then(data => {
                location.reload();
            });
    }

    /* ========= DB CART (LOGGED IN) ========= */
    function updateUserOrder(productId, action) {
        console.log('User is authenticated, sending data...');
        fetch("/add_to_cart/", {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken() },
            body: JSON.stringify({ product_id: productId })
        })
            .then(r => r.json())
            .then(data => {
                if (data.cart_count !== undefined && cartCount) {
                    cartCount.textContent = data.cart_count;
                    cartCount.classList.remove("hidden");
                }
                refreshCartPage();
            });
    }

    /* ========= REMOVE FROM CART ========= */
    document.querySelectorAll('.remove-from-cart-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            var productID = btn.dataset.product;
            var action = 'remove';

            if (!isAuthenticated) {
                addCookieItem(productID, action);
            } else {
                // Currently only remove_from_cart view exists for logged in, 
                // but we can reuse the logic or create a similar separate function.
                // The existing remove_from_cart view logic:
                fetch("/remove_from_cart/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken() },
                    body: JSON.stringify({ product_id: productID })
                })
                    .then(r => r.json())
                    .then(data => {
                        if (data.cart_count !== undefined && cartCount) {
                            cartCount.textContent = data.cart_count;
                            if (data.cart_count <= 0) {
                                cartCount.classList.add("hidden");
                            }
                        }
                        refreshCartPage();
                    });
            }
        });
    });

    /* ========= Refresh Cart Page (AJAX) ========= */
    function refreshCartPage() {
        // Only call if we are currently ON /cart/ page
        if (!window.location.pathname.startsWith('/cart')) return;

        // For guest, we reload because session cart is server side rendered mostly
        if (!isAuthenticated) {
            location.reload();
            return;
        }

        fetch("/cart/", {
            headers: { "X-Requested-With": "XMLHttpRequest" }
        })
            .then(r => r.json())
            .then(data => {
                data.cart_items.forEach(item => {
                    const qty = document.getElementById(`qty-${item.product_id}`);
                    const total = document.getElementById(`total-${item.product_id}`);
                    if (qty) qty.textContent = item.quantity;
                    if (total) total.textContent = item.total_price.toFixed(2);
                });

                const grand = document.getElementById("cart-grand-total");
                if (grand) grand.textContent = data.cart_total.toFixed(2);
            });
    }

    /* ========= CSRF Helper ========= */
    function getCSRFToken() {
        let val = null;
        document.cookie.split(";").forEach(c => {
            c = c.trim();
            if (c.startsWith("csrftoken=")) {
                val = c.substring("csrftoken=".length)
            }
        });
        return val;
    }

});