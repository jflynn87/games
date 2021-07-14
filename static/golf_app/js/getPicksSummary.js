
$(document).ready(function() {
fetch("/golf_app/get_picks_summary/" + $('#tournament_key').text(),
  
{method: "GET",
})
.then((response) => response.json())
.then((responseJSON) => {
picks_data = responseJSON
console.log(picks_data)
$('#picks_info').append('<p> Total Golfers Picked: ' + picks_data.total_picks.playerName__count + '</p')
$.each()
})

})