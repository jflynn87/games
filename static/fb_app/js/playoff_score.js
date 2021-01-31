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
         
          $('#stats-sect').append('<table id=stat-tbl class="table table-striped table-sm "><thead> </thead> <tbody> </tbody> </table>')

          $('#stat-tbl thead').append( 
                                    '<th class="top_row left_col">Player</th>' +
                                    '<th class=top_row>Player Score</th>' +
                                    '<th colspan=2 class=top_row>Winning Team</th>' +
                                    '<th colspan=2 class=top_row>Total Points</th>' +
                                    '<th colspan=2 class=top_row>FG Pts</th>' +
                                    '<th colspan=2 class=top_row>Takeaway</th>' +
                                    '<th colspan=2 class=top_row>Sacks</th>' +
                                    '<th colspan=2 class=top_row>D/ST TD</th>' +
                                    '<th colspan=2 class=top_row>' + data.response.stats.teams.home + ' Rush</th>' +
                                    '<th colspan=2 class=top_row>' + data.response.stats.teams.home + ' Rec</th>' +
                                    '<th colspan=2 class=top_row>' + data.response.stats.teams.home + ' Pass Rating</th>' +
                                    '<th colspan=2 class=top_row>' + data.response.stats.teams.away + ' Rush</th>' +
                                    '<th colspan=2 class=top_row>' + data.response.stats.teams.away + ' Rec</th>' +
                                    '<th colspan=2 class=top_row>' + data.response.stats.teams.away + ' Pass Rating</th>' 
                                    ) 
          
            
            $('#stat-tbl tbody').append(
                                    //'<tr style=border-width:thick;><th style=border-right:solid;>Actual Results</th>' +
                                    '<tr class=actual_row><th class=left_col>Actual Results</th>' +
                                    '<td class=mid_cell></td>' +
                                    '<td colspan=2 class=mid_cell> <strong>' + data.response.stats.winning_team + '</td> </strong>' +
                                    '<td colspan=2 class=mid_cell> <strong>' + data.response.stats.total_points + '</td> </strong>' +
                                    '<td colspan=2 class=mid_cell> <strong>' + data.response.stats.points_on_fg + '</td> </strong>' +
                                    '<td colspan=2 class=mid_cell> <strong>' + data.response.stats.takeaways + '</td> </strong>' +
                                    '<td colspan=2 class=mid_cell> <strong>' + data.response.stats.sacks + '</td> </strong>' +
                                    '<td colspan=2 class=mid_cell> <strong>' + data.response.stats.def_special_teams_tds + '</td> </strong>' +
                                    '<td colspan=2 class=mid_cell> <strong>' + data.response.stats.home_runner + '</td> </strong>' +
                                    '<td colspan=2 class=mid_cell> <strong>' + data.response.stats.home_receiver + '</td> </strong>' +
                                    '<td colspan=2 class=mid_cell> <strong>' + data.response.stats.home_passer_rating + '</strong> </td>' +
                                    '<td colspan=2 class=mid_cell> <strong>' + data.response.stats.away_runner + '</strong> </td>' +
                                    '<td colspan=2 class=mid_cell> <strong>' + data.response.stats.away_receiver + '</strong> </td>' +
                                    '<td colspan=2 class=mid_cell> <strong>' + data.response.stats.away_passer_rating + '</strong> </td>' +
                                    '</tr>')
          
        $.each(data.response.picks, function(player, p) {
                               
                //add picks to page
               
                $('#stat-tbl tbody').append('<tr>' + 
                                            '<th class=left_col>' + player + '</th>' +
                                            '<td class=mid_cell> <strong>' + data.response.scores[player].player_total + '</strong> </td>' +
                                            '<td class>' + p.winning_team + '</td>' +  
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
                                            
                )
                 }
                 
        )
        
        sort_table()
            
        } 
        else {
            $('#stats-sect').append('<h2> Scores Not Ready </h2>')
        }

            $('#message').hide()
            $('#stats-sect').toggleClass('status')
          })

          }

function format_score(score) {
    //console.log(score)
    if (score == 0) {
        return '<td class=mid_cell>-</td>'
    }
    else {
        return '<td class=mid_cell style=background-color:pink>' + score + '</td>'
    }
}

function sort_table() {
    var table, rows, swtiching, i, x, y, shouldSwitch;
    table = $('#stat-tbl')
    switching = true;
    
    while(switching) {
      switching = false;
      rows = table[0].rows;
      console.log('rowss', rows.length)
      
      for (i=1; i < (rows.length - 1); i++) {
        shouldSwitch = false;
        x = rows[i].getElementsByTagName('td')[0];
        y = rows[i + 1].getElementsByTagName('td')[0];
        
        
        if (Number(x.innerText) < Number(y.innerText)) {
            console.log(i, Number(x.innerText), Number(y.innerText))        
          shouldSwitch = true;
          break;
        }
    }
        if (shouldSwitch) {
            console.log('switching', rows[i])
          rows[i].parentNode.insertBefore(rows[i +1], rows[i]);
          switching = true;
        }
     
     }
     $('#stat-tbl tr:last').addClass('last_row')
   
    }
    
    