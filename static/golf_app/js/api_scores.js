let filler = /[\s\.\,\']/g;
let not_playing = ['CUT', 'WD', 'DQ', 'MDF']
$(document).ready(function() {
    
      var start = new Date()
      console.log(start)
      
      //$.getScript('/static/golf_app/js/common_scores.js')
      const common = load_common()
      common.then((response) => $('#totals-table').ready(function() {sort_table('totals-table');
                                                                     $('#scores-div').attr('hidden', false)}))
      
      const fn1 = totalScores()
      const fn2 = seasonPoints()
      
      Promise.all([fn1, fn2]).then((response) => 
      {

      sort_table('totals-table')
      udatePickData()
      if ($('#pga_t_num').text() != '470')
      {

      updateBigPicks(response[0].group_stats, response[2])
      //$('#status').html('<h5>Scores Updated</h5>')
      $('#scores-div').attr('hidden', false)
      summary_data()


      buildLeaderboard($('#tournament_key').text())}
      msgs()

      if ($('#pga_t_num').text() == '470') {
            get_records()
            //get_ranks()
      }
     $('#status').html('<h5>Scores Updated</h5>')
      var done = new Date()
      console.log('load duration: ', done - start)
      }
      )      

})

function load_common() {
      return new Promise(function (resolve,reject) {
            common = $.getScript('/static/golf_app/js/common_scores.js')
            resolve(common)
      })
}


function totalScores( ) {
      return new Promise (function (resolve, reject) {
      if ($('#pga_t_num').text() == '470') {
            url = "/golf_app/mp_scores/" + $('#tournament_key').text()
      }
      else {url = "/golf_app/get_api_scores/" + $('#tournament_key').text()}

      fetch(url,
      {method: "GET",
      })
      .then((response) => response.json())
      .then((responseJSON) => {
            console.log('ts api returned')
            data = responseJSON

            if (data.error) {
                  $('#issues').html('<h4>Errors: ' + data.error.source + ' : ' + data.error.msg + '</h4>')
            }
            bestInGroup(data.group_stats)
            cuts(data.group_stats)

            $.each(data, function(user, score) {
            if (Object.keys(score) != 'group_stats'){
            $('#score_' + user).html(score.score + ' / ' + score.cuts)
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
            $('#name_' + user).html(user + '  ('  + info.diff + ' / ' + info.points_behind_second + ')')
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

                  if (pick.sod_position) {sod = format_move(parseInt(pick.sod_position))}
                  else {sod = ''}

                  try {if (pick.thru.slice(-1) == 'Z') {
                        var utcDate = pick.thru;
                        thru = new Date (utcDate).toLocaleTimeString([], {hour: 'numeric', minute:'2-digit'})
                  }
                  else {thru = pick.thru}}
                  catch {thru = ''}
                  
                  $('#' + pick.pick.id + '-score').html(
                         '<p>' + pick.score + 
                         '<span > <a id=tt-' + pick.id + 
                         ' data-toggle="tooltip" > <i class="fa fa-info-circle" style="color:blue;"></i> </a> </span>' +
                         '  ' + sod + '</p>') 

                  if ($('#pga_t_num').text() != '470')
                         {$('#' + pick.pick.id + '-p2').html('<p>' + pick.toPar + ' (' + thru + ')</p>')}

                  $('#tt-' + pick.id + '[data-toggle="tooltip"]').tooltip({trigger:"hover",
                  delay:{"show":400,"hide":800}, "title": 'gross score: ' + pick.gross_score})

                  if (not_playing.indexOf(pick.thru) != -1) {$('#' + pick.pick.id).addClass('cut')}  
                  
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
                  $('#big-' + group).append('<p>' + golfer + '</p>')
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
            if (data.source == 'espn_scrape') {
                  console.log('espn_scrape')
            }
            else {
            $.each(data.leaders, function(i, leader) {
              if (i == 0) {$('#leader').text(leader)}
              else {$('#leader').text($('#leader').text() + ', ' + leader)}
            })

            $('#leader').text($('#leader').text() + ' : ' + data.leader_score)
            if (data.cut_info.line_type == 'Actual') {c_type = ''}
            else (c_type = data.cut_info.line_type)
            $('#cut_line').text('Round ' + data.curr_round + ' - ' + data.round_status + ', ' + c_type + 'Cut Line: ' + data.cut_info.cut_score)
            $('#cut_line').append('<br>')
            $('#cut_line').append('<p> Base cut penalty: ' + data.cut_num + '</p>')
      }
      })
}

function msgs() {
      fetch("/golf_app/get_msgs/" + $('#tournament_key').text(),
      {method: "GET",
      }
            )
      .then((response) => response.json())
      .then((responseJSON) => {
            console.log('get msgs api returned')
            data = $.parseJSON(responseJSON)
             $.each(data.handicap, function(user, handi) {
                   $('#msg_' + user).text('h/c: ' + handi.total)
             })
            
            $.each(data.pick_method, function(i, info) {
                  if (info.method == '3'){
                        $('#msg_'+ info.user.username).append('<p>Auto Picks - no bonuses')
                  }
            })
            $.each(data.bonus_dtl, function(i, info) {
                  $('#msg_' + info.user.username).append('<p>' + info.bonus_type_desc + ': -' + info.bonus_points + '</p>')
            })
      })
}

// get_records used for match play to display group stage results
function get_records() {
      fetch("/golf_app/get_mp_records/" + $('#tournament_key').text(),
      {method: "GET",
       })
      .then((response) => response.json())
      .then((responseJSON) => {
        record_data = responseJSON

      $.each(record_data, function(golfer, record) {
            var rec = ''
            $.each(record, function (i, r){
            if (i == record.length -1){
                  rec = rec + r
            }
            else
            {rec = rec + r + '-'}
      })
            $('#' + golfer + '-p2').html(rec)
      })

    })
    }
// function get_ranks() {
//       fetch("/golf_app/get_mp_ranks/" + $('#tournament_key').text(),
//       {method: "GET",
//        })
//       .then((response) => response.json())
//       .then((responseJSON) => {
//         rankData = responseJSON

//         $.each(rankData, function(field, rank) {
//               $('#' + field + '-p2').append('<p>grp rank: ' + rank + '</p>')
//         })
//       })
// }
    