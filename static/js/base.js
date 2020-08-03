function myFunction() {
  document.getElementById("demo").innerHTML = "Hello World";
}

// function to hide/display reply box on bird_details
// receives comment id to know under which one to perform action
// it also re-attaches all the events back to forms submitions 
// as these get wipped off when ajax reloads the div the replies
// are inserted in

function myFunc(reply_id) {
  var x = document.getElementById(reply_id);
  if (x.style.display == "none") {
    x.style.display = "block";
    postReply();
  } else {
    x.style.display = "none";
  }
}

// rotate images
// function rotate_image() {
//   var img = document.getElementById("bird_image");
//   img.setAttribute("style", "transform:rotate(90deg)");
// }