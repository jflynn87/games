
$(document).ready(function() {
fetch("/golf_app/get_picks_summary/" + $('#tournament_key').text(),
  
{method: "GET",
})
.then((response) => response.json())
.then((responseJSON) => {
picks_data = responseJSON
console.log('picks data: ', picks_data)
$('#picks_info').append('<p> Total Golfers Picked: ' + picks_data.total_picks.playerName__count + '  <i id="picks_toggle" class="fa fa-plus-circle" style="color:lightblue;">View Pick Counts</i> </p')
$('#picks_toggle').on('click', function() {togglePicks($(this))})
$('#picks_info').append('<div id=picks_counts hidden><table id=picks_summary_table class="table table-borderless table-sm"></table></div>')
$('#picks_summary_table').append('<tr class=small><th>Picks</th></tr>')

$.each(picks_data.by_player, function(player, count) {
    if ($('#picks_summary_row' + count).length === 0) {
        $('#picks_summary_table').append('<tr id=picks_summary_row' + count +' class=small> <td style=font-weight:bold;>' + count + ' </td> <td>' + player + '</td></tr>')
        }
    else {
         $('#picks_summary_row' + count).append('<td>' + player + '</td>')
    }
})
})

})

function togglePicks(ele) {
    console.log('toggle', ele.text())
    if (ele.text()  == 'View Pick Counts') {
        ele.text('Hide Pick Counts')
        ele.attr('class', 'fa fa-minus-circle')
        $('#picks_counts').removeAttr('hidden')
    }
    else if (ele.text()  == 'Hide Pick Counts') {
        ele.text('View Pick Counts')
        ele.attr('class', 'fa fa-plus-circle') 
        $('#picks_counts').attr('hidden', '')
    }


}