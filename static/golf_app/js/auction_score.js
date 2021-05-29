$(document).ready(function () {
    fetch("/golf_app/auction_scores/",         
    {method: "GET",
    headers: {
    'Accept': 'application/json',
//    'Content-Type': 'application/json',
//    'X-CSRFToken': $.cookie('csrftoken')
            },
//    body: JSON.stringify({'tournament_key': $('#tournament_key').text(),
//                        'golfer_list': [],
 //                       'group': 'all'})
    })
    .then((response) => response.json())
    .then((responseJSON) => {
    scores = responseJSON
    console.log(scores)
    $.each(scores, function(player, data){
        picks = []
        $.each(Object.keys(data), function(i, golfer) {
            console.log(golfer)
            if (golfer != 'total') {
                picks.push(golfer)
            }
                    
        })

        console.log(picks)
        $('#score_table').append(
            '<tr>' +
                '<td>' + player + '</td>' +
                '<td id=' + player + 'total_score_cell class=total_score>' + data.total + '</td>' +
                '<td> <p class=small>' + picks[0] + '</p> <p class=small>rank: ' + data[picks[0]][0] +' score: ' + data[picks[0]][1] + '</p></td>' +
                '<td> <p class=small>' + picks[1] + '</p> <p class=small>rank: ' + data[picks[1]][0] +' score: ' + data[picks[1]][1] + '</p></td>' +
                '<td> <p class=small>' + picks[2] + '</p> <p class=small>rank: ' + data[picks[2]][0] +' score: ' + data[picks[2]][1] + '</p></td>' +
                '<td> <p class=small>' + picks[3] + '</p> <p class=small>rank: ' + data[picks[3]][0] +' score: ' + data[picks[3]][1] + '</p></td>' +
                '<td> <p class=small>' + picks[4] + '</p> <p class=small>rank: ' + data[picks[4]][0] +' score: ' + data[picks[4]][1] + '</p></td>' +
            '</tr>'
        )

    })
    sort_table()
    $('#status').text('Scores Updated').removeClass('status')
    
    })
})

$(document).ready(function() {
    $('#picks_sect').append(
        '<table id=score_table class="table table-bordered border-primary">' +
        '<thead style=background-color:lightblue;> <th> Player </th>' +
        '<th> Score</th>' +
        '<th> Pick 1</th>' +
        '<th> Pick 2</th>' +
        '<th> Pick 3</th>' +
        '<th> Pick 4</th>' +
        '<th> Pick 5</th>' +
        '</thead>' +
        '</table>'
    )
})



function sort_table(info) {
var table, rows, swtiching, i, x, y, shouldSwitch;
table = $('#score_table')[0]
//console.log(table)
switching = true;

while(switching) {
  switching = false;
  rows = table.rows;
  //console.log(rows.length)

  for (i=1; i < (rows.length - 1); i++) {
  //for (i=1; i < (rows.length); i++) {
    //console.log('for loop', i, rows[i].getElementsByClassName('total_score')[0])
    shouldSwitch = false;
    x = rows[i].getElementsByClassName('total_score')[0].innerHTML
    y = rows[i + 1].getElementsByClassName('total_score')[0].innerHTML
    //console.log(x, y)
    
    if (Number(x) > Number(y)) {
      //console.log(i, Number(x), Number(y))
      shouldSwitch = true;
      break;
    }
  }
    if (shouldSwitch) {
      rows[i].parentNode.insertBefore(rows[i+1], rows[i]);
      switching = true;
    }
  }
}
