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
                '<td>' + picks[0] + ' - ' + data[picks[0]] +'</td>' +
                '<td>' + picks[1] + ' - ' + data[picks[1]] +'</td>' +
                '<td>' + picks[2] + ' - ' + data[picks[2]] +'</td>' +
                '<td>' + picks[3] + ' - ' + data[picks[3]] +'</td>' +
                '<td>' + picks[4] + ' - ' + data[picks[4]] +'</td>' +
                '<td></td>' +
                '<td></td>' +
            '</tr>'
        )

    })
    sort_table()
    $('#status').text('Scores Updated').removeClass('status')
    
    })
})

$(document).ready(function() {
    $('#picks_sect').append(
        '<table id=score_table class=table>' +
        '<thead style=background-color:lightblue;> <th> Player </th>' +
        '<th> Score 1</th>' +
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
console.log(table)
switching = true;

while(switching) {
  switching = false;
  rows = table.rows;
  console.log(rows.length)

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
