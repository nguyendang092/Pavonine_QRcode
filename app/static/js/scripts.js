const slides = document.querySelector('.slides');
const images = document.querySelectorAll('.slides img');
let index = 0;

function nextSlide() {
    index = (index + 1) % images.length;
    slides.style.transform = `translateX(${-index * 100}vw)`;
}

setInterval(nextSlide, 15000);