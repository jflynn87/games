$(document).ready(function() {
    console.log('first step');
    /*$('#picks-tbl').hide() */
    /*$('#det-list').attr('class', 'pulse')*/
    $('#det-list').attr('class', 'spinner')
    start = new Date() 
    console.log('month', start.toString("MMM dd"), start.getTimezoneOffset())
    console.log(new Date(start - start.getTimezoneOffset()))
  
    $('#status').append(start)
    /*var fromatted = d.toLocaleFormat("%d.%m.%Y %H:%M (%a)");*/


    $.ajax({
      type: "GET",
      url: "/golf_app/get_db_scores/",
      data: {'tournament' : $('#tournament_key').text()},
      dataType: 'json',
      success: function (json) {
        console.log('load connected');
        build_score_tbl(json)
        console.log('first load duration: ', start, new Date()) 
        /*long running process */

        $.ajax({
          type: "GET",
          url: "/golf_app/get_scores/",
          data: {'tournament' : $('#tournament_key').text()},
          dataType: 'json',
          success: function (json_update) {
            console.log('load connected');
            build_score_tbl(json_update)
            build_random_data(json_update)
            console.log('updated load duration: ', start, new Date()) 
            $('#status').append(new Date())
            $('#status').attr('class', 'updated-status').text('score updated: ' + new Date())
            $('#time').hide()
        
                                                },
          failure: function(json_update) {
            console.log('fail');
            console.log(json_update);
          }
        })


      },
      failure: function(json) {
        console.log('fail');
        console.log(json);
      }
    })

    
  
})

function build_score_tbl(data) {

$('#det-list').empty()
$('#det-list').append('<table class="table">' + '</table>')
var picks_data = $.parseJSON((data['picks']))
var total_data = $.parseJSON((data['totals']))

$.each(picks_data, function(player, stats) {
    console.log(player, stats)
     $('#det-list table').append('<thead style="background-color:lightblue">' + '<tr>' + '<th>' + player + '</th>' + 
     '<th>' + '</th>' + '<th>' + '</th>' +  '<th>' + '</th>' + '<th>' + '</th>' + '<th>' + '</th>' + 
     '</thead>' +
     '<thead>' + '<th>' + 'Golfer' + '</th>' +
     '<th>' + 'Current Position' + '</th>' +
     '<th>' + 'Thru' + '</th>' +
     '<th>' + 'Score to par' + '</th>' +
     '<th>' + 'Current Round' + '</th>' +
     '<th>' + 'Today Change' + '</th>' +
     '</thead>')
     $.each(stats, function(group, score) {
       
      if (score['sod_position'] == null) {
        move=''} 
      else if (score['sod_position'].includes('down')) {
        move = '<svg class="bi bi-box-arrow-down text-danger" width="24" height="24" viewBox="0 0 20 20" fill="currentColor" xmlns="http://www.w3.org/2000/svg"> \
              <path fill-rule="evenodd" d="M6.646 13.646a.5.5 0 01.708 0L10 16.293l2.646-2.647a.5.5 0 01.708.708l-3 3a.5.5 0 01-.708 0l-3-3a.5.5 0 010-.708z" clip-rule="evenodd"></path> \
              <path fill-rule="evenodd" d="M10 6.5a.5.5 0 01.5.5v9a.5.5 0 01-1 0V7a.5.5 0 01.5-.5z" clip-rule="evenodd"></path> \
              <path fill-rule="evenodd" d="M4.5 4A1.5 1.5 0 016 2.5h8A1.5 1.5 0 0115.5 4v7a1.5 1.5 0 01-1.5 1.5h-1.5a.5.5 0 010-1H14a.5.5 0 00.5-.5V4a.5.5 0 00-.5-.5H6a.5.5 0 00-.5.5v7a.5.5 0 00.5.5h1.5a.5.5 0 010 1H6A1.5 1.5 0 014.5 11V4z" clip-rule="evenodd"></path> </svg>'
               } 
        else if (score['sod_position'].includes('up')) {
        move = '<svg class="bi bi-box-arrow-up text-success" width="24" height="24" viewBox="0 0 20 20" fill="currentColor" xmlns="http://www.w3.org/2000/svg"> \
        <path fill-rule="evenodd" d="M6.646 6.354a.5.5 0 00.708 0L10 3.707l2.646 2.647a.5.5 0 00.708-.708l-3-3a.5.5 0 00-.708 0l-3 3a.5.5 0 000 .708z" clip-rule="evenodd"></path> \
        <path fill-rule="evenodd" d="M10 13.5a.5.5 0 00.5-.5V4a.5.5 0 00-1 0v9a.5.5 0 00.5.5z" clip-rule="evenodd"></path> \
        <path fill-rule="evenodd" d="M4.5 16A1.5 1.5 0 006 17.5h8a1.5 1.5 0 001.5-1.5V9A1.5 1.5 0 0014 7.5h-1.5a.5.5 0 000 1H14a.5.5 0 01.5.5v7a.5.5 0 01-.5.5H6a.5.5 0 01-.5-.5V9a.5.5 0 01.5-.5h1.5a.5.5 0 000-1H6A1.5 1.5 0 004.5 9v7z" clip-rule="evenodd"></path> </svg>'
         } 
        else {move = ""}
  
      $('#det-list table').append('<tr style=color:' + score['winner'] + '>' +
      '<td>' + score['pick'] + '</td>' +
      '<td>' + score['score'] + '</td>' +
      '<td>' + score['thru'] + '</td>' +
      '<td>' + score['toPar'] + '</td>' +
      '<td>' + score['today_score'] + '</td>' + 
      '<td>' + move +  score['sod_position'] + '</td>'  
      + '</tr>')
      })})
      $('#det-list').attr('class', 'none')

$('#totals').empty()

$.each(total_data, function(p, total) {
  if (total['winner_bonus'] >0 || total['major_bonus'] > 0 || total['cut_bonus'] > 0) {
    var bonus_dtl = total['winner_bonus']  + total['major_bonus'] + total['cut_bonus'] 
    $('#totals').append('<tr>' + '<td>'+ p + '<span class="bonus">' + total['msg'] + ' - Bonus Points: ' + bonus_dtl.toString() + '</span>' + '</td>' + '<td>' + total['total_score'] + '</td>'  + '<td>' + total['cuts']  + '</td>'  + '</tr>')
  }
  else {
  $('#totals').append('<tr>' + '<td>'+ p + total['msg'] + '</td>' + '<td>' + total['total_score'] + '</td>'  + '<td>' + total['cuts']  + '</td>'  + '</tr>')}
})



var leaders = $.parseJSON((data['leaders']))
console.log(leaders)


$('#cut_line').text(data['cut_line'])
$('#leader').text("Leaders: " + leaders['leaders'] + " ;   score: " + leaders['score'])        


/*$('#totals').append()*/
    /*$('#pulse').hide()*/
    
    $('#picks-tbl').show()
/*    finish = new Date()
    $('#status').append(finish)
    $('#status').attr('class', 'updated-status').text('score updated' + finish)
    $('#time').hide()
*/

}

function build_random_data(data) {
  optimal = $.parseJSON(data['optimal'])
  var total_score = 0
  $.each(optimal, function(group, data) {
  $('#optimal').append('<tr>' + '<td>' + 'Group ' + group + '</td>' + 
                        '<td>' + data['golfer'] + '</td>' +
                        '<td>' + data['rank'] + '</td>' + '</tr>')
  total_score = total_score + data['rank']
  $('#cuts').append('<tr>' + '<td>' + 'Group ' + group + '</td>' + 
  '<td>' + data['cuts'] + '</td>' +
  '<td>' + data['total_golfers'] + '</td>' + '</tr>')
  })
  $('#optimal').append('<tr>' + '<td>'+ '</td>' + '<td>' +
   'Total: ' + '</td>' + '<td>' + total_score + '</td>' + '</tr>')
}
