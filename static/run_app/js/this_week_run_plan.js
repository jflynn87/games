//$(document).ready(function () {
function thisWeekRunPlan() {
    var start = new Date()
    console.log('THIS WEEK')
    fetch("/run_app/this_week_run_plan_api",
    {method: "GET",
    })
.then((response) => response.json())
.then((responseJSON) => {
    data = $.parseJSON(responseJSON)
    console.log(data)
    if (data.error) {$('#this_week_run_plan').append("<h3>ERROR: " + data.error + "</h3>")
                        }
    else {
        $('#this_week_run_plan').append('<table id=this_week_plan_table class=table></table>')
        $('#this_week_plan_table').append('<tr><th>ending</th><th>M</th><th>T</th><th>W</th><th>T</th><th>F</th><th>S</th><th>S</th></tr>')
        $('#this_week_plan_table').append('<tr id=plan_row></tr>')
        $('#plan_row').append('<td>' + data[data.length-1].fields.date + '</td>')
        $.each(data, function(i, d) {
            console.log(d.fields.run)
            if (d.fields.run == null) {$('#plan_row').append('<td>' + d.fields.dist + '</td>')}
            else {$('#plan_row').append('<td style=color:green;font-weight:bold;>' + d.fields.dist + '</td>')}


        })

        }
    })
}

