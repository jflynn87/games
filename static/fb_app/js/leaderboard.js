function update_fb_lb() {
    fetch("/fb_app/fb_leaderboard/",
    {method: "GET",
    })
    .then((response) =>  response.json())
    .then((responseJSON) => {
          data = JSON.parse(responseJSON)
          console.log(data, data.length)
          var fb_table = '<table class=table><thead><tr><th>Rank</th><th>Player</th><th>Behind</th><tr></thead>'
          for (var d of data) {
            if (d[0] == document.getElementById('username').innerText) {
              fb_table = fb_table += ('<tr class=table-danger> <td>' + d[1]['rank'] + '</td> <td> ' + d[0] + '</td> <td style="text-align:center;">' + d[1]['behind'] + '</td>' + 
                                                          '</tr>')}
              else {
              fb_table += ('<tr><td>' + d[1]['rank'] + '</td> <td> ' + d[0] + '</td> <td style="text-align:center;">' + d[1]['behind'] + '</td>' + 
                                 '</tr>')
              }
            }
              fb_table + '</table>'

              //ele.appendChild(text)
              document.getElementById('fb_lb_body').innerHTML = fb_table
              
            }
                    
          )
          
    }