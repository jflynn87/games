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
            $('#' + user + '_weeks_dtl_table').append('<tr><td>' + num +
            '<span id=' + user + '_expand_week_' + num +
            ' class="fa fa-plus-circle" style="color: lightblue;"> Click for details</span></td><td>' +
                                                       record.wins + '</td><td>' + record.loss + '</td></tr>') 
            $('#' + user + '_expand_week_' + num).on('click', weekGames(user + '_' + num))
                                                    })
            
        })
         
        $('#' + Object.keys(data)[0] + '_weeks_dtl_row').attr('hidden', false)
})
}

function weekGames(user) {
    console.log('week games ', user)
}