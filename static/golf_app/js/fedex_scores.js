function score_view() {
    start = new Date()
    rowFields = {'fed_ex_score': 'FedEx Points', 
    'in_top30': 'In Top 30', 'outside_top30': 'Outside Top 30',
    'minus_80': '-80 Picks', 'plus_20': '+20 Picks', 'at_risk': 'At Risk',
    'onthe_verge': 'On the Verge', 'top_70': 'Still Hope',
    'into_top30': 'Into Top 30', 'out_top30': 'Out of Top 30'}
    
    fetch('/golf_app/season_points/' + $('#season_key').text() + '/all')
    .then(response=>response.json())
    .then((responseJSON) => {
        total_points = $.parseJSON(responseJSON)
        init = initTable(rowFields, total_points)
        init.then((response => {
            picksSummary()
            inOut()
            updateRow('fed_ex_score', total_points)
        }))
       $('#fedex_picks_summary').attr('hidden', false)

    })
    
}

function loadStatus() {
    $('#status').append('<br>')
    $('#status').append('<h4>Data Load Status</h4>')
    $('#status').append('<table id=status_table class="table-sm table-bordered"><tr><th>Data</th><th>Status</th></tr></table>')
}


function initTable(rowFields, totals) {
    return new Promise(function(resolve, reject) {
    
    createStatusRow('total_score_status', 'Total Scores')
    $('#fedex_picks_summary').append('<br>')
    $('#fedex_picks_summary').append('<h3 style=background-color:lightblue;>FedEx Summary Data</h3>')
    $('#fedex_picks_summary').append('<table id=summary_table class="table table-bordered"></table>')
    $('#summary_table').append('<tr id=summary_table_header class=small><th style=position:sticky;top:0;left:0;background:lightgray;z-index:1;></th></tr>')
    t = sortUsers(totals)
            
    $.each(t, function(i, info){$('#summary_table_header').append('<th style=position:sticky;top:0;background:lightgray;>' + info.player + '</th>')})
        
    $.each(rowFields, function(key, value) {
        $('#summary_table').append('<tr id=' + key + '_row class=small><th style=position:sticky;left:0;background:white;>' + key + '</th></tr>')
        if (key != 'into_top30' && key != 'out_top30') {
        $.each(t, function(i, player) {
            {$('#' + key + '_row').append('<td id=' + key + player.player + '_data></td>')}
                                        })
        }
        else {$('#' + key + '_row').append('<td id=' + key  + '_data colspan=' + t.length +  '></td>')}
    })
    updateStatusRow('total_score_status')
    resolve()    
})
}

function createStatusRow(id, label) {
    $('#status_table').append('<tr id=summary_data_status><td>' + label + '</td><td id=' + id + '_td>loading<span class=status> ...</span></td></tr>')
    return
}

function updateStatusRow(id) {
    $('#' + id + '_td').html('<i class="fas fa-check"></i>').css('color', 'green')
    return
}

function sortUsers(totals) {
    t = Object.values(totals).sort((a,b ) => {if (parseInt(a.fed_ex_score) < parseInt(b.fed_ex_score)) {return -1}})
    return t
}


function updateRow(key, data) {
    $.each(data, function(player, stats) {
        $('#' + key + player + '_data').text(stats[key])
    })
}

function picksSummary() {
    createStatusRow('summary_data_status', 'Summary Data')
    fetch('/golf_app/fedex_picks_by_score/' + $('#fedex_season_key').text())
    .then(response=>response.json())
    .then((responseJSON) => {
        data = responseJSON
        $.each(data, function(player, d) {
            $.each(d, function(k, v) {
                updateRow(k, data)
            })
        })
        updateStatusRow('summary_data_status')
        
    })
   
}

function detail() {
    createStatusRow('picks', 'Picks')
    Promise.all([
        fetch('/golf_app/season_points/' + $('#season_key').text() + '/all').then(response=>response.json()),
        fetch('/golf_app/fedex_detail_api/' + $('#fedex_season_key').text()).then(response=>response.json()),
    ])
    .then((responseJSON) => {
        data = responseJSON[1]
        totals = $.parseJSON(responseJSON[0])
        console.log('detail: ', data)
        t = sortUsers(totals)
        $('#fedex_detail').append('<table id=fedex_detail_table class="table table-bordered"></table>')
        $('#fedex_detail_table').append('<tr id=fedex_detail_header class=small  style=position:sticky;top:0;background:lightgray;z-index:1;><th></th>')
        $.each(t, function(i, u) {
            
            $('#fedex_detail_header').append('<th>' + u.player + '</th>')
        })
        
        $.each(data, function(golfer, d) {
            let filler = /[\s\.\,\']/g;
            g = golfer.replace(filler, '_')
            $('#fedex_detail_table').append('<tr id='+ g +'_row class=small style=font-weight:bold;><td style=position:sticky;left:0;background:white;>' + golfer + '</td></tr>')    
            $.each(t, function(i, user) {
                e = document.createElement('td')
                //eSpan = document.createElement('span')
                //eSpanP = document.createElement('p')
                //eSpan.classList.add('watermarkAll')
                //eSpanP.innerHTML = user.player
                //eSpan.appendChild(eSpanP)
                //e.appendChild(eSpan)
                eP = document.createElement('p')
                if (data[golfer].top_3.indexOf(user.player) != -1) {
                    eP.innerHTML = 'Top3'
                    if (d.rank == 1) {eP.style.color = 'green'}
                }
                else if (data[golfer].user_list.indexOf(user.player) != -1) {
                    eP.innerHTML = 'X'}
                else {
                        eP.innerHTML = ''}
                
                e.appendChild(eP)
                $('#' + g + '_row').append(e)
            })
        })
        $('#fedex_detail').attr('hidden', false)
        updateStatusRow('picks')
    })
}


function inOut() {
    fetch('/golf_app/fedex_in_out/')
    .then(response=>response.json())
    .then((responseJSON) => {
        data = responseJSON
        $.each(data, function(category, d) {
            $.each(d, function(golfer, info) {
                h = $('#' + category + '_data').html()
                $('#' + category + '_data').html(h + '<p>' + golfer + ' (' + info.rank + ')' + '</p>')
            })
        })
    })
}

