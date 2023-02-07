//bad copy, rewrite it all

function score_view() {
    start = new Date()
    //fetch('/golf_app/season_points/' + $('#season_key').text() + '/all')
    Promise.all([
        fetch('/golf_app/season_points/' + $('#season_key').text() + '/all').then(response=>response.json()),
        //fetch('/golf_app/fedex_picks_api/' + $('#fedex_season_key').text() + '/all').then(response=>response.json()),
        fetch('/golf_app/fedex_picks_by_score/' + $('#fedex_season_key').text()).then(response=>response.json()),
        fetch('/golf_app/fedex_detail_api/' + $('#fedex_season_key').text()).then(response=>response.json()),
        
    ])
    //.then(response=> response.json())
    .then((responseJSON) => {
        total_points = $.parseJSON(responseJSON[0])
        //picks = responseJSON[1]
        summary = responseJSON[1]
        by_golfer = responseJSON[2]
        //console.log('points', total_points)
        //console.log('picks', picks)
        //console.log('summary: ', summary)
        //console.log('golfer dtl: ', by_golfer)

        buildSummary(summary, total_points)
        byGolfer(by_golfer)
    //     const score_frag = new DocumentFragment()

    //     score_tbl = document.createElement('table')
    //     score_tbl.classList.add('table', 'table-sm', 'table-bordered', 'table-stripped')
    //     score_tbl.id = 'score_tbl'
    //     header = document.createElement('thead')
        
    //     th0 = document.createElement('th')
    //     th0.innerHTML = 'Player'
    //     th0a = document.createElement('th')
    //     th0a.innerHTML = 'Total Points'
    //     th0c = document.createElement('th')
    //     th0c.innerHTML = 'Top 3'
        
    //     th0b = document.createElement('th')
    //     th0b.innerHTML = '-80 point picks'
    //     th1 = document.createElement('th')
    //     th1.innerHTML = '-30 point picks'
    //     th2 = document.createElement('th')
    //     th2.innerHTML = '+20 point picks '
    //     th3 = document.createElement('th')
    //     th3.innerHTML = '0 point picks '

    //     header.appendChild(th0)
    //     header.appendChild(th0a)
    //     header.appendChild(th0c)
    //     header.appendChild(th0b)
    //     header.appendChild(th1)
    //     header.appendChild(th2)
    //     header.appendChild(th3)

    //     score_tbl.appendChild(header)
    //     score_frag.appendChild(score_tbl)

    //     user_l = Object.keys(total_points).length
        
    //     for (let i=0; i < user_l; i++) {
    //         var row = document.createElement('tr')
    //         row.id = 'user_' + Object.keys(total_points)[i]
    //         row.classList.add('small')
    //         userCell = document.createElement('th')
    //         userCell.innerHTML = Object.keys(total_points)[i]
    //         pointsCell = document.createElement('td')
    //         pointsCell.innerHTML = Object.values(total_points)[i].fed_ex_score
    //         row.appendChild(userCell)
    //         row.appendChild(pointsCell)
    //         score_tbl.appendChild(row)    

    //     }
    //     document.getElementById('scores').appendChild(score_frag)
        
    //     $.each(picks, function(user, pick_data) {
    //         top3 = document.createElement('td')
    //         cell80 = document.createElement('td')
    //         cell30 = document.createElement('td')
    //         cell20 = document.createElement('td')
    //         cell0 = document.createElement('td')
            
    //         $.each(pick_data, function(id, pick){
               
    //             if (pick.score == -80) {
    //                 if (cell80.innerHTML == '') {
    //                     cell80.append(pick.golfer_name)
    //                 }
    //                 else {cell80.append(', ' + pick.golfer_name)}
    //             }
    //             else if (pick.score == -30) {
    //                 if (cell30.innerHTML == '') {
    //                 cell30.append(pick.golfer_name)}
    //                 else {cell30.append(', ' + pick.golfer_name)}
    //             }   
    //             else if (pick.score == 20) {
    //                 if (cell20.innerHTML == '') {
    //                     cell20.append(pick.golfer_name)
    //                 }
    //                 else
    //                     {cell20.append(', ' + pick.golfer_name)}
    //             }
    //             else if (pick.score == 0) {
    //                 if (cell0.innerHTML == '') {
    //                     cell0.append(pick.golfer_name)
    //                 }
    //                 else {cell0.append(', ' + pick.golfer_name)}
                    
    //             }
    //             if (pick.top_3) {
    //                // if (top3.innerHTML == '') {
    //                     t_3_p = document.createElement('p')
    //                     t_3_p.innerHTML = pick.golfer_name
    //                     top3.append(t_3_p)
    //                // }
    //                // else
    //                //     {top3.append(', ' + pick.golfer_name)}
                    
    //             }
    //         })
            
    //         document.getElementById('user_' + user).appendChild(top3)
    //         document.getElementById('user_' + user).appendChild(cell80)
    //         document.getElementById('user_' + user).appendChild(cell30)
    //         document.getElementById('user_' + user).appendChild(cell20)
    //         document.getElementById('user_' + user).appendChild(cell0)
    //     })
        
        
    //     sort_table($('#score_tbl'), 2, 'dsc')
    //     $('#status').attr('hidden', true)
    //     $('#scores').attr('hidden', false)
    //     finish = new Date()
    //     console.log('duration: ', finish - start)
     })

}
rowFields = {'fedex_points': 'FedEx Points', 'Rank': 'Rank',
'in_top30': 'In Top 30', 'outside_top30': 'Outside Top 30',
'minus_80': '-80 Picks', 'plus_20': '+20 Picks', 'at_risk': 'At Risk',
'onthe_verge': 'On the Verge', 'top_70': 'Still Hope',
'into_top30': 'Into Top 30', 'out_of_top_30': 'Out of Top 30'}

function buildSummary(data, totals) {
    console.log('SUMMARY', data)
    $('#summary').append('<h3>FedEx Summary Data</h3>')
    $('#summary').append('<table id=summary_table class=table></table>')
    $('#summary_table').append('<tr id=summary_table_header><td></td></tr>')
    players = Object.keys(data)
    // rowFields = {'fedex_points': 'FedEx Points', 'Rank': 'Rank',
    // 'in_top30': 'In Top 30', 'outside_top30': 'Outside Top 30',
    // 'minus_80': '-80 Picks', 'plus_20': '+20 Picks', 'at_risk': 'At Risk',
    // 'onthe_verge': 'On the Verge', 'top_70': 'Still Hope',
    // 'into_top30': 'Into Top 30', 'out_of_top_30': 'Out of Top 30'}
    
    $.each(players, function(i, player){$('#summary_table_header').append('<th>' + player + '</th>')})
    
    
    $.each(rowFields, function(key, value) {
        $('#summary_table').append('<tr id=' + key + '_row><th>' + key + '</th></tr>')
        $.each(players, function(i, player) {
            if (data[player][key] != undefined)
            {$('#' + key + '_row').append('<td id=' + key + player + '_data>' + data[player][key]+ '</td>')}
        })
    })

}

    

    $('#summary').attr('hidden', false)

function byGolfer(data) {
    console.log('byGolfer', data)
}