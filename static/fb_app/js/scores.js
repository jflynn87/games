$( document ).ready(function() { 
    refresh()
    setInterval (refresh, 600000) 
})
function refresh() {
    console.log('js linked') 
    
    $.ajax({
        type: "GET",
        url: "/fb_app/update_scores/",
        data: {'week' : $('#week').text(), 
               'league': $('#league').text(),
               'season': $('#season').text()
               
            },
        dataType: 'json',
        /*context: document.body, */
        success: function (json) {
            //console.log(json)
            if ($.parseJSON(json)['msg'] == 'week not started') {
                console.log('week not started')
                $('#loading').hide()
            }
            else {
                build_page(json)
            }}
        })}

function build_page(json) {
//console.log(json)
picks_data = $.parseJSON(json)['player-data']
games = $.parseJSON(json)['games']

console.log(picks_data)
//console.log(picks_data)


//add table
$('#picks-sect').empty()

$('#picks-sect').append('<table id=picks-tbl class="table table-striped"> <tbody>' + '</tbody> </table>')

//headers
$('#picks-tbl').append('<thead style="background-color:lightblue">' + '<th> Week' + $("#week").text() + '</th> </thead>')
$.each(picks_data, function(player, data) {$('#picks-tbl thead tr').append('<th>' + player + '</th>') }  )
  
$('#picks-tbl').append('<tr id="rank"> <th>' + 'Rank' + '</th> </tr>' + 
                       '<tr id="score"> <th>' + 'Score' + '</th> </tr>' + 
                       '<tr id="proj"> <th>' + 'Projected' + '</th> </tr>' + 
                       '<tr id="proj_rank"> <th>' + 'Projected Rank' + '</th> </tr>'  
)

$.each(picks_data, function(player, data) {
    //console.log(data['score'])
    $('#rank').append('<td class=ranks>' + data['rank'] + '</td>')
    $('#score').append('<td>' + data['score'] + '</td>')
    $('#proj').append('<td>' + data['proj_score'] + '</td>')
    $('#proj_rank').append('<td class=ranks>'  + data['proj_rank'] + '</td>')
})    

for (var i= 16; i > 16 - parseInt($('#game_cnt').text()); i -- ) {
    $('#picks-tbl').append('<tr id=pick-' + i + '> <td>' + i + '</td> </tr>')}
    
$.each(picks_data, function(player, data) {
    $.each(data['picks'], function(index) {
        $('#pick-' + index).append('<td class=' + data['picks'][index]['status'] + '>' + data['picks'][index]['team'] + '</td>')
    })
})

$('#picks-tbl').append('<tr id="season_total"> <th>' + 'Season Total' + '</th> </tr>' + 
                       '<tr id="season_rank"> <th>' + 'Season Rank' + '</th> </tr>' )

$.each(picks_data, function(player, data) {
    $('#season_total').append('<td>' + data['season_total'] + '</td>' )
    $('#season_rank').append('<td>' + data['season_rank'] + '</td>' )
})

$('#picks-tbl').append('<th> Week' + $("#week").text() + '</th> </thead>')
$.each(picks_data, function(player, data) {
    $('#picks-tbl').append('<th>' + player + '</th>') }  )


$('#loading').hide()
$('#score-tbl').empty()
$('#sub-btn').remove()
//build NFL game sect
//$('#nfl-scores').empty()

//$('#nfl-scores').append('<table id="score-tbl" class="table table-sm">' + '</table>')

$('#nfl-scores').append('<button disabled id=sub-btn type="button" class="btn btn-primary">Not Available</button>')

//headers
$('#score-tbl').append('<thead style="background-color:lightblue">' + '<th> Home </th>' +
                                                                      '<th> Score </th>' + 
                                                                      '<th> Visitor </th>' +
                                                                      '<th> Score </th>' +
                                                                      '<th> Qtr </th>' +
                                                                      '<th> Winner </th>' +
                                                            '</thead>')


//$('#nfl-row').append('<div class=column id=winners> <table class=table sm> <th> Winners </th> </table></div>')  
//$('#nfl-row').append('<div class=column id=winners></div>')
//$('#nfl-scores').append('<form method=POST> </form>')
//$('#nfl-scores form').append('<table id=score-tbl> </table>')


$.each(games, function(id,game) {
    //console.log(game)
    $('#score-tbl').append('<tr id=' + id + '>' + '<td>' + game['home'] + '</td>' + '<td>' + game['home_score'] + '</td>' +
                           '<td>' + game['away'] + '</td>' + '<td>' + game['away_score'] + '</td>' +
                                    '<td id=qtr' + id + '>' + game['qtr'] + '</td>')

                                        if (game['qtr'].substring(0,5) == 'FINAL') {
                                            if (parseInt(game['home_score']) > parseInt(game['away_score'])) {$('#' + id).append('<td id=winner' + id + '> <input name=winners type=hidden value=' + game['home'] + '> </input> ' + game['home'] + '</td>')}
                                            else if (parseInt(game['home_score']) < parseInt(game['away_score'])) {$('#' + id).append('<td id=winner' + id + '> <input name=winners type=hidden value=' + game['away'] + '> </input> ' + game['away'] + '</td>')}
                                            else if (parseInt(game['home_score']) == parseInt(game['away_score'])) {$('#' + id).append('<td id=winner' + id + '> <input name=tie type=hidden value=' + game['home'] + '> </input>' + '<input name=tie type=hidden value=' + game['away'] + '> </input>' + 'Tie, no winner' + '</td>')}
                                                                                    }
                                        else {$('#' + id).append('<td> <form method=POST> <select id=winner' + id + '> <option value=1 selected=selected>' + game['home'] + '</option>' + 
                                                                 '<option value=2>' + game['away'] + '</option> </select>  <form> </td>' 
                                        )}

})
color()

}  //closes build_page

function color() {
    $('td.ranks').each(function( index ) {
          if($( this ).text()== '1'){
             $(this).css("background-color","#ff3333");
          }
          else if ($(this).text() == '2') {
            $(this).css("background-color","#ccebff");

          }
          else if ($(this).text() == '3') {
            $(this).css("background-color","#ffff99");

          }
    });
  }



$(document).on('click', '#sub-btn', function() {
    console.log('clicked')
    token = $.cookie('csrftoken')
    t = document.getElementById('score-tbl')
    //console.log(t.rows)
    //console.log(t.rows.length)
    var proj_winners = new Array()
    //start with 1 to skip header
    for (var i=1, row; row = t.rows[i]; i++) {
        if ($('#qtr' + row.id).text() ==  "FINAL") {
            proj_winners.push($('#winner' + row.id)[0].innerText)
        }
        else {
           proj_winners.push($('#winner' + row.id).children("option").filter(":selected").text()) 
            }
        }
    console.log('proj',  proj_winners)
    $.ajax({
        type: "GET",
        url: "/fb_app/update_proj/",
        data: {'week' : $('#week').text(), 
               'league': $('#league').text(),
               'season': $('#season').text(),
               'winners': proj_winners,
              
            },
        dataType: 'json',
        /*context: document.body, */
        success: function (json) {
            console.log(json)
            if ($.parseJSON(json) == 'week not started') {
                console.log('week not started')
            }
            else {
                console.log('success')
                update_proj(json)
            }}
        })
    
    })

function update_proj(json) {
    console.log(json)
}



           
//             for (i = 1; i < table.rows.length; ++i) { 
//                 game = table.rows[i]
//                 $('#' + game.id + 'home_score').text(updates[game.id]['home_score'])
//                 $('#' + game.id + 'away_score').text(updates[game.id]['away_score'])
//                 $('#' + game.id + 'qtr').text(updates[game.id]['qtr'])
                
                
//                 if (updates[game.id]['final'] === true) {
//                    $('#winners > tbody').find('tr').each(function() {
//                     if (typeof($(this).find('input').val()) === 'undefined' && $(this).attr('id')==game.id + 'winners') {
//                         console.log('inside if', game.id)
//                         $(this).children().remove()
//                         $(this).append('<input type="hidden" value=' + updates[game.id]['winner'] + '"' + ' name="winners" />')
//                         $(this).append('<td>' + updates[game.id]["winner"] + '</td>')
//                    }
//                 })
//                 }
//             }

            
//             var player_list = player_index()
//             console.log(updates['losers'])
            
//             $('#scores').find('td').each (function(index, text) {
                
//                 if (index > 0) {
//                     $(this).text(updates[player_list[index-1]]['score'])
             
//             }}) 
                
//             $('#ranks').find('td').each (function(index, text) {
//                 if (index > 0) {
//                 $(this).text(updates[player_list[index-1]]['week_rank'])
//                 $(this).css('background-color', rank_color($(this)))
//             }}) 

//             $('#proj').find('td').each (function(index, text) {
//                 if (index > 0) {
//                 $(this).text(updates[player_list[index-1]]['week_proj'])

//             }});

             

//             $('#proj_rank').find('td').each (function(index, text) {
//                 if (index > 0) {
//                 $(this).text(updates[player_list[index-1]]['week_proj_rank'])
//                 $(this).css('background-color', rank_color($(this)))
//             }}) 

//             $('#season_total').find('td').each (function(index, text) {
//                 if (index > 0) {
//                 $(this).text(updates[player_list[index-1]]['season_total'])
             
//             }}) 

//             $('#season_rank').find('td').each (function(index, text) {
//                 if (index > 0) {
//                 $(this).text(updates[player_list[index-1]]['season_rank'])
             
//             }}) 
            
//             $('#picks-tbl tr').each(function(){
//                 $(this).find('td').each(function(){
//                   if ($.inArray($(this).text(), updates['losers']) !== -1) {
//                         $(this).css('color', 'red')
//                     }
//                 })
//             })
//         }
//     },
//         failure: function (json) {
//             console.log('fail')
//         }
//         })

    
//     // , 2000000 })
// }



// function player_index() {
//     var player_list = []
//     $('#players').find('th').each (function(index) {
//         if (index>0) {
//     player_list.push($(this).text())
//     }})
//     return player_list

  
// };                      

// function rank_color(field) {

//         /* figure out how to import this from ranks */
//         if(field.text()== '1'){
//             bc = "#ff3333";
//         }
//         else if (field.text() == '2') {
//             bc = "#ccebff";
//         }
//         else if (field.text() == '3') {
//             bc ="#ffff99";
//         }
//         else {
//             bc = 'white'}

//         return bc
// }

