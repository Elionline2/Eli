
// Loader Javascript Coding Start

    window.addEventListener('load', function () {
        const loader = document.getElementById('loader');
        const content = document.getElementById('main-content');

        // Start a minimum timer of 7 seconds
        const MIN_LOAD_TIME = 500;
        const startTime = Date.now();

        function showContent() {
            const elapsed = Date.now() - startTime;
            const remainingTime = Math.max(MIN_LOAD_TIME - elapsed, 0);

            setTimeout(() => {
                loader.style.opacity = 0;
                loader.style.pointerEvents = 'none';
                content.style.opacity = 1;
                loader.style.display = 'none';
            }, remainingTime);
        }

        showContent();
    });


//Loader javascript Coding Stop

// Image Slider Configuration
const sliderConfig = {
    images: [
        "images/image1.jpg",
        "images/image2.jpg",
        "images/image3.jpg",
        "images/image4.jpg"
    ],
    slideInterval: 5000, // 5 seconds
    fadeDuration: 800   // 0.8 seconds
};


// DOM Elements
const sliderImage = document.getElementById("slider-image");
let currentIndex = 0;
let slideInterval;

// Preload images for smoother transitions
function preloadImages() {
    sliderConfig.images.forEach(src => {
        const img = new Image();
        img.src = src;
    });
}

/**
 * Shows an image with a smooth crossfade and scale animation
 * @param {number} index - The index of the image to show in sliderConfig.images
 */
function showImage(index) {
    // Handle wrap-around for continuous slider (both forward and backward)
    currentIndex = (index + sliderConfig.images.length) % sliderConfig.images.length;
    
    // Start transition out:
    // 1. Set transition properties (duration and easing)
    // 2. Fade out current image
    // 3. Slightly shrink image (to 95% size) for depth effect
    sliderImage.style.transition = `all ${sliderConfig.fadeDuration}ms ease`;
    sliderImage.style.opacity = 0;
    sliderImage.style.transform = 'scale(0.95)';
    
    /**
     * After half of the fade duration (when first image is mostly hidden):
     * 1. Swap the image source
     * 2. Fade new image in
     * 3. Return to normal scale (100%)
     * 
     * Using half duration creates overlap where both transitions occur,
     * making the crossfade smoother
     */
    setTimeout(() => {
        // Change image source to new image
        sliderImage.src = sliderConfig.images[currentIndex];
        
        // Animate new image in
        sliderImage.style.opacity = 1;
        sliderImage.style.transform = 'scale(1)';
        
    }, sliderConfig.fadeDuration / 2); // Halfway through total transition
}

// Navigation functions
function nextImage() {
    showImage(currentIndex + 1);
    resetSlideTimer();
}

function prevImage() {
    showImage(currentIndex - 1);
    resetSlideTimer();
}

// Auto-slide functionality
function startSlideTimer() {
    slideInterval = setInterval(nextImage, sliderConfig.slideInterval);
}

function resetSlideTimer() {
    clearInterval(slideInterval);
    startSlideTimer();
}

// Initialize slider
function initSlider() {
    preloadImages();
    sliderImage.style.transition = `opacity ${sliderConfig.fadeDuration / 1000}s ease-in-out`;
    startSlideTimer();
    
    // Set initial image
    sliderImage.src = sliderConfig.images[currentIndex];
    sliderImage.style.opacity = 1;
}

// Start the slider when DOM is loaded
document.addEventListener('DOMContentLoaded', initSlider);

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop - 80,
                behavior: 'smooth'
            });
        }
    });
});







// navbar responsive js coding

document.addEventListener("DOMContentLoaded", function () {
    const navbar = document.querySelector(".navbar");
    const navLinks = document.querySelector(".nav-links");
    
    // Create Menu Toggle Button
    const menuToggle = document.createElement("div");
    menuToggle.classList.add("menu-toggle");
    menuToggle.innerHTML = '<i class="fa fa-bars"></i>';
    navbar.appendChild(menuToggle);
  
    // Create Close Toggle Button
    const closeToggle = document.createElement("div");
    closeToggle.classList.add("close-toggle");
    closeToggle.innerHTML = '<i class="fa fa-times"></i>';
    navLinks.prepend(closeToggle);
  
    // Toggle Navigation
    menuToggle.addEventListener("click", function() {
      navLinks.classList.add("active");
      document.body.style.overflow = "hidden";
    });
  
    closeToggle.addEventListener("click", function() {
      navLinks.classList.remove("active");
      document.body.style.overflow = "auto";
    });
  
    // Close when clicking nav links
    const navItems = document.querySelectorAll(".nav-links a");
    navItems.forEach(item => {
      item.addEventListener("click", () => {
        navLinks.classList.remove("active");
        document.body.style.overflow = "auto";
      });
    });
  });




  









  document.addEventListener('DOMContentLoaded', function() {
    if (window.innerWidth <= 768) {
        const observerOptions = {
            threshold: 0.4,
            rootMargin: '0px 0px -100px 0px' // Slightly early trigger
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                const item = entry.target;
                const overlayItems = item.querySelectorAll('.overlay > *');
                
                if (entry.isIntersecting) {
                    // Add animate class
                    item.classList.add('animate');
                    
                    // Reset styles to ensure animation can replay
                    overlayItems.forEach(el => {
                        el.style.animation = 'none';
                        el.offsetHeight; // Trigger reflow
                        el.style.animation = '';
                    });
                } else {
                    // Remove animate class and reset state
                    item.classList.remove('animate');
                    overlayItems.forEach(el => {
                        el.style.transform = 'translateX(-100%)';
                        el.style.opacity = '0';
                        el.style.animation = 'none';
                    });
                }
            });
        }, observerOptions);

        // Observe all items
        const items = document.querySelectorAll('.showroom-item');
        items.forEach(item => {
            // Initialize hidden state
            item.querySelectorAll('.overlay > *').forEach(el => {
                el.style.transform = 'translateX(-100%)';
                el.style.opacity = '0';
            });
            observer.observe(item);
        });

        // Reset on window resize
        let resizeTimer;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function() {
                items.forEach(item => {
                    if (!item.classList.contains('animate')) {
                        item.querySelectorAll('.overlay > *').forEach(el => {
                            el.style.transform = 'translateX(-100%)';
                            el.style.opacity = '0';
                        });
                    }
                });
            }, 250);
        });
    }
});









document.addEventListener("DOMContentLoaded", () => {
    const showroomItems = document.querySelectorAll(".showroom-item");

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const overlay = entry.target.querySelector(".overlay");

            if (entry.isIntersecting) {
                // Trigger animation
                overlay.classList.add("animate");
            } else {
                // Reset animation so it can replay
                overlay.classList.remove("animate");
                void overlay.offsetWidth; // force reflow (ensures animation restarts)
            }
        });
    }, {
        threshold: 0.5
    });

    showroomItems.forEach(item => observer.observe(item));
});


