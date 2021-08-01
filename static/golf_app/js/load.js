let filler = /[\s\.\,\']/g;
let not_playing = ['CUT', 'WD', 'DQ']
$(document).ready(function() {
    //$('#det-list').attr('class', 'spinner')
    $('#totals-table').hide()
    start = new Date() 
    console.log('start time: ', start.toLocaleString())
    $('#local').text.toLocaleString()
    $('#status').append(start.toLocaleString())

    $.ajax({
      type: "GET",
      url: "/golf_app/get_db_scores/",
      data: {'tournament' : $('#tournament_key').text()},
      dataType: 'json',
      success: function (json) {
        console.log('DB loaded');
        console.log(json, typeof(json))
        if (!$.isEmptyObject(json)) {
          build_score_tbl(json)
         
        console.log('first load duration: ', start, new Date()) 
                                    }
        else {$('#det-list').append('<p>No Saved Scores, please wait</p>')}
                                  },
      failure: function(json) {
        console.log('fail');
        console.log(json);
        $('#det-list').attr('class', 'none')
      }
    })
})


$('#tournament_key').ready(function (){
$.ajax({
  type: "GET",
  url: "/golf_app/get_scores/",
  data: {'tournament' : $('#tournament_key').text()},
  dataType: 'json',
  success: function (json_update) {
    console.log('second load connected', typeof(json_update), $.isEmptyObject(json_update))
    if (!$.isEmptyObject(json_update)) {
    
    //build_score_tbl(json_update)
    update_score_tbl(json_update) }
    console.log('updated load duration: ', start, new Date()) 
    var finish = new Date().toLocaleString()
    $('#status').append(finish)
    $('#status').attr('class', 'updated-status').text('score updated: ' + finish)
    $('#time').hide()

                                        },
  failure: function(json_update) {
    console.log('fail');
    console.log(json_update);
    $('#det-list').attr('class', 'none')
  }
})

})

function build_score_tbl(data) {
  $('#det-list').empty()
  $('#det-list').append('<table class="table">' + '</table>')
  
  //console.log(info)
  //var picks_data = $.parseJSON((data['picks']))
  var total_data = $.parseJSON((data['totals']))
  var optimal_data = $.parseJSON((data['optimal']))
  var scores = $.parseJSON((data['scores']))
  var season_totals = $.parseJSON(data['season_totals'])
  var info = $.parseJSON(data['info'])
  var t_data = $.parseJSON(data['t_data'])

  console.log(scores)
  //console.log(t_data[0]['fields']['saved_round'])
  //console.log('T info: ', t_data[0])
//  console.log('totals', total_data)

  $('#det-list table').append('<thead style="background-color:lightblue">' + '<tr>' + '<th> Tournament Scores  </th>' + 
    '<th>' + '</th>' + '<th>' + '<a href="#"> <button> return to top</button> </a>' + '</th>' +  '<th>' + '</th>' + '<th>' + '</th>' + '<th>' + '</th>' +
    '<th>' + '</th>' + '<th>' + '</th>' + '<th>' + '</th>' + '<th>' + '</th>' + 
    '</thead>' +
    '<thead>' + 
    '<th>' + 'Position' + '</th>' +
    '<th>' + 'Change' + '</th>' +
    '<th>' + 'Golfer' + '</th>' +
    '<th>' + 'Total' + '</th>' +
    '<th>' + 'Thru' + '</th>' +
    '<th>' + 'Round' + '</th>' +
    '<th>' + 'R1' + '</th>' +
    '<th>' + 'R2' + '</th>' +
    '<th>' + 'R3' + '</th>' +
    '<th>' + 'R4' + '</th>' +
    '</thead>')
  $.each(scores, function(player, data) {
    if (player != 'info'){
    $('#det-list table').append('<tr    class="small">' +
    '<td>' + data['rank']+ '</td>' +
    '<td>' + format_move(data['change']) + data['change'].replace(filler, '') + '</td>' +
    '<td>' + player.bold() + '</td>' +
    '<td>' + data['total_score']+ '</td>' +
    '<td>' + data['thru']+ '</td>' +
    '<td>' + data['round_score']+ '</td>' +
    '<td>' + data['r1']+ '</td>' +
    '<td>' + data['r2']+ '</td>' +
    '<td>' + data['r3']+ '</td>' +
    '<td>' + data['r4']+ '</td>' +
    '</tr>')
  }}
  )


  $('#det-list').attr('class', 'none')

  $('#totals').empty()
  var col_num_picks = $('#multi-col').data('picks')
  $('#multi-col').attr('colspan', col_num_picks).attr('style', 'text-align:center;')

  $.each(total_data, function(p, total) {
    //$('#totals').append('<tr id=totals' + p + ' class=small> <span>' + '<td id=ts_' + p + ' class=total_score>'+  p  + ' (' + season_totals[p]['diff'] +')'  + '</p>' + '<p>' +  total['total_score'] + ' / ' + total['cuts']  + '</td>'  + '</tr>')
    $('#totals').append('<tr id=totals' + p + ' class=small> <span>' + '<td id=ts_' + p + ' style=font-weight:bold;>'+  p  + ' (' + season_totals[p]['diff'] + ' / ' + season_totals[p]['points_behind_second'] +')'  + '</p>' + '<p>' +  total['total_score'] + ' / ' + total['cuts']  + '</td>'  + '</tr>')

    var bonus = ''
     if (total['msg']) {$('#totals' + p).append('<td id=msg_' + p + '><p> h/c: ' + total['handicap'] + '</p>' + total["msg"] + '</td>' +
                                                '<td id=loading_' + p + '>Loading....</td>') }
    else {
      if (total['winner_bonus'] >0) {bonus = bonus + '<p> Winner: -' + total['winner_bonus'] +  '</p>'}
      if (total['best_in_group'] > 0) {bonus = bonus + '<p> Group: -' + total['best_in_group'] +  '</p>'}
      if (total['major_bonus'] > 0) {bonus = bonus + '<p> Major: -' + total['major_bonus'] +  '</p>'}
      if (total['cut_bonus'] > 0) {bonus = bonus + '<p> No Cut: -' + total['cut_bonus'] +  '</p>'}
      if (total['playoff_bonus'] > 0) {bonus = bonus + '<p> Playoff: -' + total['playoff_bonus'] +  '</p>'}
      //$('#totals' + p).append('<td id=msg_' + p + '><span class=bonus> <p> h/c: ' + total['handicap'] + '</p>' + bonus + '</span></td>' +
      $('#totals' + p).append('<td id=msg_' + p + '><span>  <p> h/c: ' + total['handicap'] + '</p>' + bonus + '</span></td>' +
                              '<td id=loading_' + p + '>Loading....</td> </span> </tr>')  
    }
      
 
 
  if ($('#pga_t_num').text() == '999') {
    $('#totals' + p).append('<td id=totals' + p +  'men_countries></td>')
    $('#totals' + p).append('<td id=totals' + p +  'women_countries></td>')
  }
})

  $('#totals').append('<tr id=optimalpicks class=small> <td> <p> Best Picks </p> </td> <td> </td> </tr>')
  if ($('#pga_t_num').text() == '999') {$('#optimalpicks').append('<td></td><td></td>')
                                        $('#cuts').append('<td></td><td></td>')} 
  $.each(optimal_data, function(group, data) {
    
    $('#optimalpicks').append('<td id=optimal_' + group + ' colspan=' + info[group] + ' style=text-align:center;> <p>' + Object.values(data["golfer"]) + '</p> <p>' + data['rank'] + '</td>')
  })

  $('#totals').append('<tr id=cuts class=small> <td> <p> Cuts </p> </td> <td> </td> </tr>')
  if ($('#pga_t_num').text() == '999') {$('#cuts').append('<td></td><td></td>')} 
  
  $.each(optimal_data, function(group, data) {
    $('#cuts').append('<td id=cuts_' + group + ' colspan=' + info[group] + ' style=text-align:center;> <p>' + data["cuts"] + ' / ' + data['total_golfers'] + '</td>')
  })

  var leaders = $.parseJSON((data['leaders']))
  
  if (t_data[0]['fields']['complete']) {
    $('#cut_line').text('Tournament Complete')  
                                        }
  else {
    //$('#cut_line').text('Round ' + t_data[0]['fields']['saved_round'] +  ', '  + data['cut_line']) 
    $('#cut_line').text(data['round_status'] +  ', '  + data['cut_line']) 
       }
  $('#leader').text(format_leaders(leaders))     

  $('#picks-tbl').show()
  $('#totals-table').show()

  get_picks(info, optimal_data)
  

}

function format_leaders(leaders) {
      
  var leader_display = ''    
  $.each(leaders['leaders'], function (i, l) {
        if (i == leaders['leaders'].length - 1)
        leader_display += l + ':  '
        else {leader_display += l + ', '}
      })
      leader_display += ' ' + leaders['score']
  return leader_display    

}



function format_move(score) {
  if (score == null) {
    return '  '} 
  else if (score.includes('down')) {
    return '<i class="fa fa-arrow-down text-danger"></i>'
           } 
    else if (score.includes('up')) {
    return '<i class="fa fa-arrow-up text-success"></i>'
     } 
    else {return "  "}
}


function get_picks(info, optimal_data) {

  //$.each(total_data, function(player, data) { 

  //fetch("/golf_app/get_picks/" + $('#tournament_key').text() + '/' + player,
  fetch("/golf_app/get_picks/" + $('#tournament_key').text() + '/' + 'all',
  
  {method: "GET",
  })
.then((response) => response.json())
.then((responseJSON) => {
  score_detail = responseJSON
  //$.each(total_data, function(player, data) { 
    if ($('#pga_t_num').text() == '999') {
      fetch("/golf_app/get_country_picks/" + $('#pga_t_num').text() + '/all' ,
      {method: "GET",
      })
      .then((response) => response.json())
      .then((responseJSON) => {
          country_detail = responseJSON
          //console.log('countries', country_detail)
          $.each(country_detail, function(i, data) {
           // console.log('country picks api call', data)
            if (data.gender == 'men') {
            $('#totals' + data.user.username + 'men_countries').append('<p><img src=' + data.get_flag + '</src></p>') }
            else {
            $('#totals' + data.user.username + 'women_countries').append('<p><img src=' + data.get_flag + '</src></p>') }

    })
  })
}

  $.each(score_detail, function (index, stats) {
    //console.log('stats', stats, stats.sod_position)
    let player = stats.user.username
    let filler = /[\s\.\,\']/g;
    $('#loading_' + player).remove()
      var pick = stats.pick.playerName.playerName.replace(filler, '')

      if (stats.toPar == 0) {
        toPar = "E"
      }
      else {toPar = stats.toPar} 
      
      $('#totals' + player).append('<td id=' + player + stats.pick.playerName.golfer.espn_number +  '>' + '<span class=watermark>' + 
       '<p>' + player.substring(0, 4)  + ' : ' + stats.pick.playerName.group.number +  '</p>'  +
       '</span>' + '<p> <img src=' + stats.pick.playerName.golfer.pic_link + ' style="max-height:85px;">' + stats.pick.playerName.playerName + '</img> </p>' + 
       '<p>' + '<img src=' + stats.pick.playerName.golfer.flag_link + ' style="max-height:25px;"></img>' +  stats.score +
        '<span > <a id=tt-' + pick + ' data-toggle="tooltip" > <i class="fa fa-info-circle" style="color:blue;"></i> </a> </span>' +
     '</p>' +  toPar + ' (' + stats.thru + ')' +  '   ' +
       format_move(stats.sod_position) +  stats.sod_position.replace(filler, '') +
        '</p>' +  '</td>')
     //console.log($('#tt-' + $(this)[0]['pick'].replace(/ +?/g, '').replace(/\./g,'') + '[data-toggle="tooltip"]'))
      $('#tt-' + pick + '[data-toggle="tooltip"]').tooltip({trigger:"hover",
                                            delay:{"show":400,"hide":800}, "title": 'gross score: ' + stats.gross_score
                                            }) 
     
      if (not_playing.indexOf(stats.today_score) != -1) {$('#' + player + stats.pick.playerName.golfer.espn_number).addClass('cut')}                                            
      //if ($(this)[0]['today_score'] in ['CUT', 'WD', 'DQ']) {$('#' + p + stats[index]['pga_num']).addClass('cut')}
    
    //use 0 of the index to strip the extra chars in multi pick groups.  Need to fix for tournaments with 10 groups.
    //console.log($(this)[0]['pick'], optimal_data[index], info[10])

    if (info[10] == 1) {if ($.inArray(stats.pick.playerName.golfer.espn_number, Object.keys(optimal_data[stats.pick.playerName.group.number]['golfer'])) !== -1) {$('#' + player + stats.pick.playerName.golfer.espn_number).addClass('best')} }
    else {
    if ($.inArray(stats.pick.playerName.golfer.espn_number, Object.keys(optimal_data[stats.pick.playerName.group.number]['golfer'])) !== -1) {$('#' + player + stats.pick.playerName.golfer.espn_number).addClass('best')} 
    }
  })}) 
//})

} 



function update_score_tbl(data) {
  $('#det-list').empty()
  $('#det-list').append('<table class="table">' + '</table>')
  
  var total_data = $.parseJSON((data['totals']))
  var optimal_data = $.parseJSON((data['optimal']))
  var scores = $.parseJSON((data['scores']))
  var season_totals = $.parseJSON(data['season_totals'])
  var info = $.parseJSON(data['info'])
  var t_data = $.parseJSON(data['t_data'])

  $('#det-list table').append('<thead style="background-color:lightblue">' + '<tr>' + '<th> Tournament Scores  </th>' + 
    '<th>' + '</th>' + '<th>' + '<a href="#"> <button> return to top</button> </a>' + '</th>' +  '<th>' + '</th>' + '<th>' + '</th>' + '<th>' + '</th>' +
    '<th>' + '</th>' + '<th>' + '</th>' + '<th>' + '</th>' + '<th>' + '</th>' + 
    '</thead>' +
    '<thead>' + 
    '<th>' + 'Position' + '</th>' +
    '<th>' + 'Change' + '</th>' +
    '<th>' + 'Golfer' + '</th>' +
    '<th>' + 'Total' + '</th>' +
    '<th>' + 'Thru' + '</th>' +
    '<th>' + 'Round' + '</th>' +
    '<th>' + 'R1' + '</th>' +
    '<th>' + 'R2' + '</th>' +
    '<th>' + 'R3' + '</th>' +
    '<th>' + 'R4' + '</th>' +
    '</thead>')
  $.each(scores, function(player, data) {
    if (player != 'info'){
    $('#det-list table').append('<tr    class="small">' +
    '<td>' + data['rank']+ '</td>' +
    '<td>' + format_move(data['change']) + data['change'].replace(filler, '') + '</td>' +
    '<td>' + player.bold() + '</td>' +
    '<td>' + data['total_score']+ '</td>' +
    '<td>' + data['thru']+ '</td>' +
    '<td>' + data['round_score']+ '</td>' +
    '<td>' + data['r1']+ '</td>' +
    '<td>' + data['r2']+ '</td>' +
    '<td>' + data['r3']+ '</td>' +
    '<td>' + data['r4']+ '</td>' +
    '</tr>')
  }}
  )


  $('#det-list').attr('class', 'none')

  //$('#totals').empty()
  var col_num_picks = $('#multi-col').data('picks')
  $('#multi-col').attr('colspan', col_num_picks).attr('style', 'text-align:center;')

  $.each(total_data, function(p, total) {
    $('#ts_' + p).html(p  + ' (' + season_totals[p]['diff'] + ' / ' + season_totals[p]['points_behind_second'] + ')'  + '</p>' + '<p>' +  total['total_score'] + ' / ' + total['cuts'])
    
    var bonus = ''
     if (total['msg']) {$('#msg_' + p).html('<p> h/c: ' + total['handicap'] + '</p> <td>' + total["msg"] + '</td>') }
    else {
      if (total['winner_bonus'] >0) {bonus = bonus + '<p> Winner: -' + total['winner_bonus'] +  '</p>'}
      if (total['best_in_group'] > 0) {bonus = bonus + '<p> Group: -' + total['best_in_group'] +  '</p>'}
      if (total['major_bonus'] > 0) {bonus = bonus + '<p> Major: -' + total['major_bonus'] +  '</p>'}
      if (total['cut_bonus'] > 0) {bonus = bonus + '<p> No Cut: -' + total['cut_bonus'] +  '</p>'}
      if (total['playoff_bonus'] > 0) {bonus = bonus + '<p> Playoff: -' + total['playoff_bonus'] +  '</p>'}
      //$('#msg_' + p).html('<span class=bonus> <p> h/c: ' + total['handicap'] + '</p>' + bonus + '</span>')  
      $('#msg_' + p).html('<span> <p> h/c: ' + total['handicap'] + '</p>' + bonus + '</span>')  
    }
  })

  //$('#totals #optimalpicks').html('<tr id=optimalpicks class=small> <td> <p> Best Picks </p> </td> <td> </td> </tr>')
  //if ($('#pga_t_num').text() == '999') {$('#optimalpicks').append('<td></td><td></td>')
  //                                      $('#cuts').append('<td></td><td></td>')}
  $.each(optimal_data, function(group, data) {
    $('#optimal_' + group).html('<p>' + Object.values(data["golfer"]) + '</p> <p>' + data['rank'] + '</p>')
  })

  //$('#totals').append('<tr id=cuts class=small> <td> <p> Cuts </p> </td> <td> </td> </tr>')
  $.each(optimal_data, function(group, data) {
    $('#cuts_' + group).html('<p>' + data["cuts"] + ' / ' + data['total_golfers'] + '</p>')
  })

  var leaders = $.parseJSON((data['leaders']))
  
  if (t_data[0]['fields']['complete']) {
    $('#cut_line').text('Tournament Complete')  
                                        }
  else {
    //$('#cut_line').text('Round ' + t_data[0]['fields']['saved_round'] +  ', '  + data['cut_line']) 
    $('#cut_line').text(data['round_status'] +  ', '  + data['cut_line']) 
       }

  $('#leader').text(format_leaders(leaders))        


  $('#picks-tbl').show()
  $('#totals-table').show()

  update_picks(info, optimal_data)


}

function update_picks(info, optimal_data) {

  
  //$.each(total_data, function(player, data) { 

  //fetch("/golf_app/get_picks/" + $('#tournament_key').text() + '/' + player,
  fetch("/golf_app/get_picks/" + $('#tournament_key').text() + '/' + 'all',
  {method: "GET",
  })
.then((response) => response.json())
.then((responseJSON) => {
  score_detail = responseJSON
  $.each(score_detail, function (index, stats) {
    let player = stats.user.username
    let filler = /[\s\.\,\']/g;
    //$('#loading_' + player).remove()
      var pick = stats.pick.playerName.playerName.replace(filler, '')

      if (stats.toPar == 0) {
        toPar = "E"
      }
      else {toPar = stats.toPar} 
    
      $('#' + player + stats.pick.playerName.golfer.espn_number).html('<span class=watermark>' + 
       '<p>' + player.substring(0, 4)  + ' : ' + stats.pick.playerName.group.number +
       '</p>'  + '</span>' + '<p>' +  '<img src=' + stats.pick.playerName.golfer.pic_link + ' style="max-height:85px;">' + stats.pick.playerName.playerName + '</img> </p>' + 
       '<p> <img src=' + stats.pick.playerName.golfer.flag_link + ' style="max-height:25px;"></img>' +  stats.score +
        '<span > <a id=tt-' + pick + ' data-toggle="tooltip" > <i class="fa fa-info-circle" style="color:blue;"></i> </a> </span>' +
     '</p>' +  toPar + ' (' + stats.thru + ')' +  '   ' +  format_move(stats.sod_position) +  stats.sod_position.replace(filler, '') + '</p>' +  '</td>')
     //console.log($('#tt-' + $(this)[0]['pick'].replace(/ +?/g, '').replace(/\./g,'') + '[data-toggle="tooltip"]'))
      $('#tt-' + pick + '[data-toggle="tooltip"]').tooltip({trigger:"hover",
                                            delay:{"show":400,"hide":800}, "title": 'gross score: ' + stats.gross_score
                                            }) 
     
      $('#' + player + stats.pick.playerName.golfer.espn_number).removeClass()
      if (not_playing.indexOf(stats.today_score) != -1) {$('#' + player + stats.pick.playerName.golfer.espn_number).addClass('cut')}                                            
      //if ($(this)[0]['today_score'] in ['CUT', 'WD', 'DQ']) {$('#' + p + stats[index]['pga_num']).addClass('cut')}
    
    //use 0 of the index to strip the extra chars in multi pick groups.  Need to fix for tournaments with 10 groups.
    //console.log($(this)[0]['pick'], optimal_data[index], info[10])
    
    if (info[10] == 1) {if ($.inArray(stats.pick.playerName.golfer.espn_number, Object.keys(optimal_data[stats.pick.playerName.group.number]['golfer'])) !== -1) {$('#' + player + stats.pick.playerName.golfer.espn_number).addClass('best')} }
    else {
    if ($.inArray(stats.pick.playerName.golfer.espn_number, Object.keys(optimal_data[stats.pick.playerName.group.number]['golfer'])) !== -1) {$('#' + player + stats.pick.playerName.golfer.espn_number).addClass('best')} 
    }
  })
//}) 
})

 sort_table(info)

} 

function sort_table(info) {
var table, rows, swtiching, i, x, y, shouldSwitch;
table = $('#totals-table')
switching = true;

while(switching) {
  switching = false;
  rows = table[0].rows;
  //console.log(rows.length)

  for (i=1; i < (rows.length - 3); i++) {
    //console.log('for loop', i)
    shouldSwitch = false;
    x = rows[i].getElementsByTagName('td')[0].getElementsByTagName('p')[1].innerHTML.split('/')[0].replace(/\s/g, '');
    y = rows[i + 1].getElementsByTagName('td')[0].getElementsByTagName('p')[1].innerHTML.split('/')[0].replace(/\s/g, '');
    //console.log(x, y)
    
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

function olympicCountryPicks(resolve) {
  return new Promise (function (resolve, reject) {
  fetch("/golf_app/get_country_picks/" + $('#pga_t_num').text() + '/all' ,
  {method: "GET",
  })
.then((response) => response.json())
.then((responseJSON) => {
  score_detail = $.parseJSON(responseJSON)
  //console.log('country picks api call', score_detail)
  $.each(score_detail, function(i, data) {
    //console.log(data.fields)
    $('#totals' + data.fields.user).append('<td id=men_countries>Mens Picks</td>')
    $('#totals' + data.fields.user).append('<td id=women_countries>Womens Picks</td>')
  })
})
resolve()})
}
