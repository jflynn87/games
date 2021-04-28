$(document).ready(function () {
    console.log('connected')
    draw_chart()
})
function draw_chart() {
    num_t = $('#show_t :selected').val()
    fetch("/golf_app/total_score_chart_api/" + $('#season_id').text() + '/' + num_t,
    {method: "GET",
    })
  .then((response) => response.json())
  .then((responseJSON) => {
    json_data =  responseJSON
    console.log(json_data)
    $('#chart-sect').remove()
    $('#chart').append("<div id='chart-sect'><h4 id='chart_status_msg' class=status'>Loading Chart ...</h4> <canvas id='trend_chart' class='chart-style'></canvas></div>")
    
    var ctx = document.getElementById('trend_chart').getContext("2d");
    
    
    var ds = []
    var colors = ['aqua', 'blue', 'red', 'purple', 'orange', 'green', 'lightgreen', 'yellow', 'pink', 'black', 'gray']
    var i = 0
    $.each(json_data.data, function(user, stats) {
        ds.push({label: user, backgroundColor: colors[i], borderColor: colors[i], data: stats})
        i ++;
                                                })
    var data = {
        labels: json_data.labels,
        datasets: ds,
        yAxisID: 'left-y-axis',
        yAxisID: 'right-y-axis'
    }

    var options = {//type: 'line', 
                    //data,
                    
                        //responsive: false,
                        //maintainAspectRatio: false,
                    
                        plugins: {
                            title: {
                                display: true,
                                text: 'Trend Analysis - click name to toggle inclusion in chart'
                                    }
                                 },
                        scales: {
                            'left-y-axis': {
                                display: true,
                                type: 'linear',
                                position: 'right',
                                min: 0,
                                max: json_data.min_scale

                                    },
                                'right-y-axis':    {
                                display: true,
                                type: 'linear',
                                position: 'left',
                                min: 0,
                                max: json_data.min_scale
                                   }
                    }
                
            }

    var oldChart = ctx

    var myChart = new Chart(ctx, 
    {type: 'line',
     data: data,
     options: options
    }
                    )
  
    $('#chart_status_msg').hide()
  })
}
