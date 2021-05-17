$(window).on('load', function() {
    console.log('prior results start: ', new Date())
    tables = $('table')
    $.each(tables, function(i, table) {
      golfer_list = []
      if (table.rows.length < 12 && table.id.includes('group')) {$.each(table.rows, function(r, row) {golfer_list.push((row.id.replace('player', '')))})
          l = golfer_list.filter(function (e) {return e != '';})
          update_stats(l, table)
          season(l)}
      else if (table.rows.length > 12) {
        //dont need to skip the stats or pick summary tables as len is less than 12
        ids = []
        $.each(table.rows, function(r, row) {ids.push((row.id.replace('player', '')))})
        n = 50
        for (x=0; x < table.rows.length; x += n) {
          golfer_list.push(ids.slice(x, x+n))
          l = golfer_list[0].filter(function (e) {return e != '';})
          update_stats(l, table)
          //season(l)
          golfer_list = []
        }
        
      }
    })

})
      
function update_stats(golfer_list, table) {
        //console.log('b golfer list ', golfer_list)
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
               $.each(Object.values(data[0].recent), function(i, recent) {
               $('#main').append('<p id=t_' + i + ' hidden>' + recent.name)
              })
            }
             last_year(data)
             recent(data)
             season(data)
             //console.log('done: ', table.id, new Date())
    
})
}

function last_year(data) {
        $.each(data, function(key, stats) {
        //$('#prior' + stats.golfer.espn_number).text('prior: ' + stats.prior_year)
        $('#prior' + stats.golfer.espn_number).text(stats.prior_year)
    })
}

function recent(data) {
  
    $.each(data, function(i, stats) {
      //console.log(Object.keys(stats.recent).reduce())  
      ranks = ''
        $.each(stats.recent, function(i, rank){ranks += rank.rank + ', '})
        var items = ''
        $.each(stats.recent, function(i, rank){items += rank.name + ': ' + rank.rank + '\n'})
        
        $('#recent' + stats.golfer.espn_number).html('<p>' + ranks + '<span> <a id=tt-recent' + stats.golfer.espn_number + 
            ' data-toggle="tooltip" html="true" > <i class="fa fa-info-circle" style="color:blue"></i> </a> </span> </p>')
        $('#tt-recent' + stats.golfer.espn_number + '[data-toggle="tooltip"]').tooltip({trigger:"hover",
             delay:{"show":400,"hide":800}, "title": items
    })
      }) 

}

function season(data) {
  $.each(data, function(i, stats) {
    //console.log(stats.seaseon_statsplayed)
       $('#played' + stats.golfer.espn_number).text(stats.season_stats.played) 
       $('#won' + stats.golfer.espn_number).text(stats.season_stats.won) 
       $('#top10' + stats.golfer.espn_number).text(stats.season_stats.top10)
       $('#top30' + stats.golfer.espn_number).text(stats.season_stats.bet11_29)
       $('#top50' + stats.golfer.espn_number).text(stats.season_stats.bet30_49)
       $('#over50' + stats.golfer.espn_number).text(stats.season_stats.over50)
       $('#cut' + stats.golfer.espn_number).text(stats.season_stats.cuts)

})
}
// function season(golfer_list) {
//   //console.log('season stats list: ', golfer_list)
//   fetch("/golf_app/season_stats/",
//   {method: "POST",
//   headers: {
//     'Accept': 'application/json',
//     'Content-Type': 'application/json',
//     'X-CSRFToken': $.cookie('csrftoken')
//           },
//    body: JSON.stringify({'tournament_key': $('#tournament_key').text(), 
//                          'golfer_list': golfer_list})
//   })
//    .then((response) => response.json())
//  .then((responseJSON) => {
//    stats = responseJSON
//    $.each(stats, function(golfer, data) {
//     $('#played' + golfer).text(data.played) 
//     $('#won' + golfer).text(data.won) 
//     $('#top10' + golfer).text(data.top10) 
//     $('#top30' + golfer).text(data.bet11_29) 
//     $('#top50' + golfer).text(data.bet30_49)
//     $('#over50' + golfer).text(data.over50)
//     $('#cut' + golfer).text(data.cuts)   

//     //console.log(golfer, data)
//    })
   

// })

// }