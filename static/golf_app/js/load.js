$(document).ready(function() {
    console.log('first step');
    /*$('#picks-tbl').hide() */
    /*$('#det-list').attr('class', 'pulse')*/
    $('#det-list').attr('class', 'spinner')
    start = new Date()
    $('#status').append(start)
    
    $.ajax({
      type: "GET",
      url: "/golf_app/get_scores/",
      data: {'tournament' : $('#tournament_key').text()},
      dataType: 'json',
      success: function (json) {
        console.log('load connected');
        
        $('#det-list').append('<table class="table">' + '</table>')
        var picks_data = $.parseJSON((json['picks']))
        var total_data = $.parseJSON((json['totals']))
        /*console.log(stats)*/

        $.each(picks_data, function(player, stats) {
             $('#det-list table').append('<thead style="background-color:lightblue">' + '<tr>' + '<th>' + player + '</th>' + 
             '<th>' + '</th>' + '<th>' + '</th>' +  '<th>' + '</th>' + '<th>' + '</th>' + 
             '</thead>' +
             '<thead>' + '<th>' + 'Golfer' + '</th>' +
             '<th>' + 'Current Position' + '</th>' +
             '<th>' + 'Score to par' + '</th>' +
             '<th>' + 'Current Round Score' + '</th>' +
             '<th>' + 'Today Change' + '</th>' +
             '</thead>')
             $.each(stats, function(group, score) {
               
              if (score['sod_position'].includes('down')) {
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

              $('#det-list table').append('<tr>' +
              '<td>' + score['pick'] + '</td>' +
              '<td>' + score['score'] + '</td>' +
              '<td>' + score['toPar'] + '</td>' +
              '<td>' + score['today_score'] + '</td>' + 
              '<td>' + move +  score['sod_position'] + '</td>'  
              + '</tr>'

        )})})

        $('#totals').empty()
        
        $.each(total_data, function(p, total) {
          $('#totals').append('<tr>' + '<td>'+ p + '</td>' + '<td>' + total['total_score'] + '</td>'  + '<td>' + total['cuts']  + '</td>'  + '</tr>')
        })
        
        leader = json['leaders']
        $('#leader').text('leader: ' + leader)
        $('#cut_line').text(json['cut_line'])
        console.log(leader)        


        /*$('#totals').append()*/
            /*$('#pulse').hide()*/
            $('#det-list').attr('class', 'none')
            $('#picks-tbl').show()
            finish = new Date()
            $('#status').append(finish)
            $('#status').attr('class', 'updated-status').text('score updated' + finish)
            $('#time').hide()
            console.log('duration: ', start, finish)
  
                                            },
      failure: function(json) {
        console.log('fail');
        console.log(json);
      }
    })
  
})

  