console.log('hello there mate')

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