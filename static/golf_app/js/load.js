$(document).ready(function() {
    $('#det-list').attr('class', 'spinner')
    $('#totals-table').hide()
    start = new Date() 
    console.log(start.toLocaleString())
    $('#local').text.toLocaleString()
    $('#status').append(start.toLocaleString())

    $.ajax({
      type: "GET",
      url: "/golf_app/get_db_scores/",
      data: {'tournament' : $('#tournament_key').text()},
      dataType: 'json',
      success: function (json) {
        console.log('DB load success');
        console.log(json, typeof(json))
        if (!$.isEmptyObject(json)) {
          build_score_tbl(json)
         
        console.log('first load duration: ', start, new Date()) 
      }},
      failure: function(json) {
        console.log('fail');
        console.log(json);
      }
    })
})

$(document).ready(function() {
  //$('#det-list').attr('class', 'spinner')
  //$('#totals-table').hide()
  start = new Date() 
  //console.log(start.toLocaleString())
  //$('#local').text.toLocaleString()
  //$('#status').append(start.toLocaleString())

  $.ajax({
    type: "GET",
    url: "/golf_app/cbs_scores/",
    data: {'tournament' : $('#tournament_key').text()},
    dataType: 'json',
    success: function (json) {
      console.log('cbs load success');
      console.log('cbs len', json, $.isEmptyObject(json))
      if (!$.isEmptyObject(json)) {
      build_score_tbl(json)
      $('#status').text('scores from CBS, getting PGA scores')
      console.log('cbs load duration: ', start, new Date()) 
    }},
    failure: function(json) {
      console.log('fail');
      console.log(json);
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
    
    build_score_tbl(json_update) }
    console.log('updated load duration: ', start, new Date()) 
    var finish = new Date().toLocaleString()
    $('#status').append(finish)
    $('#status').attr('class', 'updated-status').text('score updated: ' + finish)
    $('#time').hide()

                                        },
  failure: function(json_update) {
    console.log('fail');
    console.log(json_update);
  }
})

})

// $('#tournament_key').ready(function (){
//   $.ajax({
//     type: "GET",
//     url: "/golf_app/get_info/",
//     dataType: 'json',
//     //async: false,
//     data: {'tournament' : $('#tournament_key').text()},
//     success: function (json) {
//       info= $.parseJSON(json)
      
//     },
//     failure: function(json) {
//       console.log('get info fail');
//       console.log(json);
//       return {}
//     }
//   })
// })


function build_score_tbl(data) {
  $('#det-list').empty()
  $('#det-list').append('<table class="table">' + '</table>')
  
  //console.log(info)
  var picks_data = $.parseJSON((data['picks']))
  var total_data = $.parseJSON((data['totals']))
  var optimal_data = $.parseJSON((data['optimal']))
  var scores = $.parseJSON((data['scores']))
  var season_totals = $.parseJSON(data['season_totals'])
  var info = $.parseJSON(data['info'])

  //console.log('season totals: ', season_totals)
  //console.log('totals', total_data)

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
    $('#det-list table').append('<tr    class="small">' +
    '<td>' + data['rank']+ '</td>' +
    '<td>' + format_move(data['change']) + data['change'] + '</td>' +
    '<td>' + player.bold() + '</td>' +
    '<td>' + data['total_score']+ '</td>' +
    '<td>' + data['thru']+ '</td>' +
    '<td>' + data['round_score']+ '</td>' +
    '<td>' + data['r1']+ '</td>' +
    '<td>' + data['r2']+ '</td>' +
    '<td>' + data['r3']+ '</td>' +
    '<td>' + data['r4']+ '</td>' +
    '</tr>')
  })


  $('#det-list').attr('class', 'none')

  $('#totals').empty()
  var col_num_picks = $('#multi-col').data('picks')
  $('#multi-col').attr('colspan', col_num_picks).attr('style', 'text-align:center;')

  $.each(total_data, function(p, total) {
    $('#totals').append('<tr id=totals' + p + ' class=small>' + '<td>'+  p  + ' (' + season_totals[p]['diff'] +')'  + '</p>' + '<p>' +  total['total_score'] + ' / ' + total['cuts']  + '</td>'  + '</tr>')
    
    //clean this up.  Always display and drop the if.
    if (total['msg']) {$('#totals' + p).append('<td>' + total["msg"] + '</td>') }
    else if (total['winner_bonus'] >0 || total['major_bonus'] > 0 || total['cut_bonus'] > 0 || total['best_in_group'] > 0  || total['playoff_bonus'] > 0 || total['handicap'] > 0) {
      var bonus_dtl = total['winner_bonus']  + total['major_bonus'] + total['cut_bonus'] + total['best_in_group'] + total['playoff_bonus']
      $('#totals' + p).append('<td>' + total['msg'] + '<span class="bonus">' + '<p>' + 'h/c: ' + total['handicap'] + '</p>' + '<p>' +  'B: ' + bonus_dtl.toString() + '</p>' + '</span>' + '</td>') }
    else {$('#totals' + p).append('<td> </td>')}

  })

 
  $.each(picks_data, function (p, stats) {
    let filler = /[\s\.]/g;
    $.each(stats, function(index) {
      var pick = $(this)[0]['pick'].replace(filler, '')
    $('#totals' + p).append('<td id=' + p +  pick + '>' + '<span class=watermark>' + 
    '<p>' + p.substring(0, 4)  + ' : ' + index +  '</p>'  + '</span>' + '<p>' +  $(this)[0]['pick']  + '</p>' + '<p>' + $(this)[0]['score'] +
    '<span > <a id=tt-' + pick + ' href="#" data-toggle="tooltip" > <i class="fa fa-info-circle"></i> </a> </span>' +
     '</p>' +  $(this)[0]['toPar'] +  '   ' +  format_move($(this)[0]['sod_position']) +  $(this)[0]['sod_position'] + '</p>' +  '</td>')
     //console.log($('#tt-' + $(this)[0]['pick'].replace(/ +?/g, '').replace(/\./g,'') + '[data-toggle="tooltip"]'))
      $('#tt-' + pick + '[data-toggle="tooltip"]').tooltip({trigger:"hover",
                                            delay:{"show":400,"hide":800}, "title": 'gross score: ' + $(this)[0]['gross_score']
                                            }) 
     
      if ($(this)[0]['today_score'] == 'CUT') {$('#' + p + pick).addClass('cut')}
    
    //use 0 of the index to strip the extra chars in multi pick groups.  Need to fix for tournaments with 10 groups.
    
    if ($.inArray($(this)[0]['pick'], optimal_data[index[0]]['golfer']) !== -1) {$('#' + p + $(this)[0]['pick'].replace(/ +?/g, '')).addClass('best')} 
  })}) 
 

  $('#totals').append('<tr id=optimalpicks class=small> <td> <p> Best Picks </p> </td> <td> </td> </tr>')
  $.each(optimal_data, function(group, data) {
    $('#optimalpicks').append('<td colspan=' + info[group] + ' style=text-align:center;> <p>' + data["golfer"] + '</p> <p>' + data['rank'] + '</td>')
  })

  $('#totals').append('<tr id=cuts class=small> <td> <p> Cuts </p> </td> <td> </td> </tr>')
  $.each(optimal_data, function(group, data) {
    $('#cuts').append('<td colspan=' + info[group] + ' style=text-align:center;> <p>' + data["cuts"] + ' / ' + data['total_golfers'] + '</td>')
  })

  var leaders = $.parseJSON((data['leaders']))
  
  $('#cut_line').text(data['cut_line'])
  $('#leader').text("Leaders: " + leaders['leaders'] + " ;   score: " + leaders['score'])        


  $('#picks-tbl').show()
  $('#totals-table').show()

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





