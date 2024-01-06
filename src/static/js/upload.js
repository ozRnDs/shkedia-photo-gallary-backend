

function resetModal(){
  const input = document.getElementById('fileInput');
  const btn_upload = document.getElementById('btn_upload')
  const error_DOM = document.getElementById("error_message")

  input.value = ""
  error_DOM.innerHTML = ""
  btn_upload.className = "fas fa-cloud-upload-alt"
}

  document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault();
  
    const error_DOM = document.getElementById("error_message")
    const formData = new FormData(this);
    const input = document.getElementById('fileInput');
    const file = input.files[0];
    const btn_upload = document.getElementById('btn_upload')
    const original_form_DOM = document.getElementById('uploadForm')


    error_DOM.innerHTML = ""
    btn_upload.className = "fas fa-spinner fa-spin"
    formData.append('created_on',file.lastModifiedDate.toISOString())
    formData.append('device_media_uri', input.value)

    const token = document.cookie.replace(/(?:(?:^|.*;\s*)forward\s*=\s*([^;]*).*$)|^.*$/, "$1");

    fetch(original_form_DOM.action, {
      method: 'POST',
      body: formData,
      headers:{
        'Authorization': `Bearer ${token}`,
      }
    })
    .then(response => {
      // Handle the response as needed
      if (response.ok) {
        const model = document.getElementById("staticBackdrop")
        $('#staticBackdrop').modal('hide');
        resetModal();
        $('#successModal').modal('show');
      } else {
        btn_upload.className = "fas fa-exclamation-triangle"
        
        error_DOM.innerHTML = response.statusText
      }
    })
    .catch(error => {
      btn_upload.className = "fas fa-exclamation-triangle"
    });
  });
