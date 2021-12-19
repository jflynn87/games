let filler = /[\s\.\'\’]/g;
$( document ).ready(function() { 
    var first_time = true
    refresh(first_time)
    setInterval (refresh, 120000) 
})
function refresh(first_time) {
    $('#status').html('<p class=status> Updating Scores ... </p>')
    $.ajax({
        type: "GET",
        url: "/fb_app/update_scores/",
        data: {'week' : $('#week').text(), 
               'league': $('#league').text(),
               'season': $('#season').text()
               
            },
        dataType: 'json',
        success: function (json) {
            //console.log(json)
            if ($.parseJSON(json)['msg'] == 'week not started') {
                console.log('week not started')
                $('#loading').hide()
            }
            else {
                build_page(json, first_time)
                get_picks()
            }}
        })}


function get_picks() { 
        
        for (var i=16; i > 16 - parseInt($('#game_cnt').text()); i--) {
            fetch("/fb_app/get_pick/",
            {method: "POST",
            headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': $.cookie('csrftoken')
                    },
            body: JSON.stringify({
                            'week' : $('#week').text(), 
                            'league': $('#league').text(),
                            'season': $('#season').text(),
                            'game_cnt': $('#game_cnt').text(),
                            'pick_num': i
                                                })
            })
        .then((response) =>  response.json())
        .then((responseJSON) => {
            //console.log(responseJSON)
            d = $.parseJSON(responseJSON)
            $.each(d, function(num, data) {
             $.each(data, function(player, pick) {
                 p =player.replace(filler, '')
                if (pick['loser']) {
                $('#pick-' + p + num).text(pick['team']).removeClass('status').addClass('loser_abbr')
                //$('#pick-' + p + num).html('<img src=' + pick['logo'] + ' height=40 width=40 class=loser></img> <p>X</p>').addClass('loser').addClass('fs-2').removeClass('status')
                
                }
                else {
                //$('#pick-' + p + num).html('<img src=' + pick['logo'] + ' height=40 width=40">').addClass('tbl_center').removeClass('status')
                $('#pick-' + p + num).text(pick['team']).removeClass('status')
                }
             })
        })
        })
            }
}

function build_page(json,first_time) {

picks_data = $.parseJSON(json)['player-data']
games = $.parseJSON(json)['games']

//console.log(picks_data)
//console.log(picks_data)


if (first_time) {
$('#picks-sect').append('<table id=picks-tbl class="table table-striped table-sm tbl_center"> </table>')

//headers
$('#picks-tbl').append('<thead style="background-color:lightblue">' + '<th> Week' + $("#week").text() + '</th> </thead>')
$.each(picks_data, function(player, data) {$('#picks-tbl thead tr').append('<th id=name' + player +'>' + player + '</th>') }  )
  
$('#picks-tbl').append('<tbody> <tr id="rank"> <th>' + 'Rank' + '</th> </tr>' + 
                       '<tr id="score"> <th>' + 'Score' + '</th> </tr>' + 
                       '<tr id="proj"> <th>' + 'Projected' + '</th> </tr>' + 
                       '<tr id="proj_rank"> <th>' + 'Projected Rank' + '</th> </tr> </tbody> '  
)

$.each(picks_data, function(player, data) {
    p = player.replace(filler, '')
    $('#rank').append('<td id=rank-' + p + ' class=ranks>' + data['rank'] + '</td>')
    $('#score').append('<td id=score-' + p + '>' + data['score'] + '</td>')
    $('#proj').append('<td id=proj_score-' + p + '>' + data['proj_score'] + '</td>')
    $('#proj_rank').append('<td class=ranks id=proj_rank-' + p + '>'  + data['proj_rank'] + '</td>')
})    


for (var i= 16; i > 16 - parseInt($('#game_cnt').text()); i -- ) {
    $('#picks-tbl').append('<tr id=pick-' + i + '> <td>' + i + '</td> </tr>')
    $.each(picks_data, function(player, data) {
        if (first_time) {
        //$('#pick-' + i).append('<td id=pick-' + player.replace(filler, '') + i +' class=status> updating... </td>') 
        $('#pick-' + i).append('<td id=pick-' + player.replace(filler, '') + i +' ></td>') 
        }
        else {$('#pick-' + i).append('<td id=pick-' + player.replace(filler, '') + i +' class=status>' + $('#pick-' + player.replace(filler, '') + i).text()  +'</td>')
    }})}
   

$('#picks-tbl').append('<tr id="season_total"> <th>' + 'Season Total' + '</th> </tr>' + 
                       '<tr id="season_rank"> <th>' + 'Season Rank' + '</th> </tr>' )

$.each(picks_data, function(player, data) {
    p = player.replace(filler, '')
    $('#season_total').append('<td id=season_total' + p + '>' + data['season_total'] + '</td>' )
    $('#season_rank').append('<td id=season_rank' + p + ' class=ranks>' + data['season_rank'] + '</td>' )
})

$('#picks-tbl').append('<th> Week' + $("#week").text() + '</th> </thead>')
$.each(picks_data, function(player, data) {
    $('#picks-tbl').append('<th>' + player + '</th>') }  )
//}

$('#loading').hide()
$('#score-tbl').empty()
$('#sub-btn').remove()

$('#nfl-scores').append('<button id=sub-btn type="button" class="btn btn-primary">Project Scores</button>')

//headers
$('#score-tbl').append('<thead style="background-color:lightblue">' + '<th> Home </th>' +
                                                                      '<th> Score </th>' + 
                                                                      '<th> Visitor </th>' +
                                                                      '<th> Score </th>' +
                                                                      '<th> Qtr </th>' +
                                                                      '<th> Winner </th>' +
                                                            '</thead>')


$.each(games, function(id,game) {
    console.log(game)
    $('#score-tbl').append('<tr id=' + id + '>' + '<td id=home>' + game['home'] + '</td>' + '<td id=home_score>' + game['home_score'] + '</td>' +
                           '<td id=away>' + game['away'] + '</td>' + '<td id=away_score>' + game['away_score'] + '</td>' +
                                    '<td id=qtr>' + game['qtr'] + '</td>')

                                        if (game['qtr'].substring(0,5) == 'Final') {
                                            update_winner(id, game)
                                            //if (parseInt(game['home_score']) > parseInt(game['away_score'])) {$('#' + id).append('<td id=winner> <input name=winners type=hidden value=' + game['home'] + '> </input> ' + game['home'] + '</td>')}
                                            //else if (parseInt(game['home_score']) < parseInt(game['away_score'])) {$('#' + id).append('<td id=winner> <input name=winners type=hidden value=' + game['away'] + '> </input> ' + game['away'] + '</td>')}
                                            //else if (parseInt(game['home_score']) == parseInt(game['away_score'])) {$('#' + id).append('<td id=winner> <input name=tie type=hidden value=' + game['home'] + '> </input>' + '<input name=tie type=hidden value=' + game['away'] + '> </input>' + 'Tie, no winner' + '</td>')}
                                                                                    }
                                        else {$('#' + id).append('<td> <form method=POST> <select id=winner> <option value=1 selected=selected>' + game['home'] + '</option>' + 
                                                                 '<option value=2>' + game['away'] + '</option> </select>  <form> </td>' 
                                        )}

})

}

else {
$.each(picks_data, function(player, data) {
    p = player.replace(filler, '')
    $('#rank-' + p).text(data['rank'])
    $('#score-' + p).text(data['score'])
    $('#proj_score-' + p).text(data['proj_score'])
    $('#proj_rank-' +p).text(data['proj_rank'])
}) 


$.each(picks_data, function(player, data) {
    p = player.replace(filler, '')
    $('#season_total' + p).text(data['season_total'])
    $('#season_rank' + p).text(data['season_rank'])
})
$.each(games, function(id,game) {
    $('#' + id + ' #home').text(game['home'])
    $('#' + id + ' #home_score').html(game['home_score'])
    $('#' + id + ' #away').text(game['away'])
    $('#' + id + ' #away_score').text(game['away_score'])
    $('#' + id + ' #qtr').text(game['qtr'])

     if (game['qtr'].substring(0,5) == 'Final') {
        // $('#' + id + ' #winner').empty()
        // if (parseInt(game['home_score']) > parseInt(game['away_score'])) {$('#' + id + ' #winner').html('<input name=winners type=hidden value=' + game['home'] + '> </input> ' + game['home'])}
        // else if (parseInt(game['home_score']) < parseInt(game['away_score'])) {$('#' + id + ' #winner').html('<input name=winners type=hidden value=' + game['away'] + '> </input> ' + game['away'])}
        // else if (parseInt(game['home_score']) == parseInt(game['away_score'])) {$('#' + id).html('<td id=winner> <input name=tie type=hidden value=' + game['home'] + '> </input>' + '<input name=tie type=hidden value=' + game['away'] + '> </input>' + 'Tie, no winner' + '</td>')}
        update_winner(id, game)
                                                }



    //add else to swap choice based on current team in lead or fav?

})

}

function update_winner(id, game) {
    //$('#' + id + ' #winner').detach()
    winner = $('#' + id + ' #winner')
    winner.remove()
    if (game['qtr'].substring(0,5) == 'Final') {
        if (parseInt(game['home_score']) > parseInt(game['away_score'])) {$('#' + id).append('<td id=winner> <input name=winners type=hidden value=' + game['home'] + '> </input> ' + game['home'] + '</td>')}
        else if (parseInt(game['home_score']) < parseInt(game['away_score'])) {$('#' + id).append('<td id=winner> <input name=winners type=hidden value=' + game['away'] + '> </input> ' + game['away'] + '</td>')}
        else if (parseInt(game['home_score']) == parseInt(game['away_score'])) {$('#' + id).append('<td id=winner> <input name=tie type=hidden value=' + game['home'] + '> </input>' + '<input name=tie type=hidden value=' + game['away'] + '> </input>' + 'Tie, no winner' + '</td>')}
                                                }
    else {$('#' + id).append('<td> <form method=POST> <select id=winner> <option value=1 selected=selected>' + game['home'] + '</option>' + 
                            '<option value=2>' + game['away'] + '</option> </select>  <form> </td>' 
    )}

}


$('#status').html('<p class=none> Scores Updated:  ' + new Date($.now()) +  '</p>').removeAttr('hidden')
color()

}  //closes build_page

$(document).ready(function () {
function color() {
    $('td.ranks').each(function( index ) {

          if($(this).text()== '1'){
             $(this).css("background-color","#ff3333");
          }
          else if ($(this).text() == '2') {
            $(this).css("background-color","#ccebff");
          }
          else if ($(this).text() == '3') {
            $(this).css("background-color","#ffff99");
          }
          else {$(this).css("background-color","transparent")}
        
        });
  }
})


$(document).on('click', '#sub-btn', function() {
    console.log('clicked')
    $(window).scrollTop(0); 
    $('#proj').find('td').each(function() {$(this).html('...').addClass('status') })
    $('#proj').find('th').html('Proj Updating...')
    $('#proj_rank').find('td').each(function() {$(this).html('...').addClass('status') })
    $('#proj_rank').find('th').html('Proj Updating...')

    t = document.getElementById('score-tbl')
    var proj_winners = new Array()
    //start with 1 to skip header
    for (var i=1, row; row = t.rows[i]; i++) {
        if ($('#' + row.id +  ' #qtr').text().substring(0,5) ==  "Final") {
            proj_winners.push($('#' + row.id + ' #winner').text().replace(filler, ''))
            //proj_winners.push($('#' + row.id + ' #winner').text())
        }
        else {
           proj_winners.push($('#' + row.id + ' #winner').children("option").filter(":selected").text()) 
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
                update_proj($.parseJSON(json))
            }}
        })
    })


function update_proj(json) {
    $('#proj').find('th').html('Projected Score')
    $('#proj_rank').find('th').html('Projected Rank')    
    $.each(json, function(player, data) {

    $('#proj_score-' + player.replace(filler, '')).html(data['proj_score']).removeClass('status').show()
    $('#proj_rank-' + player.replace(filler, '')).text(data['proj_rank']).removeClass('status').show()
    color()
 

})
}
