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
    console.log(' skipping updating scores')
    // $.ajax({
    //   type: "GET",
    //   url: "/golf_app/get_scores/",
    //   data: {'tournament' : $('#tournament_key').text()},
    //   dataType: 'json',
    //   success: function (json_update) {
    //     console.log('updated scores', typeof(json_update), $.isEmptyObject(json_update))
        
          
    //console.log(responseJSON)
    //console.log(start, new Date())
     // }
    //})
  })
})
