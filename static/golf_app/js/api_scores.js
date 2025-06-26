let filler = /[\s\.\,\']/g;
let not_playing = ['CUT', 'WD', 'DQ', 'MDF']
$(document).ready(function() {
    
      var start = new Date()
      console.log(start)
      
      //$.getScript('/static/golf_app/js/common_scores.js')
      const common = load_common()
      common.then((response) => $('#totals-table').ready(function() {sort_table('totals-table');
                                                                        sortUserCards();
                                                                     $('#scores-div').attr('hidden', false)}))
      
      const fn1 = totalScores()
      //const fn2 = seasonPoints()
      const fn2 = function(){return}
      
      Promise.all([fn1, fn2]).then((response) => 
      {
            console.log('total scores done')
      seasonPoints()
      sort_table('totals-table')
      sortUserCards()
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
     //$('#status').html('<h5>Scores Updated</h5>')
      var done = new Date()
      var totalTime = done - start
      sec = Math.floor((totalTime/1000)%60)
      console.log(sec)
      console.log('load duration: ', done - start)
      $('#status').html('<h5>Scores Updated - duration ' + sec + ' seconds' + '</h5>')
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
      .then((response) => {
            if (!response.ok) {
                  console.log('Network response was not ok ' + response.statusText);
                  $('#status').html('<h4>Scores not updated - ' + response.status + ' ' + response.statusText + '</h4>')
                  reject(response.statusText)
            }
            else {
                  return response.json()}
            })
      .then((responseJSON) => {
            console.log('ts api returned')
            data = responseJSON

            if (data.error) {
                  $('#issues').html('<h4>Errors: ' + data.error.source + ' : ' + data.error.msg + '</h4>')
            }
            bestInGroup(data.group_stats)
            cuts(data.group_stats)
            mobileSummary(data)

            $.each(data, function(user, score) {
            if (Object.keys(score) != 'group_stats'){
                  console.log('user: ', user, ' score: ', score)
                  // For table view
                  $('#score_table_' + user).text(score.score + '/' + (score.cuts ? score.cuts : '0'));
                  // For card view
                  $('#score_card_' + user).text(score.score + '/' + (score.cuts ? score.cuts : '0'));
                  $('#ts_' + user).append('<p>Rank: ' + (score.rank ? score.rank : '') + '</p>');
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
            $('#card_season_' + user).html('  Seaon behind: ('  + info.diff + ' / ' + info.points_behind_second + ')').addClass('small').addClass('text-muted').addClass('text-center')
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
                  
                  data = responseJSON
                  console.log('picks api returned: ', data)
                  
                  $.each(data, function(i, pick) {
                        // Format SOD
                        let sod = pick.sod_position ? format_move(parseInt(pick.sod_position)) : '';

                        // Format thru
                        let thru = '';
                        try {
                              if (pick.thru && pick.thru.slice(-1) == 'Z') {
                                    thru = new Date(pick.thru).toLocaleTimeString([], {hour: 'numeric', minute:'2-digit'});
                              } else {
                                    thru = pick.thru;
                              }
                        } catch { thru = ''; }

                        // Score HTML (with tooltip)
                        let scoreHtml = '<p>' + pick.score +
                              '<span> <a id="tt-' + pick.id +
                              '" data-toggle="tooltip"><i class="fa fa-info-circle" style="color:blue;"></i></a></span> ' +
                              sod + '</p>';

                        // ToPar HTML
                        let toParHtml = '<p>' + pick.toPar + ' (' + thru + ')</p>';

                        // --- Update Card View ---
                        $('#pickrow_' + pick.pick.id + ' #' + pick.pick.id + '-score').html(scoreHtml);
                        $('#pickrow_' + pick.pick.id + ' #' + pick.pick.id + '-p2').html(toParHtml);

                        // --- Update Table View ---
                        // If your table cell contains the same score and toPar fields, update them too:
                        $('#' + pick.pick.id + ' #' + pick.pick.id + '-score').html(scoreHtml);
                        $('#' + pick.pick.id + ' #' + pick.pick.id + '-p2').html(toParHtml);

                        // If your table cell is just a single cell, you may want to update its HTML directly:
                        // $('#' + pick.pick.id).html(scoreHtml + toParHtml);

                        // Tooltip
                        $('#tt-' + pick.id + '[data-toggle="tooltip"]').tooltip({
                              trigger: "hover",
                              delay: {"show": 400, "hide": 800},
                              "title": 'gross score: ' + pick.gross_score
                        });

                        // --- Classes for cut/best ---
                        if (not_playing.indexOf(pick.thru) != -1) {
                              $('#' + pick.pick.id).removeClass('cut best').addClass('cut');           // Table
                              $('#pickrow_' + pick.pick.id).removeClass('cut best').addClass('cut');   // Card
                        }
                        });
                              })
})
}


function bestInGroup(data) {
      $.each(data, function(group, info) {
            $.each(info.golfers, function(i,golfer) {
            if (i==0){
                  $('#big-' + group).html(golfer) 
                  $('#best-picks-mobile-' + group).html(golfer)

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

function mobileSummary(data) {
$.each(data.group_stats, function(group, info) {
      console.log('mobile summary group: ', group, ' info: ', info)
    let line = 'Group ' + group + ': '+  
               '<span class="text-left"> ' + info.golfers +
               ' | Cuts: ' + info.cuts + '/' + info.total_golfers + '</span>';
                  $('#group-mobile-' + group).html(line);
      });
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
    fetch("/golf_app/get_msgs/" + $('#tournament_key').text(), {method: "GET"})
    .then((response) => response.json())
    .then((responseJSON) => {
        let data = $.parseJSON(responseJSON);

        // Get all users from handicap (or another reliable source)
        let users = Object.keys(data.handicap);

        $.each(users, function(i, user) {
            // Table: use <br>
            $('#msg_' + user).html(buildMsgLines(user, data, 'br'));
            // Card: use <div>
            $('#bonus_' + user).html(buildMsgLines(user, data, 'div'));
            $('#bonus_' + user).addClass('msgs-bg');
        });
    });
}// get_records used for match play to display group stage results
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
    

function sortUserCards() {
    // Collect all user cards
    let cards = Array.from(document.querySelectorAll('.user-card'));
    // Extract score from the score_card_USERNAME span
    cards.sort((a, b) => {
        let aUser = a.id.replace('card-', '');
        let bUser = b.id.replace('card-', '');
        let aScore = parseInt($('#score_card_' + aUser).text().trim()) || 9999;
        let bScore = parseInt($('#score_card_' + bUser).text().trim()) || 9999;
        return aScore - bScore; // Lower score is better
    });
    // Re-append cards in sorted order
    let parent = cards[0]?.parentNode;
    if (parent) {
        cards.forEach(card => parent.appendChild(card));
    }
}

function buildMsgLines(user, data, lineTag) {
    let lines = [];
    if (data.handicap && data.handicap[user]) {
        lines.push('h/c: ' + data.handicap[user].total);
    }
    if (data.pick_method) {
        $.each(data.pick_method, function(i, info) {
            if (info.user.username === user && info.method == '3') {
                lines.push('Auto Picks - no bonuses');
            }
        });
    }
    if (data.bonus_dtl) {
        $.each(data.bonus_dtl, function(i, info) {
            if (info.user.username === user) {
                lines.push(info.bonus_type_desc + ': -' + info.bonus_points);
            }
        });
    }
    return lines.map(l => `<${lineTag}>${l}</${lineTag}>`).join('');
}