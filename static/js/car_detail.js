const mainGalleryImage = document.getElementById('mainGalleryImg');
const galleryThumbnails = document.querySelectorAll('.thumb-btn');

galleryThumbnails.forEach(button => {
  button.addEventListener('click', () => {
    const imageUrl = button.dataset.imgUrl;
    if (imageUrl && mainGalleryImage) {
      mainGalleryImage.parentElement.classList.add('image-loading');
      mainGalleryImage.src = imageUrl;
    }

    galleryThumbnails.forEach(thumbnail => thumbnail.classList.remove('is-active'));
    button.classList.add('is-active');
  });
});
