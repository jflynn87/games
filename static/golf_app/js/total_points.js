$(document).ready(function () {
    fetch("/golf_app/season_points/"  + $('#season_id').text() + '/all')
    .then(response=> response.json())
    .then((responseJSON) => {
         points = $.parseJSON(responseJSON)
         console.log(points)
         $.each(points, function(player,data) {
             console.log(player, data.fed_ex_score)
             $('#weekly_total_' + player).text(data.t_scores)
             $('#fedex_' + player).text(data.fed_ex_score)
             $('#total_' + player).text(data.total)
             $('#rank_' + player).text(data.rank)
         })
        //  points_l = points.length
        //  console.log(points_l, points.length)
        //  for (let i=0; i< points_l; i++) {
        //      console.log('key ', Objects.keys(points[i]))
        //      $('#fedex_' + Objects.keys(points[i])).text(points[i].score)
        //  }
    })

}
)
