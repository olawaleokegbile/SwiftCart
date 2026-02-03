window.addEventListener("load", function () {

    /* ========= DRAWER ELEMENTS ========= */
    const cartDrawer = document.getElementById('cart-drawer');
    const cartDrawerBackdrop = document.getElementById('cart-drawer-backdrop');
    const cartDrawerContent = document.getElementById('cart-drawer-content');
    const closeDrawerBtn = document.getElementById('close-cart-drawer');
    const cartIcon = document.querySelector('a[href="/cart/"]');
    const cartCount = document.getElementById('cart-count');

    /* ========= OPEN/CLOSE DRAWER ========= */
    function openDrawer() {
        cartDrawer.classList.remove('invisible');
        setTimeout(() => {
            cartDrawerBackdrop.classList.add('opacity-100');
            cartDrawerContent.classList.remove('translate-x-full');
        }, 10);
        updateDrawerContent();
    }

    function closeDrawer() {
        cartDrawerBackdrop.classList.remove('opacity-100');
        cartDrawerContent.classList.add('translate-x-full');
        setTimeout(() => {
            cartDrawer.classList.add('invisible');
        }, 300);
    }

    if (cartIcon && cartDrawer) {
        cartIcon.addEventListener('click', (e) => {
            if (window.innerWidth > 768) { // Only show drawer on desktop for better feel
                e.preventDefault();
                openDrawer();
            }
        });
    }

    if (closeDrawerBtn) closeDrawerBtn.addEventListener('click', closeDrawer);
    if (cartDrawerBackdrop) cartDrawerBackdrop.addEventListener('click', closeDrawer);

    /* ========= UPDATE DRAWER CONTENT ========= */
    function updateDrawerContent() {
        const itemsContainer = document.getElementById('cart-drawer-items');
        const totalContainer = document.getElementById('cart-drawer-total');

        itemsContainer.innerHTML = `
            <div class="flex justify-center py-10">
                <svg class="animate-spin h-8 w-8 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
            </div>
        `;

        fetch("/cart/", {
            headers: { "X-Requested-With": "XMLHttpRequest" }
        })
            .then(r => r.json())
            .then(data => {
                let html = '';
                if (data.cart_items.length === 0) {
                    html = '<p class="text-center text-gray-500 py-10">Your cart is empty.</p>';
                } else {
                    data.cart_items.forEach(item => {
                        html += `
                            <div class="flex gap-4 items-center group">
                                <img src="${item.image_url}" class="h-16 w-16 object-cover rounded-lg">
                                <div class="flex-grow">
                                    <h4 class="font-bold text-gray-800 text-sm truncate w-40">${item.product_name}</h4>
                                    <p class="text-gray-500 text-xs">${item.quantity} x \u20A6${item.price.toFixed(2)}</p>
                                </div>
                                <div class="text-right">
                                    <p class="font-bold text-red-600">\u20A6${item.total_price.toFixed(2)}</p>
                                </div>
                            </div>
                        `;
                    });
                }
                itemsContainer.innerHTML = html;
                totalContainer.textContent = `\u20A6${data.cart_total.toFixed(2)}`;

                // Update header count
                const totalQty = data.cart_items.reduce((sum, item) => sum + item.quantity, 0);
                if (cartCount) {
                    cartCount.textContent = totalQty;
                    cartCount.classList.toggle('hidden', totalQty === 0);
                }
            });
    }

    /* ========= ADD TO CART ========= */
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            var productID = btn.dataset.product;
            var action = 'add';

            if (!isAuthenticated) {
                addCookieItem(productID, action);
            } else {
                updateUserOrder(productID, action);
            }
        });
    });

    document.querySelectorAll('.remove-from-cart-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            var productID = btn.dataset.product;
            var action = 'remove';

            if (!isAuthenticated) {
                addCookieItem(productID, action);
            } else {
                removeUserOrder(productID);
            }
        });
    });

    function addCookieItem(productId, action) {
        fetch("/update_session_cart/", {
            method: 'POST',
            headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken() },
            body: JSON.stringify({ product_id: productId, action: action })
        })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.error) });
                }
                return response.json();
            })
            .then(data => {
                if (window.location.pathname.startsWith('/cart')) {
                    location.reload();
                } else {
                    openDrawer();
                }
            })
            .catch(err => {
                alert(err.message);
            });
    }

    function updateUserOrder(productId, action) {
        fetch("/add_to_cart/", {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken() },
            body: JSON.stringify({ product_id: productId })
        })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.error) });
                }
                return response.json();
            })
            .then(data => {
                if (window.location.pathname.startsWith('/cart')) {
                    location.reload();
                } else {
                    openDrawer();
                }
            })
            .catch(err => {
                alert(err.message);
            });
    }

    function removeUserOrder(productId) {
        fetch("/remove_from_cart/", {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken() },
            body: JSON.stringify({ product_id: productId })
        })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.error) });
                }
                return response.json();
            })
            .then(data => {
                if (window.location.pathname.startsWith('/cart')) {
                    location.reload();
                } else {
                    openDrawer();
                }
            })
            .catch(err => {
                alert(err.message);
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

    /* ========= AUTO DISMISS (MESSAGES) ========= */
    const messageAlerts = document.querySelectorAll('.message-alert');
    messageAlerts.forEach(alert => {
        const dismiss = () => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 500);
        };
        const timer = setTimeout(dismiss, 5000);
        const closeBtn = alert.querySelector('.close-message');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                clearTimeout(timer);
                dismiss();
            });
        }
    });

});
