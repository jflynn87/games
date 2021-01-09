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
          console.log(data, data.length)

          $('#stats-sect').append('<table id=stat-tbl class="table table-striped"> </table>')

          $('#stat-tbl').append('<thead><th>Stat Category</th><th>Game Stats</th></thead>') 
          $.each(data.response.picks, function(player, data) {
                $('#stat-tbl thead tr').append('<th>' + player + ' Entry</th>' + '<th>' + player + ' Points</th>') })
          $('#stat-tbl').append(
              '<tr id=passing_yards>' + '<td>Total Passing Yards</td></tr>' + 
              '<tr id=rushing_yards>' + '<td>Total Rushing Yards</td>' + 
              '<tr id=total_points>' + '<td>Total Points</td>' + 
              '<tr id=point_from_fg>' + '<td>Total Points from FG</td>' +
              '<tr id=takeaways>' + '<td>Total Takeaways</td>' +
              '<tr id=total_sacks>' + '<td>Total Sacks</td>' +
              '<tr id=total_d_td>' + '<td>Total Def/Spec Team TDs</td>' +
              '<tr id=home_top_rusher>' + '<td>Home Top Rusher</td>' +
              '<tr id=home_top_receiver>' + '<td>Home Top Receiver</td>' +
              '<tr id=home_top_passer>' + '<td>Home Top Passer</td>' +
              '<tr id=home_top_rating>' + '<td>Home Top Passer Rating</td>' +
              '<tr id=away_top_rusher>' + '<td>Away Top Rusher</td>' +
              '<tr id=away_top_receiver>' + '<td>Away Top Receiver</td>' +
              '<tr id=away_top_passer>' + '<td>Away Top Passer</td>' +
              '<tr id=away_top_rating>' + '<td>Away Top Passer Rating</td>' 
                 )
          $.each(data.response.picks, function (player, data) {$('#passing_yards').append('<td id="passing_yards-' + player + '"> Text</td>')}) 

           //for (var d of data) {
        //     if (d[0] == document.getElementById('username').innerText) {
        //       fb_table = fb_table += ('<tr class=highlight> <td>' + d[1]['rank'] + '</td> <td> ' + d[0] + '</td> <td>' + d[1]['behind'] + '</td>' + '</tr>')}
        //       else {
        //       fb_table += ('<tr> <td>' + d[1]['rank'] + '</td> <td> ' + d[0] + '</td> <td>' + d[1]['behind'] + '</td>') + '</tr>'
        //       }
        //     }
        //       fb_table + '</table>'

        //       //ele.appendChild(text)
        //       document.getElementById('fb_lb_body').innerHTML = fb_table
          }
              )
          
    }