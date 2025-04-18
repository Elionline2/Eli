let cropper = null;
const modal = document.getElementById('cropperModal');
const image = document.getElementById('cropperImage');
const fileInput = document.getElementById('photo');
const cropButton = document.getElementById('cropButton');
const closeButton = document.querySelector('.close-modal');
const croppedImageInput = document.getElementById('croppedImage');

// Initialize cropper when an image is selected
fileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            // Display the modal
            modal.style.display = 'block';
            
            // Set the image source
            image.src = e.target.result;
            
            // Initialize cropper
            if (cropper) {
                cropper.destroy();
            }
            
            cropper = new Cropper(image, {
                aspectRatio: 1,
                viewMode: 1,
                dragMode: 'move',
                autoCropArea: 1,
                restore: false,
                guides: true,
                center: true,
                highlight: false,
                cropBoxMovable: true,
                cropBoxResizable: true,
                toggleDragModeOnDblclick: false,
            });
        };
        reader.readAsDataURL(file);
    }
});

// Close modal when clicking the close button
closeButton.addEventListener('click', function() {
    modal.style.display = 'none';
    if (cropper) {
        cropper.destroy();
        cropper = null;
    }
    // Reset file input
    fileInput.value = '';
});

// Close modal when clicking outside
window.addEventListener('click', function(e) {
    if (e.target === modal) {
        modal.style.display = 'none';
        if (cropper) {
            cropper.destroy();
            cropper = null;
        }
        // Reset file input
        fileInput.value = '';
    }
});

// Handle crop button click
cropButton.addEventListener('click', function() {
    if (cropper) {
        // Get the cropped canvas
        const canvas = cropper.getCroppedCanvas({
            width: 300,
            height: 300
        });

        // Convert canvas to blob
        canvas.toBlob(function(blob) {
            // Create a new File object
            const croppedFile = new File([blob], 'cropped_profile.jpg', { type: 'image/jpeg' });
            
            // Create a new FileList containing the cropped file
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(croppedFile);
            
            // Update the file input with the cropped image
            fileInput.files = dataTransfer.files;
            
            // Update preview
            const previewImage = document.querySelector('.current-picture img');
            if (previewImage) {
                previewImage.src = canvas.toDataURL();
            }
            
            // Close the modal
            modal.style.display = 'none';
            cropper.destroy();
            cropper = null;
        }, 'image/jpeg');
    }
}); 