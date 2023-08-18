// Add passive event listeners to Cropper.js
document.addEventListener('DOMContentLoaded', function() {
  const cropperScript = document.querySelector('script[src*="cropper.min.js"]');
  if (cropperScript) {
    cropperScript.addEventListener('load', function() {
      const originalAddEventListener = HTMLElement.prototype.addEventListener;
      HTMLElement.prototype.addEventListener = function(type, listener, options) {
        const hasPassive = typeof options === 'boolean' ? options : options && options.passive;
        const passiveOptions = hasPassive ? options : { passive: true };
        return originalAddEventListener.call(this, type, listener, passiveOptions);
      };
    });
  }
});



// Select the elements
let result = document.querySelector('.result'),
    img_w = document.querySelector('.img-w'),
    save = document.querySelector('.save'),
    cropped = document.querySelector('.cropped'),
    upload = document.querySelector('#file-input'),
    cropper = '';

// on change show image with crop options
upload.addEventListener('change', e => {
  if (e.target.files.length) {
    // start file reader
    const reader = new FileReader();
    reader.onload = e => {
      if (e.target.result) {
        // create new image
        let img = document.createElement('img');
        img.id = 'image';
        img.src = e.target.result;
        // clean result before
        result.innerHTML = '';
        // append new image
        result.appendChild(img);
        // init cropper
        cropper = new Cropper(img);
        // show save btn
        save.classList.remove('hide');
      }
    };
    reader.readAsDataURL(e.target.files[0]);
  }
});

// save on click
save.addEventListener('click', e => {
  e.preventDefault();
  // get result to data uri
  let imgSrc = cropper.getCroppedCanvas({
    width: img_w.value // input value
  }).toDataURL();

  // Send cropped image data to Django view
  fetch('cropimage/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken') // Include the CSRF token
    },
    body: JSON.stringify({ image_data: imgSrc })
  })
  .then(response => response.json())
  .then(data => {
    // Handle response from Django view if needed
    console.log(data);
  })
  .catch(error => {
    console.error('Error:', error);
  });
});

// Function to get CSRF token from cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
