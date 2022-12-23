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
        $('#run_plan_summary_table').append('<tr><th>Plan Total</th><th>Plan to Date</th><th>Total to Date</th></tr>')
        $('#run_plan_summary_table').append('<tr><td>' + data.total_dist + '</td><td>' + data.expected_to_date + '</td><td>' + data.dist_to_date + '</td></tr>')
    }
})
}
