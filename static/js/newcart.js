$(document).ready(function() {
  // Your JavaScript code here


jQuery(document).ready(function() {
    var taxRate = 0.05;
    var shippingRate = 15.00;
    var fadeTime = 300;
    // var linePrice = price * quantity;
    /* Assign actions */
    $('.product-quantity input').change(function() {
      updateQuantity(this);
    });
  
    $('.product-removal button').click(function() {
      removeItem(this);
    });
  
    /* Recalculate cart */
    function recalculateCart() {
      var subtotal = 0;
  
      /* Sum up row totals */
      $('.product').each(function () {
        subtotal += parseFloat($(this).children('.product-line-price').text());
      });
  
     
      var tax = subtotal * taxRate;
      var shipping = (subtotal > 0 ? shippingRate : 0);
      var total = subtotal + shipping;
  
      /* Update totals display */
      $('.totals-value').addClass('fade-out'); // Add the fade-out class
      $('#cart-subtotal').html(subtotal.toFixed(2));
      $('#cart-tax').html(tax.toFixed(2));
      $('#cart-shipping').html(shipping.toFixed(2));
      $('#cart-total').html(total.toFixed(2));
      if (total == 0) {
        $('.checkout').fadeOut(fadeTime);
      } else {
        $('.checkout').fadeIn(fadeTime);
      }
      $('.totals-value').removeClass('fade-out'); 
    }
  
    /* Update quantity */
    function updateQuantity(quantityInput) {
      var productRow = $(quantityInput).parent().parent();
      var price = parseFloat(productRow.children('.product-price').text());
      var quantity = $(quantityInput).val();
      var productId = productRow.find('.product-quantity input').data('product-id');
      var linePrice = price * quantity;
      var csrfToken= $('input[name=csrfmiddlewaretoken]').val(); 
      console.log(productId);
      /* Update line price display and recalc cart totals */
      productRow.children('.product-line-price').each(function () {
        $(this).addClass('fade-out'); // Add the fade-out class
        $(this).text(linePrice.toFixed(2));
        recalculateCart();
        $(this).removeClass('fade-out'); // Remove the fade-out class
      });
     

      $.ajax(
        {
        type: 'POST',
        url: 'update_cart_quantity/', // Update with your URL
        
        data: {
          product_id: productId,
          quantity: quantity,
          
          csrfmiddlewaretoken: csrfToken,
        },
        success: function(response) {
          if (response.success) {
              var message = response.message;
           
              var messageContainer = $('#message-container');
              messageContainer.text(message).fadeIn().delay(3000).fadeOut(); 
             
          } else {
              console.error('Update failed:', response.message);
          }
      },
      });


    }

  
    /* Remove item from cart */
    function removeItem(removeButton) {
      var productRow = $(removeButton).parent().parent();
      productRow.slideUp(fadeTime, function() {
        productRow.remove();
        recalculateCart();
      });
    }
  });
});
