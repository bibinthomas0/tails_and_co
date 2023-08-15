
    var options = {
        
        "key": "rzp_test_VPg8DhRgbpgC0R", // Enter the Key ID generated from the Dashboard
        "amount": "{{payment.amount}}", // Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
        "currency": "INR",
        "name": "Tails and co", //your business name
        "description": "Purchases",
        "image": "https://i.ibb.co/xHXKQyt/Screenshot-2023-07-26-144602.png",
        "order_id": "{{payment.id}}", //This is a sample Order ID. Pass the `id` obtained in the response of Step 1
        "handler": function (response){

            window.location.href = `http://127.0.0.1:8000/createorder?razorpay_payment_id=${response.razorpay_payment_id}&razorpay_order_id=${response.razorpay_order_id}`;
      
             
          },
       
        "theme": {
            "color": "#3399cc"
        }
    };
    var rzp1 = new Razorpay(options);
    document.getElementById('rzp-button1').onclick = function(e){
        rzp1.open();
        e.preventDefault();
    }
    rzp1.on('payment.success', function(response) {
        console.log('Payment successful:', response);
        // Redirect to the success page
        window.location.href = 'createorder/';
    });
   
