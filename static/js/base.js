
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
	img.setAttribute('style','transform:rotate(90deg)');
};

///////////////////////// AJAX ////////////////////////////////

// ajax + jquery to control adding/removing seeds
$(document).ready(function(){
    $('#seed').click(function() {
        $.ajax(
            {
                url: "seed",
                type: "GET",
                data: {
                    pk : $('#seed').attr("data-pk")
                },
                success: success_func,
                error: error_func,
            })
        })
    function success_func(data){
        console.log(data)
        $('#seed_ico').text(' '+ data['count'])
    }
    
    function error_func(jqXHR, textStatus, errorThrown){
        console.log(jqXHR)
        console.log(textStatus)
        console.log(errorThrown)
    } 
})


    



// comment form
$('#comment_form').on('submit', function(event){
    event.preventDefault();
    console.log("form submitted!")
    var pk;
    pk = $(this).attr("data-pk");
    console.log(pk)
    create_comment()
});



function create_comment() {
    console.log('create comment is working')  // sanity check

    $.ajax(
        {
            url : "",
            type : "POST",
            data : { 
                comment_text : $('#comment-text').val(),
            },
        // hands a successful response
            success : function(json) {
                $('#comment-text').val('');
                console.log(json);
                console.log('success');
        },
            // handle a error response
            error : function(xhr,errmsg,err) {
                $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                    " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
                console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }

        
        }
    )
}