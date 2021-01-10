$( document ).ready(function() {
    console.log('commencte')
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

          $('#stats-sect').append('<table id=stat-tbl class="table table-striped"> </table>')

          $('#stat-tbl').append('<thead><th>Stat Category</th><th>Game Stats</th></thead>') 
          $('#stat-tbl').append(
            '<tr id=total_score style="font-weight:bold;">' + '<td>Total Points</td> <td></td>' +  
            '<tr id=passing_yards>' + '<td>Total Passing Yards</td> <td>' + data.response.stats.total_passing_yards  + '</td>' +
            '<tr id=rushing_yards>' + '<td>Total Rushing Yards</td> <td>' + data.response.stats.total_rushing_yards  + '</td>' +
            '<tr id=total_points>' + '<td>Total Points * 5</td> <td>' + data.response.stats.total_points  + '</td>' +
            '<tr id=point_from_fg>' + '<td>Total Points from FG *5</td> <td>' + data.response.stats.points_on_fg  + '</td>' +
            '<tr id=takeaways>' + '<td>Total Takeaways * 20</td> <td>' + data.response.stats.takeaways  + '</td>' +
            '<tr id=total_sacks>' + '<td>Total Sacks * 20</td> <td>' + data.response.stats.sacks + '</td>' +
            '<tr id=total_d_td>' + '<td>Total Def/Spec Team TDs * 50</td> <td>' + data.response.stats.def_special_teams_tds + '</td>' +
            '<tr id=home_top_rusher>' + '<td>Home Top Rusher * 3</td> <td>' + data.response.stats.home_runner + '</td>' +
            '<tr id=home_top_receiver>' + '<td>Home Top Receiver * 3</td> <td>' + data.response.stats.home_receiver + '</td>' +
            '<tr id=home_top_passer>' + '<td>Home Top Passer * 3</td> <td>' + data.response.stats.home_passing + '</td>' +
            '<tr id=home_top_rating>' + '<td>Home Top Passer Rating * 3</td> <td>' + data.response.stats.home_passer_rating + '</td>' +
            '<tr id=away_top_rusher>' + '<td>Away Top Rusher * 3</td> <td>' + data.response.stats.away_runner + '</td>' +
            '<tr id=away_top_receiver>' + '<td>Away Top Receiver * 3</td> <td>' + data.response.stats.away_receiver + '</td>' +
            '<tr id=away_top_passer>' + '<td>Away Top Passer * 3</td> <td>' + data.response.stats.away_passing + '</td>' +
            '<tr id=away_top_rating>' + '<td>Away Top Passer Rating * 3</td> <td>' + data.response.stats.away_passer_rating + '</td>'  +
            '<tr id=winning_team>' + '<td>Winning Team (20 points)</td> <td>' + data.response.stats.winning_team + '</td>'  
               )


          $.each(data.response.picks, function(player, p) {
                $('#stat-tbl thead tr').append('<th>' + player + ' Entry</th>' + '<th>' + player + ' Points</th>') 
                
                //add picks to page
                $('#total_score').append('<td></td>' )
                $('#passing_yards').append('<td>' + p.passing_yards  + '</td>' )
                $('#rushing_yards').append('<td>' + p.rushing_yards  + '</td>' )
                $('#total_points').append('<td>' + p.total_points_scored  + '</td>')
                $('#point_from_fg').append('<td>' + p.points_on_fg  + '</td>')
                $('#takeaways').append('<td>' + p.takeaways  + '</td>')
                $('#total_sacks').append('<td>' + p.sacks + '</td>')
                $('#total_d_td').append('<td>' + p.def_special_teams_tds + '</td>')
                $('#home_top_rusher').append('<td>' + p.home_runner + '</td>')
                $('#home_top_receiver').append('<td>' + p.home_receiver + '</td>')
                $('#home_top_passer').append('<td>' + p.home_passing + '</td>')
                $('#home_top_rating').append('<td>' +  p.home_passer_rating + '</td>')
                $('#away_top_rusher').append('<td>' + p.away_runner + '</td>')
                $('#away_top_receiver').append('<td>' + p.away_receiver + '</td>')
                $('#away_top_passer').append('<td>' + p.away_passing + '</td>')
                $('#away_top_rating').append('<td>' + p.away_passer_rating + '</td>')  
                $('#winning_team').append('<td>' + p.winning_team + '</td>')  

                //add scores to page - should this be in this loop?  prob ok
                $('#total_score').append('<td>' + data.response.scores[player].player_total + '</td>' )
                $('#passing_yards').append('<td>' + data.response.scores[player].passing_yards  + '</td>' )
                $('#rushing_yards').append('<td>' + data.response.scores[player].rushing_yards  + '</td>' )
                $('#total_points').append('<td>' + data.response.scores[player].total_points_scored  + '</td>')
                $('#point_from_fg').append('<td>' + data.response.scores[player].points_on_fg  + '</td>')
                $('#takeaways').append('<td>' + data.response.scores[player].takeaways  + '</td>')
                $('#total_sacks').append('<td>' + data.response.scores[player].sacks + '</td>')
                $('#total_d_td').append('<td>' + data.response.scores[player].def_special_teams_tds + '</td>')
                $('#home_top_rusher').append('<td>' + data.response.scores[player].home_runner + '</td>')
                $('#home_top_receiver').append('<td>' + data.response.scores[player].home_receiver + '</td>')
                $('#home_top_passer').append('<td>' + data.response.scores[player].home_passing + '</td>')
                $('#home_top_rating').append('<td>' +  data.response.scores[player].home_passer_rating + '</td>')
                $('#away_top_rusher').append('<td>' + data.response.scores[player].away_runner + '</td>')
                $('#away_top_receiver').append('<td>' + data.response.scores[player].away_receiver + '</td>')
                $('#away_top_passer').append('<td>' + data.response.scores[player].away_passing + '</td>')
                $('#away_top_rating').append('<td>' + data.response.scores[player].away_passer_rating + '</td>')  
                $('#winning_team').append('<td>' + data.response.scores[player].winning_team + '</td>')  
                
            
            
            })  //closes each.pics

          }) 

          }
     