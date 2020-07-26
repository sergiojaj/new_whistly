
function myFunction() {
    document.getElementById("demo").innerHTML = "Hello World";
  }

// function to hide/display reply box on bird_details
// receives comment id to know under which one to perform action
function myFunc(reply_id) {
    var x = document.getElementById(reply_id);
    if (x.style.display == "none") {
        x.style.display = 'block';
    } else {
        x.style.display = "none";
    }
}

function myJS(item) {
    // for (x of item){
    //     console.log(x)
    // }
    console.log(item)
}

// rotate images
function rotate_image(){
	var img=document.getElementById('bird_image');
	img.setAttribute('style','transform:rotate(180deg)');
}