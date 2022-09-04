$('#game_table').ready(function() {
    console.log('table ready')
    fetch("/fb_app/get_records/",
    {method: "GET",
    })
    .then((response) =>  response.json())
    .then((responseJSON) => {
        data = $.parseJSON(responseJSON)
        console.log('data ', data)
        for (i=0; i < Object.keys(data).length; i++)
        {$('.' + Object.keys(data)[i]).text('(' + Object.values(data)[i].record + ')')}
        $('input').change(function() {teamSummary(data)})
        teamSummary(data)
        //selectByRecord(data)
    })

})

$(document).ready(function() {
    $('#pick_form').submit(function() {
        console.log('submitting')
        $('#favs_btn').prop('disabled', true).text("Submitting")
        $('#sub_button').prop('disabled', true).text("Submitting")
        $('#sub_button_div').append('Submitting Picks <span class=status>....</span>')
})
})

$(document).ready(function() {
    $('#favs').submit(function() {
        console.log('submitting')
      $('#favs_btn').prop('disabled', true).text("Submitting")
      $('#sub_button').prop('disabled', true).text("Submitting")
        $('#favs').append('Submitting Picks <span class=status>....</span>')
})
})



function teamSummary(data) {
    
    $('#team_summary_list li').remove()
    for (i=0; i < Object.keys(data).length; i++) {
        var wins = $('input[value=' + Object.values(data)[i].team_pk.toString() +  ']:checked').length 
        var loss = 17 - wins
        $('.' + Object.keys(data)[i]).text('last season record: ' + Object.values(data)[i].record + ', your 2022 picks: ' + wins + ',' + loss)
        //$('#team_summary_list').append('<li id=' + Object.values(data)[i].team_pk + '>' + Object.values(data)[i].nfl_abbr + 
        //                                '<span> :' + wins + ' / ' + loss + '</span>' +
        //                                '</li>')
        

    }
    $('#summary_status').hide()
}

function selectByRecord(data) {
   table = document.getElementById('game_table')
   rows = table.rows
   l = rows.length
   for (i=0; i < l; i++) {
    //console.log(i, rows[i], rows[i].classList)
    if (! rows[i].classList.contains('week_row')) {
        
        console.log(Object.values(data.team_pk)[rows[i].children[1]])
    }
   } 
}