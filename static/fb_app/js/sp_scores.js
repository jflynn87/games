function weekDtls(user) {
    console.log('clicked details')
    fetch("/fb_app/sp_weekly_scores/" + user,
    {method: "GET",
    })
    .then((response) =>  response.json())
    .then((responseJSON) => {
        data = $.parseJSON(responseJSON)
        console.log($('#' + user + '_weeks_dtl_table tr').length)
        
        if ($('#' + user + '_weeks_dtl_table tr').length > 0)
        {$('#' + user + '_weeks_dtl_table tr').remove()}
        
        $.each(data, function(user, week) {
            $('#' + user + '_weeks_dtl_table').append('<tr><th>Week</th><th>Win</th><th>Loss</th></tr> ')
            $.each(week, function(num, record) {
            $('#' + user + '_weeks_dtl_table').append('<tr id=week_row_' + user + '_week_' + num + '><td>' + num +
            '<span id=' + user + '_expand_week_' + num +
            ' class="fa fa-plus-circle" style="color: lightblue;"> Click for details</span></td><td>' +
                                                       record.wins + '</td><td>' + record.loss + '</td></tr>') 
                                                       $('#' + user + '_expand_week_' + num).click(function() { weekGames(user, num)})
                                                    })
                                                    
        })
         
        $('#' + Object.keys(data)[0] + '_weeks_dtl_row').attr('hidden', false)
})
}

function weekGames(user, week) {
    console.log('week games ', user, week)
    $('#' + 'dtl_' + user + '_' + week + '_row').remove()
    fetch("sp_week_dtl/" + user + '/' + week,
    {method: "GET",
    })
    .then((response) =>  response.json())
    .then((responseJSON) => {
        data = $.parseJSON(responseJSON)
        console.log(data)

        $('#week_row_' + user + '_week_' + week).after('<tr id=dtl_' + user + '_' + week + '_row><td><table id=dtl_' + user + 
                                                       '_' + week + ' class="table table-borderless">' + 
                                                       '<td></td><td></td><th>Home</th><th>Away</th><th>Pick</th></table></td></tr>' )
        $.each(Object.values(data), function(i, game) {
            $.each(game, function(eid, game_data) {
            $('#dtl_' + user + '_' + week).append('<tr class=' + eid + '><td></td><td></td><td>' + 
                                            game_data.home + ' (' + game_data.home_score + ')</td><td>' + game_data.away +
                                            ' (' + game_data.away_score +  ')</td><td>' + game_data.pick + '</td></tr>')
                if (! game_data.tie && game_data.pick == game_data.winner) {
                    $('.' + eid).css('background-color', 'green')

                }
        })
        } )
    })
}