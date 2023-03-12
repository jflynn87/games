$(document).ready(function () {
    var start = new Date()
    fetch("/wc_app/wc_scores_api/" + $('#stage_key').text(),         
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
    $('#score_table').find('thead').append('<th class=border>Player</th><th class=border>Total Score</th><th class=border>Group Bonus</th>')
    $('#score_table').append('<tbody id=score_table_body></tbody>')
    $.each(Object.values(data)[0], function(group, d) {

        if (group != 'Score' && group != 'Bonus') {

        $('#score_table').find('thead').append('<th class=border>' + group + '</th>')
        }
    })
    
    $.each(data, function(user, d) {
       
        $('#score_table_body').append('<tr id=' + user + '_row class=small><th class="border">' + user + '</th>' +
                                     '<th class=border>' + d.Score + '</th> ' + '<td>' + d.Bonus + '</th>' + '</tr>')
    
            $.each(d, function(group, pick) {
            //console.log(pick)
            if (group != 'Score' && group != 'Bonus') {

                $('#' + user + '_row').append('<td id=' + user + group.substr(-1)  + '_cell><table class=table-sm id=' + user + group.substr(-1)  + 
                                                    '_cell_tbl><tr class="small all_watermark"><td>Team</td><td>Pick</td><td>Score</td></tr></table>' + '</td>')
                var groupTbl = buildGroupTable(pick, user, group ,$('#' + user + group.substr(-1)  + '_cell_tbl'))
                groupTbl.then((response) => {sortGroup(user + group.substr(-1)  + '_cell_tbl')})
                
                //                            $.each(pick, function(team, team_d) {
                                                
                //                                 if (team_d == 'perfect picks') {
                                                    
                //                                     $('#' + user + group.substr(-1) + '_cell_tbl').css('background-color', 'lightgreen')}
                //                                 else {
                //                                 $('#' + user + group.substr(-1) + '_cell_tbl').append(
                //                                 '<tr><td><img src=' + team_d.flag +' style=height:20; width:20;>' + team  + '</td><td>' + team_d.pick_rank + '</td><td>' + team_d.points +  '</td></tr>' + 
                //                                 '</table>' ) }
                //                              })
                }
            
            
            })
    
    }) //closes 1st each
    
    //console.log('sorting')
    sort_table('score_table')
    
    $('#status').html('<p class=small>Scores Updated - Teams are listed in ranked order per group, green background for any perfect groups<p>')
    $('#table_div').append('<h5 id=stand_tbl class="fa fa-plus-circle" style="color: lightblue;">Group Table - click to show</h5><div id=stand_tbl_cards class=row><br></div>')
    .on('click', function() {buildStandingTable(data)})

    
    console.log('Duration: ', new Date() - start)

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


function buildGroupTable(pick, user, group, tableId) {
  return new Promise(function (resolve,reject) {
  $.each(pick, function(team, team_d) {
                                                
    if (team_d == 'perfect picks') {
        
        $('#' + user + group.substr(-1) + '_cell_tbl').css('background-color', 'lightgreen')}
    else {
    $('#' + user + group.substr(-1) + '_cell_tbl').append(
    '<tr><td hidden>' + team_d.rank + '</td><td><img src=' + team_d.flag +' style=height:20; width:20;>' + team  + '</td><td>' +
      team_d.pick_rank + '</td><td>' + team_d.points +  '</td>' +
      //'<td>' + team_d.team_rank + '</td>' +
     '</tr>' + 
    '</table>' ) }
 })
 resolve()
})

}

function sortGroup(tableId) {
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
      
      x = rows[i].getElementsByTagName('td')[0].innerHTML;
      //console.log('x', x)
      y = rows[i + 1].getElementsByTagName('td')[0].innerHTML;
      console.log('xy ' ,x, y)
      
      if (Number(x) > Number(y)) {
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

function buildStandingTable(data) {
  toggleTableDisplay()
  if ($('.card').length != 8) {
    $('#table_div').append('<p id=standing_tbl_status>Loading <span class=status>...</span></p>')
    fetch("/wc_app/wc_group_stage_table_api",         
    {method: "GET",
    })
    .then((response) => response.json())
    .then((responseJSON) => {
      data = responseJSON

    
    standings = data
    console.log(data)
      if (data.type == 'WBC') {
        console.log('WBC')
        $.each(standings, function(group, teams) {
          if (group != 'headers' && group != 'type') {
          $('#stand_tbl_cards').append('<div class=card>' +
                              '<table id=stand_tbl_' + group[5] +'><thead><tr style=text-align:center;background-color:lightblue;><th colspan=9>' + group +  '</th></tr></thead>' + 
                              '<tr class=small><th>Team</th><th>W</th><th>L</th><th>PCT</th><th>Scored</th><th>Against</th></tr>' + 
                              '</table>' +
                            '</div>')
                            $.each(teams, function(label, stat) {
                              $('#stand_tbl_' + group[5]).append('<tr><td>' + stat.abbr + '</td><td>' + stat.wins + '</td>' +
                                                                '<td>' + stat.loss + '</td>' +
                                                                '<td>' + stat.pct + '</td>' +
                                                                '<td>' + stat.scored + '</td>' + 
                                                                '<td>' + stat.against + '</td></tr>')})
                            }
        
      })
    
      }
      else {
    $.each(standings, function(group, teams) {
      if (group != 'Score' && group != 'Bonus') {
      $('#stand_tbl_cards').append('<div class=card>' +
                          '<table id=stand_tbl_' + group[6] +'><thead><tr style=text-align:center;background-color:lightblue;><th colspan=9>' + group +  '</th></tr></thead>' + 
                          '<tr class=small><th>Team</th><th>GP</th><th>W</th><th>D</th><th>L</th><th>F</th><th>A</th><th>GD</th><th>P</th>' + 
                          '</table>' +
                        '</div>')
                        $.each(teams, function(label, stat) {
                          $('#stand_tbl_' + group[6]).append('<tr><td>' + label + '</td><td>' + stat.played + '</td>' +
                                                            '<td>' + stat.wins + '</td><td>' + stat.draw + '</td>' +
                                                            '<td>' + stat.loss + '</td><td>' + stat.for + '</td>' +
                                                            '<td>' + stat.against + '</td><td>' + stat.goal_diff + '</td>' + 
                                                            '<td>' + stat.points + '</tr>')})
                        }
    
  })
  }
  
  $('#table_div').append('<br>')
  $('#standing_tbl_status').remove()
  })
  }
}

function toggleTableDisplay() {
  if ($('#stand_tbl').text() == 'Group Table - click to show') {
    $('#stand_tbl_cards').show()
    $('#stand_tbl').text('Group Table - click to hide')
  }
  else {
    $('#stand_tbl_cards').hide()
    $('#stand_tbl').text('Group Table - click to show')
  }
}

