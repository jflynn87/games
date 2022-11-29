$(document).ready(function(){
    $('#validate_picks').append('<h3>validate picks</h3>' )
    fetch("/fb_app/validate_picks_api/" + $('#week_pk').text(),
    {method: "GET",
    })
    .then(response =>  
        {if (response.ok) {
            return response.json()
        }
        else
           // console.log(response.json())
           
            {$('#validate_picks').text('Validate picks bad response: ' + response.status).css('color', 'red')}
        })
    .then((responseJSON) => {

        data = $.parseJSON(responseJSON)
        console.log(data)
        if (data.error) {
            $('#validate_picks').text('Validate Picks ERROR: ' + Object.values(data.error)).css('color', 'red')
        }
        else {
            $.each(data, function(user, res) {
                $('#validate_picks').append('<li>' + user +  Object.values(res) + '</li>')
            })
        }
    })
    
})
