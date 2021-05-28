$(document).ready(function () {
    fetch("/golf_app/get_prior_result/",         
    {method: "POST",
    headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'X-CSRFToken': $.cookie('csrftoken')
            },
    body: JSON.stringify({'tournament_key': $('#tournament_key').text(),
                        'golfer_list': [],
                        'group': 'all'})
    })
    .then((response) => response.json())
    .then((responseJSON) => {
    field = responseJSON
    console.log(field)
    players = ['john', 'jcarl62', 'ryosuke']
    
    })
})
