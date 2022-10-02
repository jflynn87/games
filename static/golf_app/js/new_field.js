$(document).ready(function () {
    start = new Date()
    var t_key = $('#tournament_key').text()
    Promise.all([
    fetch("/golf_app/get_info/" + t_key).then(response => response.json()),
    fetch("/golf_app/get_field/" + t_key).then(response => response.json()),
    fetch("/golf_app/get_golfers_obj/" + t_key).then(response => response.json()),
    fetch("/golf_app/get_started_data/" + t_key).then(response => response.json()),
    fetch("/golf_app/field_get_picks/").then(response => response.json()),
    fetch("/golf_app/fedex_picks_api/" + $('#fedex_season_key').text() + '/' + 'by_user').then(response => response.json()),
    fetch("/golf_app/get_country_picks/" + $('#pga_t_num').text() + '/user').then(response => response.json()),  //warp in an if?         
       ])
    .then((responseJSON) => {
         info = $.parseJSON(responseJSON[0])
         f_data = $.parseJSON(responseJSON[1])
         field = $.parseJSON(f_data.field)
         groups = $.parseJSON(f_data.groups)
         g_data = $.parseJSON(responseJSON[2])
         golfers = g_data.golfers
         partners = g_data.partners
         s_data = $.parseJSON(responseJSON[3])
         //console.log(s_data)
         //g_links = $.parseJSON(responseJSON[4])
         startedGolfers = s_data.started_golfers
         tStarted = s_data.t_started
         allGolfersStarted = s_data.all_golfers_started
         latePicks = s_data.late_picks
         lockedGroups = s_data.lock_groups
         
         picksObjs = $.parseJSON(responseJSON[4])
         picks = []
         $.each(picksObjs, function(i, p) {
             picks.push(p.fields.playerName)
         })
         
         fedexPicks = responseJSON[5].data
         cpPicks = responseJSON[6]
         console.log('cp: ', cpPicks)

         if ($('#pga_t_num').text() == 468 || $('#pga_t_num').text() == 500) {
            buildHeader(cpPicks)
         }

         //console.log(info)
         //console.log(field)
         //console.log(groups)
         //console.log(tStarted)
         //console.log(startedGolfers)
         //console.log(fedexPicks)
         //console.log(picks)

         const build = buildForm(info, groups, field, golfers, partners, picks, tStarted, startedGolfers, lockedGroups, fedexPicks)
         build.then((response) => {
            $('#status').html('<h4>Ready for Picks</h4>');
            console.log('ready for picks; ', new Date() - start);

            $('#field_sect form').append('<div id=bottom_sect class=field_stats_display></div>')

            $('#bottom_sect').append(
            '<div id=bottom class=field_stats_display>' +
            '<div id=stats-dtl-toggle>' +
            '</div>' +
            
            '<div id=pick-status></div>' + 
            '<div id=grp_6_buttons class=grp_6_buttons>' + 
            //'<p id=jump_to style="background-color:lightgray; color:white; font-weight:bold;"> Jump to: ' +
            '</p>' +
            
            '</div>' +
            '<input id=sub_button type="submit" class="btn btn-secondary" value="Submit Picks" disabled>' 
            )
            
            $('#pick_form').on('submit', function(event){
                event.preventDefault();
                console.log("form submitted!")  
                create_post();
            });
            if (s_data['t_started'] == false)
                {$('#random_btn').attr('disabled', false)}

            $('#random_form').on('submit', function(event){
                event.preventDefault();
                console.log("form submitted!")  
                create_post_random();
            });
            validatePicks(info)
            console.log('done: ', new Date() - start)
            })
    })

})

function buildForm(info, groups, field, golfers, partners, picks, tStarted, startedGolfers, lockedGroups, fedexPicks) {
    return new Promise(function (resolve) {
        fieldLen = field.length

        for (let i=0; i < fieldLen; i++) {
            f = field[i]
            
            if (i==0 || f.fields.group != field[i-1].fields.group) {
                var group = groups.filter(grp => {
                    return grp.pk == Number(f.fields.group)})
                
                table_grp_num = group[0].fields.number
                frag = new DocumentFragment()
                table = document.createElement('table')
                table.id = 'tbl-group-' + table_grp_num 
                table.classList = ['table']
        
                header = document.createElement('thead')
                hRow = document.createElement('tr')
                hRow.classList = ['total_score']
                th = document.createElement('th')
                th.colSpan = 2
                th.innerHTML = 'Group ' + group[0].fields.number + ' - Pick ' + info[group[0].fields.number] + ' Golfers'
                span = document.createElement('span')
                spanP = document.createElement('p')
                spanP.innerHTML = 'Click anywhere on player info area to see stats'
                spanP.style.fontSize = 'smaller'
        
                span.append(spanP)
                th.append(span)
                hRow.append(th)
                header.append(hRow)
                table.append(header)
        
            }
            
            var group = groups.filter(g => {
                return g.pk == Number(f.fields.group)})
            
            numPicks = info[group[0].fields.number]
            if (numPicks == '1') {selectType = 'radio'}
            else {selectType = 'checkbox'}
            
            golferTr = document.createElement('tr')
            golferTr.id = 'golfer-' + f.pk
            golferTr.classList = ['border rounded border-2']

            inputTd = document.createElement('td')
            inputTd.id = 'input-' + f.pk
            inputTd.width = '2%'
            //inputTd.style.borderRight = 'thinnest dashed gray'

            csrfP = document.createElement('p')
            csrfI = document.createElement('input')
            csrfI.type = 'hidden'
            csrfI.name = "csrfmiddlewaretoken"
            csrfI.value = $.cookie('csrftoken')
                
            selectP = document.createElement('p')
            selectI = document.createElement('input')
            selectI.type = selectType
            selectI.id = f.pk
            selectI.style.cssFloat  = 'right'
            selectI.classList = ['my-checkbox form-check-input']
            selectI.name = 'group-' + group[0].fields.number  //can i make the group not an array?
            selectI.value = f.pk
            if (picks.indexOf(f.pk) != -1) {
                selectI.checked = true
            }
            selectI.addEventListener('change', function() {validatePicks(info, this)})


            var golfer = golfers.filter(g => {
                return g.id == Number(f.fields.golfer)})

            if (f.fields.withdrawn == true) {
                  
                    selectMsg = document.createElement('p')
                    selectMsg.innerHTML = "WD"
                    inputTd.style.backgroundColor = 'lightgray'
                    selectP.append(selectMsg)
                    selectI.disabled = true
                    }
    
            else if (startedGolfers.indexOf(golfer[0].espn_number) != -1) {
                  
                selectMsg = document.createElement('p')
                selectMsg.innerHTML = "Started"
                inputTd.style.backgroundColor = 'lightgray'
                selectP.append(selectMsg)
                selectI.disabled = true
                }
            
            else if (lockedGroups.indexOf(f.fields.group) != -1) {
                selectMsg = document.createElement('p')
                selectMsg.innerHTML = "Locked"
                inputTd.style.backgroundColor = 'lightgray'
                selectP.append(selectMsg)
                selectI.disabled = true

            }
    

            golferTd = document.createElement('td')
            golferTd.id = 'playerInfo' + golfer[0].espn_number
            golferTd.addEventListener('click', function() {getStatsData(this.parentNode)})
            
            golferP1 = document.createElement('p')

            if (fedexPicks.indexOf(golfer[0].id) != -1) {
                fedex = document.createElement('img')
                fedex.src = '/static/img/fedex.jpg'
                fedex.style.width = '30px'
                //fedex.style.border='1px solid lightblue';
                golferP1.appendChild(fedex)
        
            }
            golferPic = document.createElement('img')
            golferName = document.createElement('span')
            golferFlag = document.createElement('img')
            
            golferPic.src = golfer[0].pic_link
            
            
            if (f.fields.partner) {
                golferName.innerHTML = f.fields.playerName + '(' + (Number(f.fields.currentWGR) - Number(f.fields.partner_owgr)).toString() + ')'
            }
            else {golferName.innerHTML = f.fields.playerName}
            golferName.style.fontWeight = 'bold'

            golferFlag.src = golfer[0].flag_link

            golferP1.append(golferPic)
            golferP1.append(golferName)
            golferP1.append(golferFlag)

            if (f.fields.partner) {
                p = document.createElement('span')
                
                var partner = partners.filter(p => {
                    return p.id == f.fields.partner_golfer})
                if (fedexPicks.indexOf(partner[0].id) != -1) {
                    p_fedex = document.createElement('img')
                    p_fedex.src = '/static/img/fedex.jpg'
                    p_fedex.style.width = '30px'
                    p.appendChild(fedex)
                    }
                p_golferPic = document.createElement('img')
                p_golferName = document.createElement('span')
                p_golferFlag = document.createElement('img')
                
                p_golferPic.src = partner[0].pic_link
                
                p_golferName.innerHTML = partner[0].golfer_name + '('+ f.fields.partner_owgr + ')'
                p_golferName.style.fontWeight = 'bold'
    
                p_golferFlag.src = partner[0].flag_link
                p.append(' & ')
                p.append(p_golferPic)
                p.append(p_golferName)
                p.append(p_golferFlag)
                golferP1.append(p)      
        
                }


            golferTd.append(golferP1)

            golferP2 = document.createElement('p')
            google = document.createElement('a')
            google.href = "https://www.google.com/search?q=" + f.fields.playerName
            google.target="_blank"
            google.innerHTML = "Google"
            espn = document.createElement('a')
            espn.href = golfer[0].espn_link
            espn.target="_blank"
            espn.innerHTML = "/ESPN"
            pga = document.createElement('a')
            pga.href = golfer[0].pga_link
            pga.target="_blank"
            pga.innerHTML = "/PGA"
            expand = document.createElement('i')
            expand.id = 'expand-' + f.pk
            expand.classList = ['fa fa-plus-circle expand']
            expand.style.float = 'right'
            expand.innerHTML = "Show Golfer Stats"

            golferP2.appendChild(google)
            golferP2.appendChild(espn)
            golferP2.appendChild(pga)
            golferP2.appendChild(expand)
            golferTd.append(golferP2)

            golferP3 = document.createElement('p')
            if (f.fields.season_stats.fed_ex_rank != 'n/a') {
                fedexTotals = f.fields.season_stats.fed_ex_rank + '/' + f.fields.season_stats.fed_ex_points}
            else {fedexTotals = 'n/a'}

            golferP3.innerHTML = 'OWGR: ' + f.fields.currentWGR + '; Handicap: ' + f.fields.handi +
                                 '; FedEx: ' + fedexTotals + '; Prior Year: ' + f.fields.prior_year
            golferP3.style.fontWeight = 'bold'
            
            golferTd.append(golferP3)
            
            selectP.append(selectI)
            csrfP.append(csrfI)
            inputTd.append(csrfP)
            inputTd.append(selectP)
            golferTr.append(inputTd)
            golferTr.append(golferTd)
            table.append(golferTr)

            statsRow = document.createElement('tr')
            statsRow.id = 'stats_row-' + f.pk
            statsRow.classList = ['stats_row']
            statsRow.hidden = true
            statsRow.colSpan = '2'
            statsTd1 = document.createElement('td')
            statsTd1.innerHTML = 'Loading Data...'
            statsRow.append(statsTd1)

            table.append(statsRow)


            frag.appendChild(table)
            document.getElementById('pick_form').appendChild(frag)
                
        }

        
        resolve()
    }) 
}

function getStatsData(ele) {
    golfer_id = ele.cells[1].id.replace('playerInfo', '')
    field_id = ele.id.replace('golfer-', '')
    return new Promise(function (resolve) {
    row = document.getElementById('stats_row-' + field_id)
    console.log(row)
    td = row.getElementsByTagName('td')
    if (row.hidden == false) {
        document.getElementById('expand-' + field_id).classList = ['fa fa-plus-circle expand']
        document.getElementById('expand-' + field_id).innerHTML = 'Show Golfer Stats'
        row.hidden = true
                              }
    else {
        document.getElementById('expand-' + field_id).classList = ['fa fa-minus-circle expand']
        document.getElementById('expand-' + field_id).innerHTML = 'Hide Golfer Stats'
        row.hidden = false
    
    if (td.length ==1) {
      fetch("/golf_app/get_prior_result/",         
      {method: "POST",
      headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': $.cookie('csrftoken')
              },
      body: JSON.stringify({'tournament_key': $('#tournament_key').text(),
                          'golfer_list': [golfer_id],
                          'group': '',
                          'no_api': true})
    })
    .then((response) => response.json())
    .then((responseJSON) => {
      data = responseJSON
      var stats = build_stats_row(data[0])
          
      row.deleteCell(0)
      row.appendChild(stats)
    
      })
      .then(resolve())
                    }
  else {
        row.hidden = false
        resolve()}
    }
     }) 
  }
  

function build_stats_row(field) {
    console.log(field)
    let stats_row = document.createElement('tr');
    stats_row.id = 'stats_row-' + field.id
    stats_row.style.width = 100%
    stats_row.classList.add('stats_row')
    stats_row.setAttribute('hidden', true)
    stats_cell = document.createElement('td')
    stats_cell.colSpan = 2
    stats_cell.classList = ['adj_font_size']
    stats_row.appendChild(stats_cell)
    let stats_table = document.createElement('table');
        stats_table.style.width = '85%'
        stats_table.classList.add('table',  'stats-row')

        let rowA_header_fields = ['Current OWGR', 'Last Week OWGR', 'Last Season OWGR', 'FedEx Cup']
        rowA_field_l = rowA_header_fields.length
        rowA_header = document.createElement('tr')
        rowA_header_cells = []
        for (let i=0; i < rowA_field_l; i++ ) {
            let header_field = document.createElement('th')
                header_field.innerHTML = rowA_header_fields[i]
                header_field.colSpan = 2
                rowA_header_cells.push(header_field)
        }
        for (let i=0; i < rowA_field_l; i++) {
            rowA_header.append(rowA_header_cells[i])
        }
        rowA_header.classList.add('stats_row')
        stats_table.appendChild(rowA_header)
            
        let stats_rowA = document.createElement('tr')
            
            currOWGR = document.createElement('td')
            currOWGR.innerHTML = field.currentWGR
            currOWGR.colSpan = 2
            sowOWGR = document.createElement('td')
            sowOWGR.innerHTML = field.sow_WGR
            sowOWGR.colSpan = 2
            soyOWGR = document.createElement('td')
            soyOWGR.innerHTML = field.soy_WGR
            soyOWGR.colSpan = 2
            fedEx = document.createElement('td')
            fedEx.innerHTML = 'rank: ' + field.season_stats.fed_ex_rank + '; points:' + field.season_stats.fed_ex_points
            fedEx.colSpan = 2

            stats_rowA.append(currOWGR)
            stats_rowA.append(sowOWGR)
            stats_rowA.append(soyOWGR)
            stats_rowA.append(fedEx)
        stats_table.appendChild(stats_rowA)
            

        let stats_rowB = document.createElement('tr')
        let rowB_header_fields = ['Handicap', 'This event last year', 'Recent Form']

        rowB_field_l = rowB_header_fields.length
        rowB_header = document.createElement('tr')
        rowB_header_cells = []
        for (let i=0; i < rowB_field_l; i++ ) {
            let header_field = document.createElement('th')
                header_field.innerHTML = rowB_header_fields[i]
                if (i+1 == rowB_field_l) {header_field.colSpan = 4}
                else {header_field.colSpan = 2}
                rowB_header_cells.push(header_field)
        }
        for (let i=0; i < rowB_field_l; i++) {
            rowB_header.append(rowB_header_cells[i])
        }
        rowB_header.classList.add('stats_row')

        handicap = document.createElement('td')
        handicap.innerHTML = field.handi
        handicap.colSpan = 2
        prior_year = document.createElement('td')
        prior_year.innerHTML = field.prior_year
        prior_year.colSpan = 2
        
        recent_form = document.createElement('td')
        recent_form.id = 'recent' + field.golfer.espn_number
        recent_form.colSpan = 4
        
        recent_p = document.createElement('p')
        var ranks = ''
        var items = ''
        rec_l = Object.keys(field.recent).length
        for (let i=0; i < rec_l; i++) {
            var r = Object.values(field.recent)[i]
            if (i+1 < rec_l) {ranks += r.rank + ', '} 
            else {ranks += r.rank + ' '}
            items += r.name + ': ' + r.rank + '\n'
            }
        
        recent_p.innerHTML = ranks
        recent_form.appendChild(recent_p)

        recent_span = document.createElement('span')
        recent_a = document.createElement('a')
        recent_circle = document.createElement('i')
        
        recent_a.id = 'tt-recent' + field.id
        recent_a.setAttribute('data-toggle', 'tooltip')
        recent_a.setAttribute('title', items)
        
        recent_circle.classList.add('fa', 'fa-info-circle')
        recent_circle.style.color = 'blue'
       
        recent_span.appendChild(recent_a)
        recent_a.appendChild(recent_circle)

        recent_p.appendChild(recent_span)       

        stats_rowB.append(handicap)
        stats_rowB.append(prior_year)
        stats_rowB.append(recent_form)

        stats_table.appendChild(rowB_header)        
        stats_table.appendChild(stats_rowB)

        let stats_rowC = document.createElement('tr')
            let cell = document.createElement('th')
            cell.innerHTML = 'Season Stats'
            cell.colSpan = 8
            cell.classList.add('stats_row')
        stats_rowC.appendChild(cell)
        stats_table.appendChild(stats_rowC)

        let rowD_header = document.createElement('tr')
        rowD_header_fields = ['Played', 'Won', '2-10', '11-29', '30-49', '50', 'Cuts']

        rowD_field_l = rowD_header_fields.length
        
        rowD_header_cells = []
        for (let i=0; i < rowD_field_l; i++ ) {
            let header_field = document.createElement('th')
                header_field.innerHTML = rowD_header_fields[i]
                if (i+1 == rowD_field_l) {header_field.colSpan = 2}
                else {header_field.colSpan = 1}
                rowD_header_cells.push(header_field)
        }
        for (let i=0; i < rowD_field_l; i++) {
            rowD_header.append(rowD_header_cells[i])
        }

        let stats_rowD = document.createElement('tr')
            let cellA = document.createElement('td')
                cellA.colSpan = 1
                cellA.innerHTML = field.season_stats.played
                stats_rowD.appendChild(cellA)
            let cellB = document.createElement('td')
                cellB.colSpan = 1
                cellB.innerHTML = field.season_stats.won
                stats_rowD.appendChild(cellB)
            let cellC = document.createElement('td')
                cellC.colSpan = 1
                cellC.innerHTML = field.season_stats.top10
                stats_rowD.appendChild(cellC)
            let cellD = document.createElement('td')
                cellD.colSpan = 1
                cellD.innerHTML = field.season_stats.bet11_29
                stats_rowD.appendChild(cellD)
            let cellE = document.createElement('td')
                cellE.colSpan = 1
                cellE.innerHTML = field.season_stats.bet30_49
                stats_rowD.appendChild(cellE)
            let cellF = document.createElement('td')
                cellF.colSpan = 1
                cellF.innerHTML = field.season_stats.over50
                stats_rowD.appendChild(cellF)
            let cellG = document.createElement('td')
                cellG.colSpan = 1
                cellG.innerHTML = field.season_stats.cuts
                stats_rowD.appendChild(cellG)
            
            stats_table.appendChild(rowD_header)
            stats_table.appendChild(stats_rowD)

            let sg_row = document.createElement('tr')
            let sg_cell = document.createElement('th')
            sg_cell.innerHTML = 'Shots Gained Stats'
            sg_cell.colSpan = 8
            sg_cell.classList.add('stats_row')
        sg_row.appendChild(sg_cell)
        stats_table.appendChild(sg_row)


            let rowE_header = document.createElement('tr')
            rowE_header_fields = ['Off Tee Rank', 'Off Tee', 'Approach Rank', 'Approach', 'Around Green Rank', 'Around Green', 'Putting Rank', 'Putting']

            rowE_field_l = rowE_header_fields.length
            
            rowE_header_cells = []
            for (let i=0; i < rowE_field_l; i++ ) {
                let header_field = document.createElement('th')
                    header_field.innerHTML = rowE_header_fields[i]
                    rowE_header_cells.push(header_field)
            }
            for (let i=0; i < rowE_field_l; i++) {
                rowE_header.append(rowE_header_cells[i])
            }
            
            let stats_rowE = document.createElement('tr')

            if (field.season_stats.off_tee === undefined) {
                let sg_cellA = document.createElement('td')
                sg_cellA.innerHTML = "No STATS"
                stats_rowE.appendChild(sg_cellA) }
            else {
                let sg_cellA = document.createElement('td')
                    sg_cellA.innerHTML = field.season_stats.off_tee.rank
                    stats_rowE.appendChild(sg_cellA)

                let sg_cellB = document.createElement('td')
                    sg_cellB.innerHTML = field.season_stats.off_tee.average
                    stats_rowE.appendChild(sg_cellB)

                let sg_cellC = document.createElement('td')
                    sg_cellC.innerHTML = field.season_stats.approach_green.rank
                    stats_rowE.appendChild(sg_cellC)

                let sg_cellD = document.createElement('td')
                    sg_cellD.innerHTML = field.season_stats.approach_green.average 
                    stats_rowE.appendChild(sg_cellD)

                let sg_cellE = document.createElement('td')
                    sg_cellE.innerHTML = field.season_stats.around_green.rank
                    stats_rowE.appendChild(sg_cellE)

                let sg_cellF = document.createElement('td')
                    sg_cellF.innerHTML = field.season_stats.around_green.average
                    stats_rowE.appendChild(sg_cellF)

                let sg_cellG = document.createElement('td')
                    try {
                    sg_cellG.innerHTML = field.season_stats.putting.rank } 
                    catch {sg_cellG.innerHTML = 'error'}
                    stats_rowE.appendChild(sg_cellG)

                let sg_cellH = document.createElement('td')
                    try {
                        sg_cellH.innerHTML = field.season_stats.putting.average}
                    catch {sg_cellH.innerHTML = '0'}
                    stats_rowE.appendChild(sg_cellH)
       
            }

            stats_table.appendChild(rowE_header)
            stats_table.appendChild(stats_rowE)
            
        stats_cell.append(stats_table)

        return stats_cell
}

function validatePicks(info, ele) {
    if (typeof(info) == 'string') {var info = $.parseJSON(info)}

    if (ele) {
      group = ele.name.split('-')[1]
      if (parseInt(info)) {picks = info}
      else {picks = info[ele.name.split('-')[1]]}

      if($("#tbl-group-" + group + ' input:checked').length > parseInt(picks)) {
        ele.checked = false;
        alert (picks.toString() + ' picks already selected.  Deselect a pick first to change your picks')
                  }
}
  $('#pick-status').empty()
  checkComplete(info)
  
}


function checkComplete(info) {

    $('#pick-status').empty()
    $('#pick-status').append('<table id=status-tbl class="table table-sm"> </table>')
    $('#status-tbl').append('<tr id=picks-row> <td> Groups: </td> </tr>')
    $.each(info,  function(group, picks) {
       $('#picks-row').append('<td id=status-group' + group + '> <a href=#tbl-group-' + group + '>' + group + '</a> </td>')
    })  
       $('#status-tbl').append('<tr id=required-row> <td> Picks required: </td> </tr>')
       $.each(info,  function(group, picks) {
          $('#required-row').append('<td id=required-group'+ group + '>' + picks + '</td>')
   })
   $('#status-tbl').append('<tr id=actual-row> <td> Total Picks: </td> </tr>')
   $.each(info,  function(group, picks) {
     //console.log('a ', group, picks, count_actual(group, picks))
     if (group != "complete") {
      $('#actual-row').append('<td id=actual-group'+ group + '>' + count_actual(group, picks) + '</td>')
     }
  })
  var total = 0
  $("#actual-row").each(function () {
      $('td', this).slice(1,-1).each(function (i) {
        if ($(this).text() != info[i+1]) {
          $(this).css('background-color', '#FFF300')
        }
  
        total += parseInt(($(this).text()))
  
        $('#actual-grouptotal').text(total)
  
        var countries_ok = true
        if ($('#pga_t_num').text() == '999') {
          var picks = {}
          //console.log(countries_ok)
          picks['m' + $('#men_1_country').val()] = true
          picks['m' + $('#men_2_country').val()] = true
          picks['m' + $('#men_3_country').val()] = true
          picks['w' + $('#women_1_country').val()] = true
          picks['w' + $('#women_2_country').val()] = true
          picks['w' + $('#women_3_country').val()] = true
          if (Object.keys(picks).length == 6) {countries_ok = true}
          else {countries_ok = false}
        }
  
        if ($('#pga_t_num').text() == 468 || $('#pga_t_num').text() == 500) {var ryder_ok = false}
        else {var ryder_ok = true}
  
        if ($('#pga_t_num').text() == '468' || $('#pga_t_num').text() == '500') {
          console.log('complete chk ', $('#winning_points').val())
          if ($('#winning_team').val() && parseFloat($('#winning_points').val()) > 14) {
              ryder_ok = true
          }
        else {ryder_o = false}
     //   console.log(ryder_o)
        }
  
        //console.log(Object.keys(picks).length, countries_ok)
        //if (total == parseInt(info['total']) && countries_ok == true && ryder_ok == true) {
        //console.log('all started data ', allGolfersStarted)
        //console.log('lat picks ', latePicks)
        if (total == parseInt(info['total']) && countries_ok == true && ryder_ok == true && (! allGolfersStarted == true  || latePicks == true)) {
          $('#sub_button').removeAttr('disabled').attr('class', 'btn btn-primary').val('Submit Picks');
          $('#actual-grouptotal').css('background-color', '')  
          $('#required-groupcomplete').text('True')
        }
        else 
        {$('#sub_button').prop('disabled', true).attr('class', 'btn btn-secondary').val(total + ' of ' + info.total + ' picks');
        $('#actual-grouptotal').css('background-color', '#FFF300')}
        })
    
  })
  }
  
  function count_actual(group, picks) {
        var selected = $('input[name=group-' + group + ']:checked').length
        return selected
  }
  

  function create_post() {
      console.log('creating post')
    toggle_submitting()    
    checked = $('input:checked')
    pick_list = []
    men_countries = []
    women_countries = []
    men_countries.push($('#men_1_country').val(), $('#men_2_country').val(), $('#men_3_country').val())
    women_countries.push($('#women_1_country').val(), $('#women_2_country').val(), $('#women_3_country').val())
    ryder_cup = []
    ryder_cup.push($('#winning_team').val(), $('#winning_points').val())
    $.each(checked, function(i, pick){
        pick_list.push(pick.value)
    })

    console.log(pick_list)
    fetch("/golf_app/new_field_list/",         
    {method: "POST",
     headers: {
     'Accept': 'application/json',
     'Content-Type': 'application/json',
     'X-CSRFToken': $.cookie('csrftoken')
             },
     body: JSON.stringify({'key': $('#tournament_key').text(),
                            'pick_list': pick_list, 
                            'men_countries': men_countries,
                            'women_countries': women_countries,
                            'ryder_cup': ryder_cup
                             })
 })
    .then((response) => response.json())
    .then((responseJSON) => {
     d = responseJSON
     if (d.status == 1) {
         window.location = d.url
     }
     else {
         console.log(d.message)
         $('#error_msg').text(d.message).addClass('alert alert-danger')
         clear_submitting()
         window.scrollTo(0,0);
     }
     console.log(d)

 })
}

function create_post_random() {
    toggle_submitting()
    pick_list = []
    pick_list.push('random', )
    console.log('pick list', pick_list)
    fetch("/golf_app/new_field_list/",         
    {method: "POST",
     headers: {
     'Accept': 'application/json',
     'Content-Type': 'application/json',
     'X-CSRFToken': $.cookie('csrftoken')
             },
     body: JSON.stringify({'key': $('#tournament_key').text(),
                            'pick_list': pick_list, 
                             })
 })
    .then((response) => response.json())
    .then((responseJSON) => {
     d = responseJSON
     if (d.status == 1) {
         window.location = d.url
     }
     else {
         console.log(d.message)
         $('#error_msg').text(d.message).addClass('alert alert-danger')
         clear_submitting()
         window.scrollTo(0,0);
     }
     console.log(d)

 })
}


function toggle_submitting() {
    $('#sub_button').prop('disabled', 'true')
    $('#sub_button').prop('value', 'Submitting....')
    $('#random_btn').prop('disabled', 'true')
    $('#random_btn').prop('value', 'Submitting....')
    $('#top_sect').append('<p class=status style="text-align:center;"> Submitting picks, one moment....')
    $('#bottom').append('<p class=status style="text-align:center;"> Submitting picks, one moment....')

}


function clear_submitting() {
    $('#sub_button').removeAttr('disabled').attr('class', 'btn btn-primary')
    $('#sub_button').prop('value', 'Submit Picks')
    $('#random_btn').removeAttr('disabled').attr('class', 'btn btn-primary')
    $('#random_btn').prop('value', 'Random')
    $('.status').empty()

}


function buildHeader(cpPicks) {
    var eventName = $('#t-name').text()
        
    if ($('#pga_t_num').text() == 468) {
        var intl = "Europe"
        var low_points = 14
        var high_points = 28
    }
    else {
        var intl = "International"
        var lowPoints = 15
        var highPoints = 30

    }

    if ($('#pga_t_num').text() == 468 || $('#pga_t_num').text() == 500) {
            var instructions = '<p style=font-weight:bold;>Instructions:</p><p>One Pick per Group</p> <p>Match win -10 points, -1 point per hole of winning margin</p>' +
        '<p>Match loss +10 points, +1 point per hole of winning margin</p>' +
        '<p>Draw 0 points</p>' + 
        '<p>DNP +5 points (per session)</p>' + 
        '<p>Winning team -25 points</p>' +
        '<p>Closest to winning score -25.  Must pick winning team to qualify for this bonus.</p>' 
        if ($('#pga_t_num').text() == 468) {
            var tie = '<p>To bet on a 14/14 tie, choose 14 point and the prior ryder cup winning team as they keep the cup.</p>'
        }
        else {var tie = '<p>There is no winner in a tie for Presidents Cup, but you can choose 15 points if you think it will be a tie.</p>'
        
        }
        instructions = instructions + tie
    }
    else if ($('#pga_t_num').text() == 999) {
        var instructions = '<p>Olympics, build this</p>'
    }
    else {
        //var instructions = '<p>Enter 2 picks for group 1, and 1 pick for remaining groups</p>'
        var instructions = '<p>Something wrong, in Special Event header (new_field.js)</p>'
    }
    
    $('#top_sect').append('<div id=make_picks><br>' + instructions + '<br>' +
    '<form id="random_form" name="random_form" method="post">' +
    '<input type="hidden" name="csrfmiddlewaretoken" value=' + $.cookie('csrftoken') +  '>' +
    //'<input type="text" name="random" value="random" hidden>' +
    //'<h5 id=status>Loading Golfers, please wait for all to load <span class=status style="font-size:large;">...</span></h5> <br>' + 
    '<p id=random_line hidden>Click for random picks  <input id=random_btn type="submit" class="btn btn-secondary" value="Random" disabled></p>' +
    
    '</form>')

    $('#top_sect').append('<div id=too_late hidden><br> <p>Tournament Started, too late for picks</p></div>')

    // $('#top_sect').append('<span style="float: right;" >' + 
    //     '<a href="#" id="download_excel" >' +
    //     '<i class="fas fa-file-download" title="Download Excel" data-toggle="tooltip"> Download Excel</i>' +
    //     '</a>' +
    //     '</span>')


   // $('#field_sect').append('<form id=pick_form method=post></form>')

    if ($('#pga_t_num').text() == 999) {
        console.log('add countries here')
        //$('#field_sect #pick_form').append('<div id=mens_countries></div>')
        $('#field_sect #pick_form').append('<table id=mens_countries_picks' + " class=table> \
                                        <thead class=total_score> <th> Men's Medal Countries" + '</th> </thead>' +
                                        '</table>')
        $('#mens_countries_picks').append('<tr><td>Pick 3 countries, -50 for gold, -35 for silver, -20 for bronze.  Add +5 for each golfer above 1 per country.</td></tr>')
        
        $('#field_sect #pick_form').append('<table id=womens_countries_picks' + " class=table> \
                                        <thead class=total_score> <th> Women's Medal Countries" + '</th> </thead>' +
                                        '</table>')
        $('#womens_countries_picks').append('<tr><td>Pick 3 countries, -50 for gold, -35 for silver, -20 for bronze.  Add +5 for each golfer above 1 per country.</td></tr>')
        
        fetch("/golf_app/get_country_counts/",         
        {method: "GET",
        })
    .then((response) => response.json())
    .then((responseJSON) => {
        data = responseJSON
        console.log('countries: ', data)
        formatMenMedals(data)
        formatWomenMedals(data)
    })
    }

    //Ryder Cup
    if ($('#pga_t_num').text() == 468 | 500) {

        $('#field_sect #pick_form').append('<table id=ryderCup_picks' + " class=table> \
        <thead class=total_score> <th colspan=2>Special " + eventName +  " Picks " + '</th> </thead>' +
        '</table>')
        $('#ryderCup_picks').append('<p><label for=winning_team style=font-weight:bold>Choose Winning Team</label>' +  
             '<select id=winning_team class="form-control"><option></option><option value=euro>' + intl + '</option><option value-usa>USA</option> </select> </p>' + 
             '<p><label for=winning_points style=font-weight:bold>Enter winning team score, number between' + lowPoints + ' - ' + highPoints + '</label>' + 
             '<input id=winning_points class="form-control"  type=number placeholder="enter between ' + lowPoints + ' - ' + highPoints +'" step=0.5 min="' + lowPoints +  '"max="' + highPoints + '"><textbox></textbox></input></p>')
        
        if (cpPicks.length > 0) {
            console.log(cpPicks[0].ryder_cup_score)
            if (cpPicks[0].country == 'USA') {$('#winning_team').val('USA')}
            else {$('#winning_team').val('euro')}
            $('#winning_points').val(cpPicks[0].ryder_cup_score)
            
        }

        $('#winning_points').on('change', function() {
            
            if (parseFloat($('#winning_points').val()) % 1 == 0 || parseFloat($('#winning_points').val()) % 1 == 0.5)
                {
                    if (parseFloat($('#winning_points').val()) >= lowPoints && parseFloat($('#winning_points').val()) <= highPoints) 
                        {
                             $('#pick-status').empty()
                             checkComplete(info)
                        }
                    else {
                        $('#winning_points').val('')                        
                        $('#pick-status').empty()
                        checkComplete(info)
                        alert('Bad winning points entry: ' + $('#winning_points').val() + '. Please enter between ' + lowPoints +  ' and ' + highPoints)}
            
                }   
                else {
                       $('#winning_points').val('')                        
                       $('#pick-status').empty()
                       checkComplete(info)
                       alert ('Bad winning points value, must be a whole number or .5')}
            })

        $('#winning_team').change(function() {console.log('selected team '), winning_team;
                $('#pick-status').empty()                            
                checkComplete(info)})
        

        $('#random-line').remove()

        }
        
    
    $('#random_form').on('submit', function(event){
        event.preventDefault();
        console.log("random submitted!")  
        create_post_random();
    });
}

