$( document ).ready(function() {
    update_scores()
})


function update_scores() {
    fetch("/fb_app/update_playoff_scores/",
    {method: "GET",
    })
    .then((response) =>  response.json())
    .then((responseJSON) => {
          data = responseJSON
          console.log(data)
          if (!data.response.error) {
         
          $('#stats-sect').append('<table id=stat-tbl class="table table-sm table-striped table-bordered "><tbody> </tbody> </table>')

/*           $('#stat-tbl').append('<thead><th>Stat Category</th><th>Game Stats</th></thead>') 
          $('#stat-tbl').append(
            '<tr id=total_score style="font-weight:bold;">' + '<td>Total Points</td> <td></td>' +  
            '<tr id=total_points>' + '<td>Total Points</td> <td>' + data.response.stats.total_points  + '</td>' +
            '<tr id=point_from_fg>' + '<td>Total Points from FG</td> <td>' + data.response.stats.points_on_fg  + '</td>' +
            '<tr id=takeaways>' + '<td>Total Takeaways</td> <td>' + data.response.stats.takeaways  + '</td>' +
            '<tr id=total_sacks>' + '<td>Total Sacks</td> <td>' + data.response.stats.sacks + '</td>' +
            '<tr id=total_d_td>' + '<td>Total Def/Spec Team TDs</td> <td>' + data.response.stats.def_special_teams_tds + '</td>' +
            '<tr id=home_top_rusher>' + '<td>' + data.response.stats.teams.home + ' Top Rusher</td> <td>' + data.response.stats.home_runner + '</td>' +
            '<tr id=home_top_receiver>' + '<td>' + data.response.stats.teams.home + 'Top Receiver</td> <td>' + data.response.stats.home_receiver + '</td>' +
            '<tr id=home_top_rating>' + '<td>' + data.response.stats.teams.home + ' Top Passer Rating</td> <td>' + data.response.stats.home_passer_rating + '</td>' +
            '<tr id=away_top_rusher>' + '<td>' + data.response.stats.teams.away + ' Top Rusher</td> <td>' + data.response.stats.away_runner + '</td>' +
            '<tr id=away_top_receiver>' + '<td>' + data.response.stats.teams.away + ' Top Receiver</td> <td>' + data.response.stats.away_receiver + '</td>' +
            '<tr id=away_top_rating>' + '<td>' + data.response.stats.teams.away + ' Top Passer Rating</td> <td>' + data.response.stats.away_passer_rating + '</td>'  +
            '<tr id=winning_team>' + '<td>Winning Team</td> <td>' + data.response.stats.winning_team + '</td>'  
               )
 */
            $('#stat-tbl').append('<thead>' + 
                                    '<th>Player</th>' +
                                    '<th>Player Score</th>' +
                                    '<th colspan=2>Winning Team</th>' +
                                    '<th colspan=2>Total Points</th>' +
                                    '<th colspan=2>FG Pts</th>' +
                                    '<th colspan=2>Takeaway</th>' +
                                    '<th colspan=2>Sacks</th>' +
                                    '<th colspan=2>D/ST TD</th>' +
                                    '<th colspan=2>' + data.response.stats.teams.home + 'Rush</th>' +
                                    '<th colspan=2>' + data.response.stats.teams.home + 'Rec</th>' +
                                    '<th colspan=2>' + data.response.stats.teams.home + 'Pass Rating</th>' +
                                    '<th colspan=2>' + data.response.stats.teams.away + 'Rush</th>' +
                                    '<th colspan=2>' + data.response.stats.teams.away + 'Rec</th>' +
                                    '<th colspan=2>' + data.response.stats.teams.away + 'Pass Rating</th>' +
                                    '</thead>') 
          
            
            $('#stat-tbl tbody').append(
                                    '<tr><th>Actual Results</th>' +
                                    '<td></td>' +
                                    '<td colspan=2 style=text-align:center;>' + data.response.stats.winning_team + '</td>' +
                                    '<td colspan=2 style=text-align:center;>' + data.response.stats.total_points + '</td>' +
                                    '<td colspan=2 style=text-align:center;>' + data.response.stats.points_on_fg + '</td>' +
                                    '<td colspan=2 style=text-align:center;>' + data.response.stats.takeaways + '</td>' +
                                    '<td colspan=2 style=text-align:center;>' + data.response.stats.sacks + '</td>' +
                                    '<td colspan=2 style=text-align:center;>' + data.response.stats.def_special_teams_tds + '</td>' +
                                    '<td colspan=2 style=text-align:center;>' + data.response.stats.home_runner + '</td>' +
                                    '<td colspan=2 style=text-align:center;>' + data.response.stats.home_receiver + '</td>' +
                                    '<td colspan=2 style=text-align:center;>' + data.response.stats.home_passer_rating + '</td>' +
                                    '<td colspan=2 style=text-align:center;>' + data.response.stats.away_runner + '</td>' +
                                    '<td colspan=2 style=text-align:center;>' + data.response.stats.away_receiver + '</td>' +
                                    '<td colspan=2 style=text-align:center;>' + data.response.stats.away_passer_rating + '</td>' +
                                    '</tr>')
          
        $.each(data.response.picks, function(player, p) {
                               
                //add picks to page
               
                $('#stat-tbl tbody').append('<tr>' + 
                                            '<th>' + player + '</th>' +
                                            '<td>' + data.response.scores[player].player_total + '</td>' +
                                            '<td>' + p.winning_team + '</td>' +  
                                            format_score(data.response.scores[player].winning_team) +  
                                            '<td>' + p.total_points_scored + '</td>' +
                                             format_score(data.response.scores[player].total_points_scored)  +  
                                            '<td>' + p.points_on_fg  + '</td>' + 
                                            format_score(data.response.scores[player].points_on_fg) + 
                                            '<td>' + p.takeaways  + '</td>' +
                                            format_score(data.response.scores[player].takeaways) + 
                                            '<td>' + p.sacks + '</td>' +
                                            format_score(data.response.scores[player].sacks) + 
                                            '<td>' + p.def_special_teams_tds + '</td>' +
                                            format_score(data.response.scores[player].def_special_teams_tds) + 
                                            '<td>' + p.home_runner + '</td>' +
                                            format_score(data.response.scores[player].home_runner) + 
                                            '<td>' + p.home_receiver + '</td>' + 
                                            format_score(data.response.scores[player].home_receiver) + 
                                            '<td>' +  p.home_passer_rating + '</td>' +
                                            format_score(data.response.scores[player].home_passer_rating)  + 
                                            '<td>' + p.away_runner + '</td>' + 
                                            format_score(data.response.scores[player].away_runner) + 
                                            '<td>' + p.away_receiver + '</td>' + 
                                            format_score(data.response.scores[player].away_receiver) + 
                                            '<td>' + p.away_passer_rating + '</td>' + 
                                            format_score(data.response.scores[player].home_receiver)   
                                            
                )}
        )

                //add scores to page - should this be in this loop?  prob ok
                // $('#total_score').append('<td>' + data.response.scores[player].player_total + '</td>' )
                // $('#total_points').append('<td>' + data.response.scores[player].total_points_scored  + '</td>')
                // $('#point_from_fg').append('<td>' + data.response.scores[player].points_on_fg  + '</td>')
                // $('#takeaways').append('<td>' + data.response.scores[player].takeaways  + '</td>')
                // $('#total_sacks').append('<td>' + data.response.scores[player].sacks + '</td>')
                // $('#total_d_td').append('<td>' + data.response.scores[player].def_special_teams_tds + '</td>')
                // $('#home_top_rusher').append('<td>' + data.response.scores[player].home_runner + '</td>')
                // $('#home_top_receiver').append('<td>' + data.response.scores[player].home_receiver + '</td>')
                // $('#home_top_rating').append('<td>' +  data.response.scores[player].home_passer_rating + '</td>')
                // $('#away_top_rusher').append('<td>' + data.response.scores[player].away_runner + '</td>')
                // $('#away_top_receiver').append('<td>' + data.response.scores[player].away_receiver + '</td>')
                // $('#away_top_rating').append('<td>' + data.response.scores[player].away_passer_rating + '</td>')  
                // $('#winning_team').append('<td>' + data.response.scores[player].winning_team + '</td>')  
        
            

          //  })  //closes each.pics
        } 
        else {
            $('#stats-sect').append('<h2> Scores Not Ready </h2>')
        }

            $('#message').hide()
            $('#stats-sect').toggleClass('status')
          }) 

          }
     
function format_score(score) {
    console.log(score)
    if (score == 0) {
        return '<td>-</td>'
    }
    else {
        return '<td style=background-color:pink>' + score + '</td>'
    }
}