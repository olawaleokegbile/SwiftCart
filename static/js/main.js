window.addEventListener("load", function () {

    /* ========= THEME TOGGLE ========= */
    const toggleBtn = document.getElementById('themeToggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const body = document.body;
            const isDark = body.classList.contains('bg-gray-900');

            body.classList.toggle('bg-gray-900', !isDark);
            body.classList.toggle('text-gray-200', !isDark);
            body.classList.toggle('bg-gray-100',  isDark);
            body.classList.toggle('text-gray-800', isDark);

            localStorage.setItem('theme', !isDark ? 'dark' : 'light');
        });

        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('bg-gray-900','text-gray-200');
            document.body.classList.remove('bg-gray-100','text-gray-800');
        } else {
            document.body.classList.add('bg-gray-100','text-gray-800');
            document.body.classList.remove('bg-gray-900','text-gray-200');
        }
    }

    /* ========= ADD TO CART ========= */
    const cartCount = document.getElementById('cart-count');
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            fetch("/add_to_cart/", {
                method: "POST",
                headers: { "Content-Type":"application/json","X-CSRFToken":getCSRFToken() },
                body  : JSON.stringify({ product_id: btn.dataset.product })
            })
            .then(r => r.json())
            .then(data => {
                if (data.cart_count !== undefined && cartCount) {
                    cartCount.textContent = data.cart_count;
                    cartCount.classList.remove("hidden");
                }
                refreshCartPage();
            });
        });
    });

    /* ========= REMOVE FROM CART ========= */
    document.querySelectorAll('.remove-from-cart-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            fetch("/remove_from_cart/", {
                method: "POST",
                headers: { "Content-Type":"application/json","X-CSRFToken":getCSRFToken() },
                body  : JSON.stringify({ product_id: btn.dataset.product })
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
        });
    });

    /* ========= Refresh Cart Page (AJAX) ========= */
    function refreshCartPage(){
        // Only call if we are currently ON /cart/ page
        if(!window.location.pathname.startsWith('/cart')) return;

        fetch("/cart/", {
            headers: { "X-Requested-With": "XMLHttpRequest" }
        })
        .then(r => r.json())
        .then(data => {
            data.cart_items.forEach(item => {
                const qty  = document.getElementById(`qty-${item.product_id}`);
                const total = document.getElementById(`total-${item.product_id}`);
                if (qty)   qty.textContent   = item.quantity;
                if (total) total.textContent = item.total_price.toFixed(2);
            });

            const grand = document.getElementById("cart-grand-total");
            if(grand) grand.textContent = data.cart_total.toFixed(2);
        });
    }

    /* ========= CSRF Helper ========= */
    function getCSRFToken(){
        let val = null;
        document.cookie.split(";").forEach(c=>{
            c=c.trim();
            if(c.startsWith("csrftoken=")){
                val = c.substring("csrftoken=".length)
            }
        });
        return val;
    }

});