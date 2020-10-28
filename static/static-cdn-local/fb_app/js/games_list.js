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
  console.log(team_name)
  var game_list = {}
  games = document.getElementById('game_tbl')

  for (var j = 1; j <= games.rows.length; j++){
      game_list[$.trim($('#fav'+j).text().split("(")[0].toUpperCase())] = 'game'+j
      game_list[$.trim($('#dog'+j).text().split("(")[0].toUpperCase())] = 'game'+j

        }
        console.log(game_list)
  return game_list[team_name]
};


    $(document).on('change', $("select[id^='id_form_']"), function () {
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
});

function validate() {
  $('#pick_form').attr('onsubmit','return true')
  picks = document.getElementById('pickstbl')
  var pick_list = []
  for (p=1; p <= picks.rows.length; p++) {
    if (document.getElementById('pick' + (17-p)).children[0].value == '') {
        console.log('pick' + (17-p))
        var missing_picks = true
        break}
      }
    if (missing_picks){
        alert('Missing Picks, please select one team per game')
        $('#pick_form').attr('onsubmit','return false');
}

};

$('#week4').on('change', function () {
  console.log('week change')
  $.ajax({
    type: "GET",
    url: "/golf_app/ajax/ajax_get_games/",
    dataType: 'json',
    //context: document.body
    success: function (json) {
      var i;
      for (i = 0; i < json.length; ++i) {
          $('#' + json[i]).attr('checked', 'checked');
        }
    },
    failure: function(json) {
      console.log('fail');
      console.log(json);
    }
  })

})

$(document).ready(function () {
  console.log('new ready')
  $.ajax({
    type: "GET",
    url: "/fb_app/ajax_get_spreads/",
    dataType: 'json',
    //context: document.body
    success: function (json) {
      console.log(json)
      console.log(json.length )
      for (i = 0; i < json.length; ++i) {

        console.log(json[i][0])
        row = $('tr[name=' + json[i][0] + ']')

        $('td', row).each(function () {

          if ($(this).prop('id').startsWith('spread')) {
            $(this).html(json[i][5])
          }
          else if ($(this).prop('id').startsWith('fav')) {
            $(this).html(json[i][1] +"<span class='record'>" + json[i][2] + "</span>")
            
          }
          else if ($(this).prop('id').startsWith('dog')) {
            $(this).html(json[i][3] + "<span class='record'>" + json[i][4] + "</span>")

          }
        })

        

      }
      var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
      now = new Date()
      console.log(now)
      $('#status').text('spreads updated: ' + now).attr('class', 'updated-status')

    },
    failure: function(json) {
      console.log('fail');
      console.log(json);
    }
  })

})

$(window).resize(function() {
  console.log($(window).width())
  $('#picksect').attr('class', 'row')
})