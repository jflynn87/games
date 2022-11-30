function createTeams(){
    
    fetch("/wc_app/wc_ko_create_teams_api",
    {method: "GET",
    })
    .then(response =>  
        {if (response.ok) {
            return response.json()
        }
        else
           // console.log(response.json())
           
            {$('#create_teams').text('error: ' + response.status).css('color', 'red')}
        })
    .then((responseJSON) => {

        data = $.parseJSON(responseJSON)
        console.log(data)
        if (data.error) {
            $('#create_teams').text('Error: ' + Object.values(data.error)).css('color', 'red')
        }
        else {
            $('#create_teams').text('Created').css('color', 'red')
        }
    })
    
}
