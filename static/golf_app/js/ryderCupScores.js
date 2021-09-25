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

          for (let i=0; i < picks_l; i++) {
              if (Object.keys(picks)[i] != 'score_dict') {
              $('#score_tbl_body').append('<tr id=' + Object.keys(picks)[i] + '-row><td>' + Object.keys(picks)[i] + '</td></tr>' )
              $('#' + Object.keys(picks)[i] + '-row').append('<td id=score' +  Object.keys(picks)[i] + ' style=font-weight:bold>' + Object.values(picks)[i].total_score  + '</td>')
              $('#' + Object.keys(picks)[i] + '-row').append('<td>' + Object.values(picks)[i].c_pick + ' / ' + Object.values(picks)[i].c_points + '</td>')
              $('#' + Object.keys(picks)[i] + '-row').append('<td>' +  '<img src=' + Object.values(picks)[i].pic_1 + ' style="max-height:50px;"></img><img src=' + Object.values(picks)[i].flag_1 + ' style="max-height:25px;"></img>' +Object.values(picks)[i].group_1 + '<p style=font-weight:bold;>' + Object.values(picks)[i].score_1 + ' </p></td>')
              $('#' + Object.keys(picks)[i] + '-row').append('<td>' + '<img src=' + Object.values(picks)[i].pic_2 + ' style="max-height:50px;"></img><img src=' + Object.values(picks)[i].flag_2 + ' style="max-height:25px;"></img>' +Object.values(picks)[i].group_2 + '<p style=font-weight:bold;>' + Object.values(picks)[i].score_2 + ' </p></td>')
              $('#' + Object.keys(picks)[i] + '-row').append('<td>' + '<img src=' + Object.values(picks)[i].pic_3 + ' style="max-height:50px;"></img><img src=' + Object.values(picks)[i].flag_3 + ' style="max-height:25px;"></img>' +Object.values(picks)[i].group_3 + '<p style=font-weight:bold;>' + Object.values(picks)[i].score_3 + ' </p></td>')
              $('#' + Object.keys(picks)[i] + '-row').append('<td>' + '<img src=' + Object.values(picks)[i].pic_4 + ' style="max-height:50px;"></img><img src=' + Object.values(picks)[i].flag_4 + ' style="max-height:25px;"></img>' +Object.values(picks)[i].group_4 + '<p style=font-weight:bold;>' + Object.values(picks)[i].score_4 + ' </p></td>')
              $('#' + Object.keys(picks)[i] + '-row').append('<td>' + '<img src=' + Object.values(picks)[i].pic_5 + ' style="max-height:50px;"></img><img src=' + Object.values(picks)[i].flag_5 + ' style="max-height:25px;"></img>' +Object.values(picks)[i].group_5 + '<p style=font-weight:bold;>' + Object.values(picks)[i].score_5 + ' </p></td>')
              $('#' + Object.keys(picks)[i] + '-row').append('<td>' + '<img src=' + Object.values(picks)[i].pic_6 + ' style="max-height:50px;"></img><img src=' + Object.values(picks)[i].flag_6 + ' style="max-height:25px;"></img>' +Object.values(picks)[i].group_6 + '<p style=font-weight:bold;>' + Object.values(picks)[i].score_6 + ' </p></td>')
          }
        }
          sort_table($('#score_table'), 1, 'asc')
          usa = picks.score_dict.overall.USA
          eur = picks.score_dict.overall.EUR
          console.log(usa)
            $('#overall_score').append('<img src=' + usa.flag + '><span class=left_ryder_cup_score>' + usa.score.displayValue + '</span></img>' +
                                        '<span class=middle_ryder_cup_score></span>'  +
                                        '<span class=right_ryder_cup_score>' + eur.score.displayValue + '</span><img src=' + eur.flag + '></img>')
        $('#loading').hide()
         // create_detail(picks.score_dict)
    })
})

function sort_table(table, cell_i, order) {
    
    const tRows = Array.from(table[0].rows)
    //console.log(tRows.length)
    tRows.sort( ( x, y) => {
       // console.log(x.cells[cell_i].innerHTML, x.cells[cell_i].innerHTML.length)
        if (x.cells[cell_i].innerHTML != '' && x.cells[cell_i].innerHTML != 'n/a') {
        var xValue = x.cells[cell_i].innerHTML;}
        else {var xValue = '999'}

        if (y.cells[cell_i].innerHTML != '' && y.cells[cell_i].innerHTML != 'n/a') {
        var yValue = y.cells[cell_i].innerHTML; }
        else {var yValue = '999'}
        
       // console.log(xValue, yValue)

        const xNum = parseInt( xValue );
        const yNum = parseInt( yValue );
        var ascending = true
        if (order != 'asc') {var ascending = false}
        return ascending ? ( xNum - yNum ) : ( yNum - xNum );
    })
        
    for( let row of tRows ) {
        table[0].appendChild( row );

    }

}

function create_detail(score_dict) {
    $('#detail_table').append('<h3>Score Details</h3>')
    $('#detail_table').append('<br>')
    frag = document.createDocumentFragment(); 
    table = document.createElement('table')
    table.classList.add('table')
    thead = document.createElement('thead')
        th_a = document.createElement('th')
        th_a.innerHTML = "Golfer"
        th_b = document.createElement('th')
        th_b.innerHTML = 'Friday Foursomes'
        th_c = document.createElement('th')
        th_c.innerHTML = 'Friday Fourballs'
        th_d = document.createElement('th')
        th_d.innerHTML = 'Saturday Foursomes'
        th_e = document.createElement('th')
        th_e.innerHTML = 'Saturday Fourballs'
        th_f = document.createElement('th')
        th_f.innerHTML = 'Singles'
    thead.appendChild(th_a)
    thead.appendChild(th_b)
    thead.appendChild(th_c)
    thead.appendChild(th_d)
    thead.appendChild(th_e)
    thead.appendChild(th_f)
    table.appendChild(thead)
    
    l = Object.keys(score_dict).length
    console.log(l)
    
    
    frag.appendChild(table)

    
    
    
    document.getElementById('detail_table').appendChild(frag)  

    




}