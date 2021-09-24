$(document).ready(function() {
    fetch("/golf_app/ryder_cup_score_api/", 
    {method: "GET",
    }
          )
    .then((response) => response.json())
    .then((responseJSON) => {
          picks = responseJSON
          console.log(picks)

          picks_l = Object.keys(picks).length
          console.log([picks_l])
          for (let i=0; i < picks_l; i++) {
              console.log(Object.keys(picks)[i])
              $('#score_tbl_body').append('<tr id=' + Object.keys(picks)[i] + '-row><td>' + Object.keys(picks)[i] + '</td></tr>' )
              $('#' + Object.keys(picks)[i] + '-row').append('<td>' + Object.values(picks)[i].c_pick + ' / ' + Object.values(picks)[i].c_points + '</td>')
              $('#' + Object.keys(picks)[i] + '-row').append('<td>' + Object.values(picks)[i].group_1 + '</td>')
              $('#' + Object.keys(picks)[i] + '-row').append('<td>' + Object.values(picks)[i].group_2 + '</td>')
              $('#' + Object.keys(picks)[i] + '-row').append('<td>' + Object.values(picks)[i].group_3 + '</td>')
              $('#' + Object.keys(picks)[i] + '-row').append('<td>' + Object.values(picks)[i].group_4 + '</td>')
              $('#' + Object.keys(picks)[i] + '-row').append('<td>' + Object.values(picks)[i].group_5 + '</td>')
              $('#' + Object.keys(picks)[i] + '-row').append('<td>' + Object.values(picks)[i].group_6 + '</td>')
          }


    }
)
})