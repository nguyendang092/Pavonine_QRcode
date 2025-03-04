const slides = document.querySelector('.slides');
const images = document.querySelectorAll('.slides img');
let index = 0;

function nextSlide() {
    index = (index + 1) % images.length;
    slides.style.transform = `translateX(${-index * 100}vw)`;
}

setInterval(nextSlide, 30000);

window.addEventListener("load", () => {
    function clock() {
      const today = new Date();
  
      // get time components
      const hours = today.getHours();
      const minutes = today.getMinutes();
      const seconds = today.getSeconds();
  
      //add '0' to hour, minute & second when they are less 10
      const hour = hours < 10 ? "0" + hours : hours;
      const minute = minutes < 10 ? "0" + minutes : minutes;
      const second = seconds < 10 ? "0" + seconds : seconds;
  
      //make clock a 12-hour time clock
      const hourTime = hour > 12 ? hour - 12 : hour;
  
      // if (hour === 0) {
      //   hour = 12;
      // }
      //assigning 'am' or 'pm' to indicate time of the day
      const ampm = hour < 12 ? "AM" : "PM";
  
      // get date components
      const month = today.getMonth();
      const year = today.getFullYear();
      const day = today.getDate();
  
      //declaring a list of all months in  a year
      const monthList = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
      ];
  
      //get current date and time
      const date = monthList[month] + " " + day + ", " + year;
      const time = hourTime + ":" + minute + ":" + second + ampm;
  
      //combine current date and time
      const dateTime = date + " - " + time;
  
      //print current date and time to the DOM
      document.getElementById("date-time").innerHTML = dateTime;
      setTimeout(clock, 1000);
    }
    clock();   
});
document.addEventListener("DOMContentLoaded", function() {
  var message = "{{message | safe}}"
  if (message){
    message = document.getElementById("modalMessage").textContent;
    $("#messageModal").modal("show");
  }
})

document.addEventListener('scroll', function() {
  const navbar = document.getElementById('navbarheader');
  if(window.scrollY > 10){
    navbar.style.backgroundColor = rgba(0, 0, 0, 0.2);
  } else {
    navbar.style.backgroundColor = rgba(0, 0, 0, 0.5);
  }
})
function printQRcode(){
  const printWindow = window.open('', '', 'height=600,width=1000');
  const qrCodeContent = document.querySelector('.qr-code').outerHTML;
  printWindow.document.write('<html><head><title>Print QR Code</title>');
  printWindow.document.write('<style>body { font-family: Arial, sans-serif; } .qr-code { border: 1px solid #000; padding: 20px; text-align: center; }</style>');
  printWindow.document.write('</head><body>');
  printWindow.document.write(qrCodeContent);
  printWindow.document.write('</body></html>');
  printWindow.document.close();
  printWindow.focus();
  printWindow.print();
}