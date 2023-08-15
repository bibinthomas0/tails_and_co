$(document).ready(function() {
    const form = document.querySelector("#apply-coupon-form");
    const codeInput = document.querySelector("#coupon-code-input");
    const couponMessage = document.querySelector("#coupon-message");
    const cartCoupon = document.querySelector("#cart-coupon");
    const cartTotal = document.querySelector("#cart-total");

    form.addEventListener("submit", function(event) {
        event.preventDefault();

        const couponCode = codeInput.value;

        fetch(form.action, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams(new FormData(form)),
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Coupon applied successfully') {
                couponMessage.textContent = data.message;
                couponMessage.style.color = 'green';
                const removeCouponLink = document.getElementById("remove-coupon-link");
                if (removeCouponLink) {
                    removeCouponLink.style.display = "inline";
                }

                cartCoupon.textContent = `-${data.coupon_discount}`;

                const originalCartTotal = parseFloat(cartTotal.textContent);
                const couponDiscount = parseFloat(data.coupon_discount);
                const newCartTotal = originalCartTotal - couponDiscount;

                cartTotal.textContent = newCartTotal.toFixed(2);

                setTimeout(function() {
                    couponMessage.style.opacity = 0;
                    couponMessage.style.transition = 'opacity 1s';
                }, 2000);
            } else {

                couponMessage.textContent = data.message;
                couponMessage.style.color = 'red';
            }
        })
        .catch(error => {
            console.error("Error:", error);
            couponMessage.textContent = 'Coupon application failed';
            couponMessage.style.color = 'red';
        });
    });

    // Function to get CSRF token
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
