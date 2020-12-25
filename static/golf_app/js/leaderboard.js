function update_lb() {
    fetch("/golf_app/golf_leaderboard/",
    {method: "GET",
    })
    .then((response) =>  response.json())
    .then((responseJSON) => {
          data = JSON.parse(responseJSON)
          console.log(data, data.length)
          var golf_table = '<table class=mytable><thead><tr><th>Rank</th><th>Player</th><th>Behind</th><tr></thead>'
          var i = 0
          //for (i; i < d.length; i++) {
            for (var d of data) {
                if (d[0] == document.getElementById('username').innerText) {
                    golf_table = golf_table += ('<tr class=highlight> <td>' + d[1]['rank'] + '</td> <td> ' + d[0] + '</td> <td>' + d[1]['diff'] + '</td>') + '</tr>'
                }
                else {
                    golf_table = golf_table += ('<tr> <td>' + d[1]['rank'] + '</td> <td> ' + d[0] + '</td> <td>' + d[1]['diff'] + '</td>') + '</tr>'
                }
              
               
            
            }
              golf_table + '</table>'
              //ele.appendChild(text)
              document.getElementById('golf_lb_body').innerHTML = golf_table
          }
              )
          
    }