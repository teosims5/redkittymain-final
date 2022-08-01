const preview = document.getElementById("file-preview");

function previewPhoto(event) {
  if (event.target.files.length > 0) {
    var src = URL.createObjectURL(event.target.files[0]);
    preview.src = src;
    preview.style.display = "block";
  }
}
