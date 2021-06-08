$(document).ready(function () {
    console.log('picks loaded')
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
    $('#make_picks').append('<form id=pick_form> </form>')
    sel_list = []
    
    $.each(field, function(i, f) {
        console.log(f.playerName)
        $('#make_picks form').append('<li>' + f.playerName + '</li>')
    })
    var options = []
    
    //var golfers = '<select>'
    })
})
