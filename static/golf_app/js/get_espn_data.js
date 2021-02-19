$(document).ready(function() {
    //$('#det-list').attr('class', 'spinner')
    //$('#totals-table').hide()
    start = new Date() 
    console.log(start.toLocaleString())
//    $('#local').text.toLocaleString()
//    $('#status').append(start.toLocaleString())
    fetch("/golf_app/get_espn_score_dict/" + $('#tournament_key').text(),
    {method: "GET",
    })
  .then((response) => response.json())
  .then((responseJSON) => {
    console.log(responseJSON)
    console.log(start, new Date())
  })
})
