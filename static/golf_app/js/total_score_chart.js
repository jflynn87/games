$(document).ready(function () {
    console.log('connected')
    fetch("/golf_app/total_score_chart_api/" + $('#season_id').text(),
    {method: "GET",
    })
  .then((response) => response.json())
  .then((responseJSON) => {
    json_data =  responseJSON
    console.log(json_data)
    var ctx = document.getElementById('trend_chart')

    var ds = []
    var colors = ['aqua', 'blue', 'red', 'purple', 'orange', 'green', 'lightgreen', 'yellow', 'pink', 'black', 'gray']
    var i = 0
    $.each(json_data.data, function(user, stats) {

        //ds = ds + "{label: '" + user + "', data: [" + stats + "]},"
        //if (user != $('#user').text())
        //{ds.push({label: user, backgroundColor: colors[i], borderColor: colors[i], data: stats, hidden: true})}
        ds.push({label: user, backgroundColor: colors[i], borderColor: colors[i], data: stats})
        i ++;
        
    })
    
    console.log('ds', ds)
    var data = {
        labels: json_data.labels,
        datasets: ds,
    }

    const config = {type: 'line', 
                    data,
                    options: {
                        plugins: {
                            title: {
                                display: true,
                                text: 'Trend Analysis - click name to toggle inclusion in chart'
                            }
                        },
            
                    }
                }



    var myChart = new Chart(ctx, 
        config

    )
    $('#chart_status_msg').hide()
  })
})