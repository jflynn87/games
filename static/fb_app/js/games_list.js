function get_team_name(team_id) {
  var team_list=  {}
  teams = document.getElementById('teams')
  for (var i = 1; i <= teams.rows.length; i++) {
      team_list[document.getElementById('team_id'+i).innerHTML] =
      document.getElementById('team_nfl_abbr'+i).innerHTML;
    };

  return team_list[team_id]


};

function get_game_id(team_name) {
  //console.log(team_name)
  var game_list = {}
  games = document.getElementById('game_tbl')

  for (var j = 1; j <= games.rows.length; j++){
      game_list[$.trim($('#fav'+j).text().split("(")[0].toUpperCase())] = 'game'+j
      game_list[$.trim($('#dog'+j).text().split("(")[0].toUpperCase())] = 'game'+j

        }
        //console.log(game_list)
  return game_list[team_name]
};

$(document).ready(function () {
$('#pickstbl').on('change', $("select[id^='id_form_']"), function () {
mark_picks() })
//add if picks exist on load for highilgting 

})

function mark_picks() {
    //$(document).on('change', $("select[id^='id_form_']"), function () {
    //game = document.getElementById('game_tbl')
    game = document.getElementById('game_tbl')
    for (g=1; g<= game.rows.length; g++){
      document.getElementById('game' + g).style='none';


    }

    picks = document.getElementById('pickstbl')
    var pick_list = []
    for (p=1; p <= picks.rows.length; p++) {
       //pick_list.push(document.getElementById('pick' + (17-p)).children[0].value)
       pick_list.push($('#pick' + (17-p)).children().children("option").filter(":selected").text())
       
    }

    for (var k=0; k < pick_list.length; k++) {
        if (pick_list[k] != '---------') {
         //var pick = (pick_list[k]);
         var game_id = get_game_id(pick_list[k]);
         game = document.getElementById(game_id)
         game.style.background = 'yellow';

      }
}
};

function validate() {
  $('#pick_form').attr('onsubmit','return true')
  picks = document.getElementById('pickstbl')
  var pick_list = []
  for (p=1; p <= picks.rows.length; p++) {
    if (document.getElementById('pick' + (17-p)).children[0].value == '') {
        //console.log('pick' + (17-p))
        var missing_picks = true
        break}
      }
    if (missing_picks){
        alert('Missing Picks, please select one team per game')
        $('#pick_form').attr('onsubmit','return false');
}

};
//$("select[id^='week-list']").change(function () {
$(document).ready(function () {
$("#week-list").change(function () {
  console.log('caught click', $('#week-list').val())
  if ($('#week-list').val() != $('#week_key')) {
    console.log($(this).val())
    $('#status').text('changing week ....').attr('class', 'status')
    $('#favs').hide()
    $('#gamesect').hide()
    $('#picksect').hide()
    $(this).removeAttr('selected')
    location.href = $('#week-list').val() + '/'
  } 
})
})


$(document).ready(function () {
  console.log('get weeks') 
  //get_spreads()
    
  fetch("/fb_app/get_weeks/",
  {method: "GET",
  })
.then((response) =>  response.json())
.then((responseJSON) => {
      weeks = $.parseJSON(responseJSON)
      console.log(weeks)
      $.each(weeks, function(i) {
        console.log('week: ', weeks[i]['fields']['week'])
        if (weeks[i]['pk'] != $('#week_key').text()) {
          console.log(weeks[i]['pk'],  $('#week_key').text())
        //$('#week-list').append('<a href=/fb_app/games_list/' + weeks[i]['pk'] + '/'  +'> <button>' + weeks[i]['fields']['week'] + '</button> </a>') }
        $('#week-list').append('<option value=/fb_app/games_list/' + weeks[i]['pk'] + '>' + weeks[i]['fields']['week'] + '</option>') }

      }
      )
})
})
//commented on update to bootstrap 5.0
//$(window).resize(function() {
//  console.log($(window).width())
//  $('#picksect').attr('class', 'row')
//})
  
