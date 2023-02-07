//$(document).ready(function () {
function runPlanSummary () {
    var start = new Date()
    fetch("/run_app/get_run_plan_summary_api",
    {method: "GET",
    })
.then((response) => response.json())
.then((responseJSON) => {
    data = responseJSON
    console.log('summary: ', data)
    if (data.error) {$('#run_plan').append("<h3>ERROR: " + data.error + "</h3>")
                        }
    else {
        $('#run_plan_summary').append('<table id=run_plan_summary_table class=table></table>')
        $('#run_plan_summary_table').append('<tr><th>Plan Total</th><th>Plan to Date</th><th>Total to Date</th><th>% of runs</th><th>% of dist</th></tr>')
        $('#run_plan_summary_table').append('<tr><td>' + data.total_dist + '</td><td>' + data.expected_to_date + ' / ' +  data.expected_runs + '</td><td>' + 
            data.dist_to_date + ' / ' + data.total_runs +  '</td>' +
           '<td>' + data.runs_percent  + '</td><td>' + data.dist_percent + '</td></tr>')
    }
})
}
