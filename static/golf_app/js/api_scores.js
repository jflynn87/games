let filler = /[\s\.\,\']/g;
let not_playing = ['CUT', 'WD', 'DQ']
$(document).ready(function() {
    
      var start = new Date()
      console.log(start)
      $.getScript('/static/golf_app/js/common_scores.js')
      const fn1 = totalScores()
      const fn2 = seasonPoints()
      const fn3 = udatePickData()
      summary_data()
      
      Promise.all([fn1, fn2, fn3]).then((response) => 
      {
      sort_table('totals-table')
      updateBigPicks(response[0].group_stats, response[2])
      $('#status').html('<h5>Scores Updated</h5>')
      $('#scores-div').attr('hidden', false)
      buildLeaderboard($('#tournament_key').text())
      var done = new Date()
      console.log('load duration: ', done - start)}
      )      

})


function totalScores( ) {
      return new Promise (function (resolve, reject) {
      fetch("/golf_app/get_api_scores/" + $('#tournament_key').text(),
      {method: "GET",
      }
            )
      .then((response) => response.json())
      .then((responseJSON) => {
            console.log('ts api returned')
            data = responseJSON
            bestInGroup(data.group_stats)
            cuts(data.group_stats)

            $.each(data, function(user, score) {
            if (Object.keys(score) != 'group_stats'){
            //$('#ts_' + user).text($('#ts_' + user).text() + '  '  + score.score + ' / ' + score.cuts)
            $('#ts_' + user).append('<p>'  + score.score + ' / ' + score.cuts + '</p>')
            }

            } )
            resolve(data)})
      //})
})
}


function seasonPoints() {
      return new Promise (function (resolve, reject) {
      fetch('/golf_app/season_points/' + $('#season_key').text() + '/all',
      {method: "GET",
      }
            )
      .then((response) => response.json())
      .then((responseJSON) => {
            console.log('sp api returned')
            data = $.parseJSON(responseJSON)
            $.each(data, function(user, info) {
            $('#ts_' + user).text($('#ts_' + user).text() + '  ('  + info.diff + ' / ' + info.points_behind_second + ')')
      resolve(data)})
      })
})
}

function udatePickData() {
      return new Promise (function (resolve, reject) {
            fetch('/golf_app/get_picks/' + $('#tournament_key').text() + '/' + 'only',
            {method: "GET",
            }
                  )
            .then((response) => response.json())
            .then((responseJSON) => {
                  console.log('picks data api returned')
                  data = responseJSON
                  $.each(data, function(i, pick) {
                  if (pick.sod_position) {sod = format_move(pick.sod_position) + pick.sod_position.replace(filler, '')}
                  else {sod = ''}
                  $('#' + pick.pick.id + '-score').html(
                  '<p>' + pick.score + 
                  '<span > <a id=tt-' + pick.id + 
                  ' data-toggle="tooltip" > <i class="fa fa-info-circle" style="color:blue;"></i> </a> </span>' +
                  '  ' + sod + '</p>' + 
                  '<p>' + pick.toPar + '  (' + pick.thru + ')</p>')                  
        
                  $('#tt-' + pick.id + '[data-toggle="tooltip"]').tooltip({trigger:"hover",
                  delay:{"show":400,"hide":800}, "title": 'gross score: ' + pick.gross_score})
                  if (not_playing.indexOf(pick.today_score) != -1) {$('#' + pick.pick.id).addClass('cut')}  
                  
            resolve(data)})
            })
      })
      
      
}


function bestInGroup(data) {
      $.each(data, function(group, info) {
            $.each(info.golfers, function(i,golfer) {
            if (i==0){
                  $('#big-' + group).html(golfer) 
                        }
            else {
                  $('#big-' + group).html($('#big-' + group).html()  + ', ' + golfer) 
                  }
                                                    })
            colspan = $('#grp-colspan-' + group).attr('colspan')

            $('#big-' + group).attr('colspan', colspan).addClass('small').attr('align', 'center')
      })
}


function cuts(data) {
      $.each(data, function(group, info) {
          $('#cuts-' + group).html(info.cuts + '/' + info.total_golfers) 

            colspan = $('#grp-colspan-' + group).attr('colspan')
            
            $('#cuts-' + group).attr('colspan', colspan).addClass('small').attr('align', 'center')
      })            
}

function updateBigPicks(group_stats, picks) {
      $.each(group_stats, function(group, stats) {
            $.each(stats.golfer_espn_nums, function(i, espn_num) {
                  $('.' + espn_num).addClass('best')
            })
      })
}

function summary_data() {
      fetch("/golf_app/get_summary_stats/" + $('#tournament_key').text(),
      {method: "GET",
      }
            )
      .then((response) => response.json())
      .then((responseJSON) => {
            console.log('summary stats api returned')
            data = $.parseJSON(responseJSON)
            console.log(data)
            console.log(data.leaders)
            $.each(data.leaders, function(i, leader) {
              if (i == 0) {$('#leader').text(leader)}
              else {$('#leader').text($('#leader').text() + ', ' + leader)}
            })

            $('#leader').text($('#leader').text() + ' : ' + data.leader_score)

            $('#cut_line').text('Round ' + data.curr_round + ' - ' + data.round_status)
      })
}