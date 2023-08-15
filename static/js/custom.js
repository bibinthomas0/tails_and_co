// /* Update quantity */
// function updateQuantity(quantityInput) {
//     var productRow = $(quantityInput).parent().parent();
//     var productId = productRow.data('product-id');
//     var price = parseFloat(productRow.children('.product-price').text());
//     var quantity = $(quantityInput).val();
//     var linePrice = price * quantity;
  
//     /* Update line price display and recalc cart totals */
//     productRow.children('.product-line-price').each(function () {
//       $(this).addClass('fade-out'); // Add the fade-out class
//       $(this).text(linePrice.toFixed(2));
//       recalculateCart();
//       $(this).removeClass('fade-out'); // Remove the fade-out class
  
//       // Send AJAX request to update cart item in the database
//       $.ajax({
//         type: 'POST',
//         url: '/update_cart_quantity/', // Update with your URL
//         data: {
//           product_id: productId,
//           quantity: quantity
//         },
//         success: function(response) {
//           // Handle success, if needed
//         },
//         error: function(error) {
//           // Handle error, if needed
//         }
//       });
//     });
//   }
  