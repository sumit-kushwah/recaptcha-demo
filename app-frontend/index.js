// used only in case of checkbox captcha
captchaToken = null;
captchaType = null;

// This function will be called by the reCAPTCHA checkbox
function setToken(token) {
  captchaType = 'checkbox';
  captchaToken = token;
}

var onloadCallback = function () {
  grecaptcha.render('load-captcha', {
    'sitekey': '6LeiS78pAAAAAOOTR7z8vSnnHInYkEqRKr5wYG1F',
    'callback': setToken
  });
};

document.getElementById('myForm').addEventListener('submit', function (event) {
  event.preventDefault();
  const formData = new FormData(event.target);
  formData.append('g-recaptcha-response', captchaToken);
  callUploadFileAPI(formData, captchaType);
});

function callUploadFileAPI(formData, captchaType) {
  formData.append('captcha_type', captchaType);
  fetch('http://localhost:3001/api/upload', {
    method: 'POST',
    body: formData
  })
    .then(response => response.json())
    .then(resJson => {
      data = resJson.data;
      document.getElementById('file_url').innerHTML = `<textarea>${JSON.stringify(resJson, null, 2)}</textarea>`;
    })
    .catch(error => {
      console.error('Error:', error);
    });
};

function cleanupFunction() {
  fetch('http://localhost:3001/api/cleanup', {
    method: 'DELETE',
  })
    .then(response => response.json())
    .then(resJson => {
      data = resJson.data;
      // keep response in textarea for now
      document.getElementById('file_url').innerHTML = `<textarea>${JSON.stringify(resJson, null, 2)}</textarea>`;
    })
    .catch(error => {
      console.error('Error:', error);
    });
}

function onSubmitInvisible() {
  var formData = new FormData(document.getElementById('myForm'));
  callUploadFileAPI(formData, 'invisible');
}

function onSubmitV3() {
  var formData = new FormData(document.getElementById('myForm'));
  callUploadFileAPI(formData, 'v3');
}