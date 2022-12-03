$(document).ready(function () {
    var start = new Date()
    fetch("/wc_app/wc_scores_api/" + $('#stage_key').text(),         
    {method: "GET",
    })
.then((response) => response.json())
.then((responseJSON) => {
    data = responseJSON
    
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
        
        $('#score_table').append('<tr id=' + user + '_row class=small><td>' + user + '</td> <td><p style=font-weight:bold;>Total: ' + d.Score + '</p>' + 
                                                    '<p>KO: ' + d.ko_stage_score  + '</p>' +
                                                    '<p>Group Stage: ' + d.group_stage_score  + '</p></td>' + 
                                                    '<td id=' + user + '_rof16_cell></td><td id=' + user + '_quarters_cell></td>' +
                                                    '<td id=' + user + '_semis_cell></td><td id=' + user + '_third_cell></td>' + 
                                                    '<td id=' + user + '_champ_cell></td>' +
                                                    '</tr>'
                                                    )
        addPicks(user, d.picks)

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

function addPicks(user, data) {
      $.each(data, function(i, info) {

            if (i + 1 < 9) {
                $('#' + user + '_rof16_cell').append('<p><img src=' + info[1] + ' style=height:20;width:20;>' + info[0] + ' : ' + info[3] +' pts</p>')
            }
            else if (i + 1 < 13) {
                $('#' + user + '_quarters_cell').append('<p><img src=' + info[1] + ' style=height:20;width:20;>' + info[0] + ' : ' + info[3] +' pts</p>')
            }
            else if (i + 1 < 15) {
                $('#' + user + '_semis_cell').append('<p><img src=' + info[1] + ' style=height:20;width:20;>' + info[0] + ' : ' + info[3] +' pts</p>')
            }
            else if (i + 1 == 16) {
                $('#' + user + '_third_cell').append('<p><img src=' + info[1] + ' style=height:20;width:20;>' + info[0] + ' : ' + info[3] +' pts</p>')
            }
            else if (i + 1 == 15) {
                $('#' + user + '_champ_cell').append('<p><img src=' + info[1] + ' style=height:20;width:20;>' + info[0] +  ' : ' + info[3] +' pts</p>')
            }

            
        })
    }

