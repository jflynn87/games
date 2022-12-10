$(document).ready(function () {
    var start = new Date()
    fetch("/wc_app/wc_scores_api/" + $('#stage_key').text(),         
    {method: "GET",
    })
.then((response) => response.json())
.then((responseJSON) => {
    data = responseJSON
    console.log(data)
    if (data.error) {$('#scores_div').append("<h3>John is a crappy programmer, send him a line msg </h3>")
                     
                     $('#status').html('<p> Error Message: ' + data.error +'<p>')
                    }
    else {
    $('#scores_div').append('<table id=score_table class="table table-bordered table-sm"></table>')
    $('#score_table').append('<thead></thead>')
    $('#score_table').find('thead').append('<th class=border>Player</th><th class=border>Total Score</th><th class=border>Rd of 16</th>' + 
                                            '<th class=border>Quarters</th><th class=border>Semis</th><th class=border>Third</th><th class=border>Champion</th> ')
    $('#score_table').append('<tbody id=score_table_body></tbody>')
    }
    $.each(data, function(user, d) {
      if (user != 'results') {
        
        $('#score_table').append('<tr id=' + user + '_row class=small><td>' + user + '</td> <td><p style=font-weight:bold;>Total: ' + d.Score + '</p>' + 
                                                    '<p><a href=/wc_app/wc_ko_picks_view/' + user + '>KO:  ' + d.ko_stage_score  + '</a></p>' +
                                                    '<p>Group Stage: ' + d.group_stage_score  + '</p>' + 
                                                    '<p>Best possible score: ' + d.best_score  + '</p>' + 
                                                    '</td>' + 
                                                    '<td id=' + user + '_rof16_cell></td><td id=' + user + '_quarters_cell></td>' +
                                                    '<td id=' + user + '_semis_cell></td><td id=' + user + '_third_cell></td>' + 
                                                    '<td id=' + user + '_champ_cell></td>' +
                                                    '</tr>'
                                                    )
        addPicks(user, d.picks, data.results)
      }
    })
      
    sort_table('score_table')    
})


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
        
        x = rows[i].getElementsByTagName('td')[1].getElementsByTagName('p')[0].innerHTML.split(' ')[1];
        //console.log('x', x)
        y = rows[i + 1].getElementsByTagName('td')[1].getElementsByTagName('p')[0].innerHTML.split(' ')[1];
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

function addPicks(user, data, results) {
      $.each(data, function(i, info) {
            
            if (i + 1 < 9) {
                if (results['round-of-16'].losers.indexOf(info[0]) != -1) {
                
                  c = 'loser'
                }
                else if (results['round-of-16'].winners.indexOf(info[0]) != -1) {
                  c= 'winner'
                }
                else {c = ''}

                $('#' + user + '_rof16_cell').append('<p><img src=' + info[1] + ' style=height:20;width:20;><span class=' + c +  ' >' + info[0] + ' : ' + info[3] +' pts</span></p>')
              }
            else if (i + 1 < 13) {
              if (results['quarterfinals'].losers.indexOf(info[0]) != -1 || info[4] == 'out') {
                
                c = 'loser'
              }
              else if (results['quarterfinals'].winners.indexOf(info[0]) != -1) {
                c= 'winner'
              }
              else {c = ''}

                $('#' + user + '_quarters_cell').append('<p><img src=' + info[1] + ' style=height:20;width:20;><span class=' + c +  ' >' + info[0] + ' : ' + info[3] +' pts</span></p>')
            }
            else if (i + 1 ==13 || i+1 ==14) {
              if (results['semifinals'].losers.indexOf(info[0]) != -1 || info[4] == 'out') {
                
                c = 'loser'
              }
              else if (results['semifinals'].winners.indexOf(info[0]) != -1) {
                c= 'winner'
              }
              else {c = ''}

              $('#' + user + '_semis_cell').append('<p><img src=' + info[1] + ' style=height:20;width:20;><span class=' + c +  ' >' + info[0] + ' : ' + info[3] +' pts</span></p>')
            }
            else if (i + 1 == 16) {
              if (results['3rd-place'].losers.indexOf(info[0]) != -1 || info[4] == 'out') {
                
                c = 'loser'
              }
              else if (results['3rd-place'].winners.indexOf(info[0]) != -1) {
                c= 'winner'
              }
              else {c = ''}

                $('#' + user + '_third_cell').append('<p><img src=' + info[1] + ' style=height:20;width:20;><span class=' + c +  ' >' + info[0] + ' : ' + info[3] +' pts</span></p>')
            }
            else if (i + 1 == 15) {
              if (results['final'].losers.indexOf(info[0]) != -1 || info[4] == 'out') {
                
                c = 'loser'
              }
              else if (results['final'].winners.indexOf(info[0]) != -1) {
                c= 'winner'
              }
              else {c = ''}

                $('#' + user + '_champ_cell').append('<p><img src=' + info[1] + ' style=height:20;width:20;><span class=' + c +  ' >' + info[0] + ' : ' + info[3] +' pts</span></p>')
            }

            
        })
    }

