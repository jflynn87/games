$(document).ready (function() { 
  add_seasons()
  update_all('all')

})

function update_all(season) {

  
  weekly_winner(season)
  events_played(season)
  picked_winner(season)
  avg_points(season)
  avg_cuts(season)
  most_picked(season) 
  
}

  
function events_played(season) {
  fetch('/golf_app/total_played_api/' + season)
  .then((response) => response.json())
  .then((responseJSON) => {
  played = $.parseJSON(responseJSON)
  $.each(played, function(player, count) {
    $('#played_' + player).text(count.played)
  })
  $('#played_status').html('<i class="fas fa-check"></i>').css('color', 'green')
  show_hide_rows(played)  //kind of a hack but do it here as it is fast/early loading.
  
})

}

function weekly_winner(season) {
  $('#t_wins_status').text('loading...').css('color', 'black')
  fetch('/golf_app/t_wins_api/' + season)
  .then((response) => response.json())
  .then((responseJSON) => {
  wins = $.parseJSON(responseJSON)
  if (wins.error) {
      $('#msg').append('<p class=alert-danger>Error caclulating Tournament Wins: ' + wins.error.msg + '<p>')
    
  }
  else {
  $.each(wins, function(player, count) {
    $('#t_wins_' + player).text(count.weekly_winner)
  })
  }
  $('#t_wins_status').html('<i class="fas fa-check"></i>').css('color', 'green')
})

}

function picked_winner(season) {
  $('#winner_picked_status').text('loading...').css('color', 'black')
  fetch('/golf_app/picked_winner_count_api/' + season)
  .then((response) => response.json())
  .then((responseJSON) => {
  wins = $.parseJSON(responseJSON)
  if (wins.error) {
      $('#msg').append('<p class=alert-danger>Error caclulating Picked Winners: ' + wins.error.msg + '<p>')
    
  }
  else {
  $.each(wins, function(player, count) {
    $('#winner_picked_' + player).text(count.winner_count)
  })
  }
  $('#winner_picked_status').html('<i class="fas fa-check"></i>').css('color', 'green')
})
}

function avg_points(season) {
  $('#avg_points_status').text('loading...').css('color', 'black')
  fetch('/golf_app/avg_points_api/' + season)
  .then((response) => response.json())
  .then((responseJSON) => {
  wins = $.parseJSON(responseJSON)
  if (wins.error) {
      $('#msg').append('<p class=alert-danger>Error caclulating Average Points: ' + wins.error.msg + '<p>')
    
  }
  else {
  $.each(wins, function(player, avg) {
    $('#avg_points_' + player).text(avg.average)
  })
  }
  $('#avg_points_status').html('<i class="fas fa-check"></i>').css('color', 'green')
})
}

function avg_cuts(season) {
  $('#avg_cuts_status').text('loading...').css('color', 'black')
  fetch('/golf_app/avg_cuts_api/' + season)
  .then((response) => response.json())
  .then((responseJSON) => {
  cuts = $.parseJSON(responseJSON)
  if (cuts.error) {
      $('#msg').append('<p class=alert-danger>Error caclulating Average Cuts: ' + cuts.error.msg + '<p>')
    
  }
  else {
  $.each(cuts, function(player, avg) {
    $('#avg_cuts_' + player).text(avg.average_cuts)
  })
  }
  $('#avg_cuts_status').html('<i class="fas fa-check"></i>').css('color', 'green')
})
}


function most_picked(season) {
  $('#most_frequent_status').text('loading...').css('color', 'black')
  fetch('/golf_app/most_picked_api/' + season)
  .then((response) => response.json())
  .then((responseJSON) => {
  most = $.parseJSON(responseJSON)
  if (most.error) {
      $('#msg').append('<p class=alert-danger>Error caclulating Most Picked: ' + most.error.msg + '<p>')
    
  }
  else {
  $.each(most, function(player, data) {
    $('#most_picked_' + player).text(data.most_picked_golfer + ' : ' + data.times_picked + ' times')
  })
  }
  $('#most_frequent_status').html('<i class="fas fa-check"></i>').css('color', 'green')
})

}

function add_seasons() {
  $('#year_stats select').on('change', function() {
    console.log('click caught', $('#year_stats select').val())
    $('#stats_body td').html('...')
    update_all($('#year_stats select').val())
  })
}

function show_hide_rows(played)  {
  $('#stats_body tr').hide()
  $.each(played, function(user, data) {
    $('#' + user + '_stats_row').show()

  })
}