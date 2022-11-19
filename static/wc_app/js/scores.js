$(document).ready(function () {
    fetch("/wc_app/wc_scores_api",         
    {method: "GET",
    })
.then((response) => response.json())
.then((responseJSON) => {
    data = responseJSON
    console.log('scores: ', data)
    if (data.error) {$('#scores_div').append("<h3>John is a crappy programmer, send him a line msg </h3>")
                     
                     $('#status').html('<p> Error Message: ' + data.error +'<p>')
                    }
    else {
    $('#scores_div').append('<table id=score_table class="table table-bordered table-sm"></table>')
    $('#score_table').append('<thead></thead>')
    $('#score_table').find('thead').append('<th class=border>Player</th>')
    $('#score_table').append('<tbody id=score_table_body></tbody>')
    $.each(Object.values(data)[0], function(group, d) {

        $('#score_table').find('thead').append('<th class=border>' + group + '</th>')
    })
    
    $.each(data, function(user, d) {
       
        $('#score_table_body').append('<tr id=' + user + '_row class=small><th class="border">' + user + '</th>' +
                                     '<th class=border>' + d.Score + '</th> ' + '<td>' + d.Bonus + '</th>' + '</tr>')
    
            $.each(d, function(group, pick) {
            //console.log(pick)
            if (group != 'Score' && group != 'Bonus') {

                $('#' + user + '_row').append('<td id=' + user + group.substr(-1)  + '_cell><table class=table-sm id=' + user + group.substr(-1)  + 
                                                    '_cell_tbl><tr class="small all_watermark"><td>Team</td><td>Pick</td><td>Score</td></tr></tabke>' + '</td>')
                $.each(pick, function(team, team_d) {
                                                
                                                if (team_d == 'perfect picks') {
                                                    
                                                    $('#' + user + group.substr(-1) + '_cell_tbl').css('background-color', 'lightgreen')}
                                                else {
                                                $('#' + user + group.substr(-1) + '_cell_tbl').append(
                                                '<tr><td><img src=' + team_d.flag +' style=height:20; width:20;>' + team  + '</td><td>' + team_d.pick_rank + '</td><td>' + team_d.points +  '</td></tr>' + 
                                                '</table>' ) }
                                             })
                }
            
            
            })
    
    }) //closes 1st each
    
    console.log('sorting')
    sort_table('score_table')
    
    $('#status').html('<p class=small>Scores Updated - Teams are listed in ranked order per group, green background for any perfect groups<p>')

  } //closes else
}) //closes then    

})


function sort_table(tableId) {
    var table, rows, swtiching, i, x, y, shouldSwitch;
    table = $('#' + tableId)
    //console.log(table)
    switching = true;
    
    while(switching) {
      switching = false;
      rows = table[0].rows;
      //console.log(rows.length)
      l = rows.length
      for (i=0; i < (l-1); i++) {
        //console.log('for loop', i, rows[i])
        shouldSwitch = false;
        
        x = rows[i].getElementsByTagName('th')[1].innerHTML;
        //console.log('x', x)
        y = rows[i + 1].getElementsByTagName('th')[1].innerHTML;
        //console.log('xy ' ,x, y)
        
        if (Number(x) < Number(y)) {
          //console.log(i, Number(x), Number(y))
          shouldSwitch = true;
          break;
        }
      }
        if (shouldSwitch) {
          rows[i].parentNode.insertBefore(rows[i+1], rows[i]);
          switching = true;
        }
      }
    }
