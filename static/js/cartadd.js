
	document.addEventListener('DOMContentLoaded', function() {
		var modal = document.getElementById("myModal");
		var addToCartButtons = document.querySelectorAll(".addToCartBtn"); // Select all buttons with class "addToCartBtn"
		var span = document.querySelector(".close");
	
		// Loop through each "Add to Cart" button
		addToCartButtons.forEach(function(btn) {
			btn.onclick = function() {
				// Get the productId from the data attribute of the clicked button
				var productId = btn.getAttribute('data-product-id');
				console.log(productId);
				// Make an AJAX request
				var xhr = new XMLHttpRequest();
				var url = "cartaddjs/" + productId + "/";
				xhr.open('GET', url, true);
                console.log("Constructed URL:", url);
				xhr.onreadystatechange = function() {
					if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
						modal.style.display = "block";
					}
				};
				xhr.send();
			};
		});
	
	
		window.onclick = function(event) {
			if (event.target == modal) {
				modal.style.display = "none";
			}
		};
	});

