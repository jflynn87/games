$(window).on('load', function() {
    console.log('start: ', new Date())
    tables = $('table')
    $.each(tables, function(i, table) {
      golfer_list = []
      if (table.rows.length < 12 && table.id != 'pick-status') {$.each(table.rows, function(r, row) {golfer_list.push((row.id.replace('player', '')))})
          update_stats(golfer_list.filter(function (e) {return e != '';}), table)}
      else if (table.rows.length > 12) {
        ids = []
        $.each(table.rows, function(r, row) {ids.push((row.id.replace('player', '')))})
        n = 50
        for (x=0; x < table.rows.length; x += n) {
          golfer_list.push(ids.slice(x, x+n))
          update_stats(golfer_list[0].filter(function (e) {return e != '';}), table)
          golfer_list = []
        }
        
      }
})
})
      
function update_stats(golfer_list, table) {

        fetch("/golf_app/get_prior_result/",         
        {method: "POST",
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-CSRFToken': $.cookie('csrftoken')
                },
         body: JSON.stringify({'tournament_key': $('#tournament_key').text(), 
                               'golfer_list': golfer_list})
        })
         .then((response) => response.json())
       .then((responseJSON) => {
             data = responseJSON
             if (table.id == 'tbl-group-1') {
               $('#main').append('<p id=t_1 hidden>' + Object.keys(data[0].recent)[0])
               $('#main').append('<p id=t_2 hidden>' + Object.keys(data[0].recent)[1])
               $('#main').append('<p id=t_3 hidden>' + Object.keys(data[0].recent)[2])
               $('#main').append('<p id=t_4 hidden>' + Object.keys(data[0].recent)[3])
              }
             last_year(data)
             recent(data)
             console.log('done: ', table.id, new Date())
    })
}


function last_year(data) {
        $.each(data, function(key, stats) {
        $('#prior' + stats.golfer.espn_number).text('prior: ' + stats.prior_year)
    })
}

function recent(data) {
    $.each(data, function(i, stats) {
      var items = ''
      $.each(stats.recent, function(t, rank){items += t + ': ' + rank + '\n'})
          $('#recent' + stats.golfer.espn_number).html('<p> recent form: ' + Object.values(stats.recent) + '<span > <a id=tt-recent' + stats.golfer.espn_number + 
            ' href="#" data-toggle="tooltip" html="true" > <i class="fa fa-info-circle"></i> </a> </span> </p>')
          $('#tt-recent' + stats.golfer.espn_number + '[data-toggle="tooltip"]').tooltip({trigger:"hover",
             delay:{"show":400,"hide":800}, "title": items
    })
      }) 

}

