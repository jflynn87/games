function update_lb() {
    fetch("/golf_app/golf_leaderboard/",
    {method: "GET",
    })
    .then((response) =>  response.json())
    .then((responseJSON) => {
          data = JSON.parse(responseJSON)
          //console.log(data, data.length)
          var golf_table = '<table id=leaderboard_table class=table><thead><tr><th>Rank</th><th>Player</th><th>Behind 1st / 2nd</th>' +
                            '<tr></thead>'  
                            $('#golf_lb_body').append(golf_table)
                            //'<th><a href=/golf_app/fedex_picks_view>FedEx</a></th><tr></thead>'
            $.each(data, function(i, data) {
                console.log(data[0], data[1])
                $('#leaderboard_table').append('<tr id=' + data[0] + '_lb_row><td>' + data[1].rank + '</td><td>' + data[0] + '</td><td>' + data[1].diff + ' / ' + data[1].points_behind_second + '</td></tr>')   
                if (data[0] == document.getElementById('username').innerText) {
                    $('#' + data[0] + '_lb_row').addClass('highlight')
                }
            })
          }
              )
    }