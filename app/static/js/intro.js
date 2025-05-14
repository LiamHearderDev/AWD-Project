
// This file contains JavaScript code used for the typing animation on the intro page
import "https://unpkg.com/typed.js@2.1.0/dist/typed.umd.js";


let currentSlide = 0; // Track the current slide index

/**
 * Function to handle the carousel slide change
 * @param {number} offset - The offset to change the slide by (1 for next, -1 for previous) 
 */
function changeSlide(offset) {
    console.log("Change slide called with offset:", offset);
    const carousel = document.getElementById("carousel-container");
    const totalSlides = carousel.children.length;

    // Update the current slide index
    currentSlide += offset;

    // Update the visibility of the buttons based on the current slide
    // Hide the right button if on the last slide, hide the left button if on the first slide
    //document.querySelector('.right-btn').style.display = currentSlide === totalSlides - 1 ? 'none' : 'block';
    //document.querySelector('.left-btn').style.display = currentSlide === 0 ? 'none' : 'block';

    // Ensure the slide index wraps around (circular carousel)
    if (currentSlide < 0) {
        currentSlide = totalSlides - 1;
    } else if (currentSlide >= totalSlides) {
        currentSlide = 0;
    }

    // Calculate the new translateX value
    const translateX = -(currentSlide * 100) / totalSlides;

    // Apply the transform to move the carousel
    carousel.style.transition = "transform 0.5s ease"; // Smooth transition
    carousel.style.transform = `translateX(${translateX}%)`;
}

window.onload = () => {

    // This handles how the typing animation works
    var typed = new Typed(".auto-type", {
        strings: ["Welcome to SpeedLogger"],
        typeSpeed: 66,

        onComplete: () => {
            document.querySelector('.typed-cursor').style.display = 'none';
        }
    });

    // This handles the carousel button click events
    document.querySelector('.right-btn').addEventListener('click',  () => {  changeSlide(1); });
    document.querySelector('.left-btn').addEventListener('click',   () => {  changeSlide(-1); });
}

// Reveal on scroll
window.addEventListener('scroll', () => {
    document.querySelectorAll('.reveal').forEach((reveal) => {
        const rect = reveal.getBoundingClientRect();
        const triggerBottom = window.innerHeight * 0.8;
        if (rect.top < triggerBottom) {
            reveal.classList.add('active');
        } 
    });
});