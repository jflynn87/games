$(document).ready(function () {
    fetch("/wc_app/wc_scores_api",         
    {method: "GET",
    })
.then((response) => response.json())
.then((responseJSON) => {
    data = responseJSON
    console.log('scores: ', data)
    $('#scores_div').append('<table id=score_table class="table table-bordered table-sm"></table>')
    $('#score_table').append('<thead></thead>')
    $('#score_table').find('thead').append('<th class=border>Player</th>')
    $.each(Object.values(data)[0], function(group, d) {

        $('#score_table').find('thead').append('<th class=border>' + group + '</th>')
    })
    
    $.each(data, function(user, d) {
       
        $('#score_table').append('<tr id=' + user + '_row class=small><th class="border">' + user + '</th>' +
                                     '<th class=border>' + d.score + '</th> ' +  '</tr>')
    
            $.each(d, function(group, pick) {
            //console.log(pick)
            if (group != 'score') {

                $('#' + user + '_row').append('<td id=' + user + group.substr(-1)  + '_cell><table class=table-sm id=' + user + group.substr(-1)  + 
                                                    '_cell_tbl><tr class="small all_watermark"><td>Team</td><td>Pick</td><td>Score</td></tr></tabke>' + '</td>')
                $.each(pick, function(team, team_d) {
                                                
                                                if (team_d == 'perfect picks') {
                                                    console.group('xx', team, team_d)
                                                    $('#' + user + group.substr(-1) + '_cell_tbl').css('background-color', 'lightgreen')}
                                                else {
                                                $('#' + user + group.substr(-1) + '_cell_tbl').append(
                                                '<tr><td><img src=' + team_d.flag +' style=height:20; width:20;>' + team  + '</td><td>' + team_d.pick_rank + '</td><td>' + team_d.points +  '</td></tr>' + 
                                                '</table>' ) }
                                             })
                }
            
            
            })
    
    }) //closes 1st each
    
    $('#status').html('<p>Scores Updated - Teams are in ranked order per group<p>')

}) //closes then    

})