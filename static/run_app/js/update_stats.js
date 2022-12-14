$(document).ready(function () {
    var start = new Date()
    fetch("/run_app/get_run_data",
    {method: "GET",
    })
.then((response) => response.json())
.then((responseJSON) => {
    data = responseJSON
    console.log('runs: ', data)
    if (data.error) {$('#shoe_stats').append("<h3>ERROR: " + data.error + "</h3>")
                        }
    else {
        fetch("/run_app/get_shoe_data_api",
        {method: "GET",
        })
        .then((response) => response.json())
        .then((responseJSON) => {
            data = responseJSON
            console.log('shoes: ', data)
            if (data.error) {$('#shoe_stats').append("<h3>SHOE APPI ERROR: " + data.error + "</h3>")
                                }
            else {
                $('#shoe_stats').append('<table id=shoe_table class=table></table>')
                $.each(data.shoes, function(shoe, stats) {
                    $('#shoe_table').append('<tr><td>' + stats.shoes__name + '</td><td>' + stats.dist__sum + '</td></tr>')
                })
                $('#shoe_stats').append('<table id=run_table class=table></table>')
                $.each($.parseJSON(data.runs), function(i, run) {
                    $('#run_table').append('<tr><td>' + run.fields.date + '</td><td>' + run.fields.dist + '</td><td><a href=run_app/update_run/' + run.pk + '/>' + run.fields.shoes + '</a></td></tr>')
                })
            $('#shoe_update').empty()
                } 
            })
    }
    
    })
}
    )

