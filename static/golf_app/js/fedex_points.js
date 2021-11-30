$(document).ready(function () {
    fetch("/golf_app/season_points/"  + $('#season_id').text() + '/all')
    .then(response=> response.json())
    .then((responseJSON) => {
         points = responseJSON
         console.log(points)
         $.each(points, function(player,score) {
             console.log(player, score.score)
             $('#fedex_' + player).text(score.score)
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
