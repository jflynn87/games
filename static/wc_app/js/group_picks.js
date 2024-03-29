$(document).ready()
{const t = buildTable()
t.then((response) => {checkComplete()})}

function buildTable() {
    return new Promise(function (resolve,reject) {
    Promise.all([
        fetch('/wc_app/wc_group_stage_teams_api').then(response=>response.json()),
        fetch('/wc_app/wc_group_stage_picks_api').then(response=>response.json())
    ])
    //.then(response=> response.json())
    .then((responseJSON) => {
        var data = JSON.parse(responseJSON[0])
        var picks = JSON.parse(responseJSON[1])
        console.log('picks ', picks)
        
        var picksPerGrp = data.length / $('#pick_form table').length
        var options = ''
        for (g=0; g <= picksPerGrp; g++) {
            if (g == 0) {options = options + '<option value=' + g + '>--</option>'}
            else {options = options + '<option value=' + g + '>' + g + '</option>'}
        }
        $.each(data, function(i,d){
    
        $('#picks_table_' + d.fields.group).append('<tr id=' + d.pk + '_row></tr>')
        // $('#' + d.pk + '_row').append('<td style=width:10%;> <select name=' + d.pk + ' selected=0 id=sel_' + d.pk + ' class=pick_input>' +
        //                                     '<option value=0>--</option>' + 
        //                                     '<option value=1>1</option>' + 
        //                                     '<option value=2>2</option>' + 
        //                                     '<option value=3>3</option>' + 
        //                                     '<option value=4>4</option>' + 
        //                                 '</input> </td>')

        $('#' + d.pk + '_row').append('<td style=width:10%;> <select name=' + d.pk + ' selected=0 id=sel_' + d.pk + ' class=pick_input>' +
                                             options + 
                                         '</input> </td>')


        $('#' + d.pk + '_row').append('<td style=width:30%> <a href=' + d.fields.info_link + '> <span><img src="' + d.fields.flag_link + '"></img></span>' + d.fields.full_name + '</a></td>' +
                                                        '<td>' + d.fields.rank + '</td>')
        //console.log('eventlistner group', d.fields.group)
        document.getElementById('sel_' + d.pk).addEventListener('change', function () {checkComplete(document.getElementById('picks_table_' + d.fields.group))})
       
        if (picks.length > 0) {
            var pick = picks.find(t => t.fields.team === d.pk)
            //$('#sel_' + d.pk + ' option[value=' + pick.fields.rank + ']').attr('selected', 'selected')
            $('#sel_' + d.pk).val(pick.fields.rank).attr('selected', 'selected')

        }
        fetch("/wc_app/wc_group_bonus_api/" + d.pk,         
            {method: "GET",
                })
        .then((response) => response.json())
        .then((responseJSON) => {
            bonus_data = responseJSON
            //console.log('group bonus: ', Object.keys(bonus_data), Object.values(bonus_data))
                $('#' + Object.keys(bonus_data) + '_row').append('<td>' + Object.values(bonus_data) + '</td>')
            
            })

    })
    console.log('resolving')
    resolve()    
 
    })
})

}

function checkComplete(table) {
    groups = parseInt($('#group_count').text())
    teamsPerGrp = parseInt($('#teams_per_group').text())
    teams = groups * teamsPerGrp 

    $('#sub_btn').attr('disabled', true)
    picks = $('.pick_input')
    var pickArray = []
    for (var i=0; i < picks.length; i++) {
        pickArray.push(picks[i].value)
            }
    
    fns = []
            
    for (var i=0; i < groups; i++) {
        fns.push(checkGroup($('.table')[i], teamsPerGrp))
    }

    groupStatus = Promise.all(fns)
    groupStatus.then((response) => {console.log('VV ', response);
                                    if (response.indexOf(false) != -1) {
                                        $('#sub_btn').attr('disabled', true)

                                    }
                                    else {
                                        $('#sub_btn').attr('disabled', false)
                                        }
                                    })

    //for (i=0; i <= $('.table').length; i++) {
    //    var status  = checkGroup($('.table')[i], teamsPerGrp)
    //    console.log('status ', status)
    //    status.then((response) => {console.log('resp: ', response); grpArray.push(response)})
    //    }      
    //    console.log('grparray: ', grpArray)

    
    // one = pickArray.filter(i => i === '1').length
    // two = pickArray.filter(i => i === '2').length
    // three = pickArray.filter(i => i === '3').length
    // four = pickArray.filter(i => i === '4').length
    
    // if (one == 8 && two == 8 && three == 8 && four == 8){
    //     tables = document.getElementsByTagName('table')
    //     groupArray = []
        
    //     for (var t=0; t< tables.length; t++) {
    //         groupArray.push(checkGroups(tables[t]))}
    //     //console.log(groupArray)
    //     //console.log(groupArray.indexOf(false))
    //     if (groupArray.indexOf(false) != -1){
    //         $('#sub_btn').attr('disabled', true)
    //         }
    //     else {
    //         $('#sub_btn').attr('disabled', false)
    //     }
    // }
    // else if (table != undefined){
    // checkGroups(table)
    //             }
}



function checkGroup(table, pickCnt) {
    return new Promise(function(resolve, reject) {
        picks = table.getElementsByClassName('pick_input')
        var pickArray = []
        for (var i=0; i < picks.length; i++) {
            pickArray.push(picks[i].value)
                }
            for (var j=1; j <= pickCnt; j++) {
                if (pickArray.indexOf(j.toString()) == -1) {
                    console.log('grpChek resolving')
                    resolve(false)
                    if (pickArray.indexOf('0') == -1) {
                        $('#' + table.id.split('_')[2] + '_status').html('- Error - Check Picks')
                        $('#' + table.id.split('_')[2] + '_status').css('background-color', 'red')
                    }
                    return
                }
            //only here if picks good
            $('#' + table.id.split('_')[2] + '_status').html(' - Picks Good')
            $('#' + table.id.split('_')[2] + '_status').css('background-color', 'blue')

            resolve(true)     
            }
    })

}

// function checkGroups(table){
//     rows = table.rows

//     pickArray = []
//     //var one = 0 
//     //var two = 0 
//     //var three = 0 
//     //var four = 0 
//     for (i=2; i < rows.length; i++) {
    
//         pickArray.push(rows[i].cells[0].children[0].value)
//              }

//     one = pickArray.filter(c => c === '1').length
//     two = pickArray.filter(c => c === '2').length
//     three = pickArray.filter(c => c === '3').length
//     four = pickArray.filter(c => c === '4').length
//     total = one + two + three + four
//     //console.log(table.id, one, two, three, four, total)
//     if (one === 1 && two === 1 && three === 1 && four === 1) {
//         $('#' + table.id.split('_')[2] + '_status').html(' - Picks Good')
//         $('#' + table.id.split('_')[2] + '_status').css('background-color', 'blue')
//         return true
//     }
//     else if (total == 0) {$('#' + table.id.split('_')[2] + '_status').html('- Make Picks')
//                             return false}
//     else if (total == 4) {$('#' + table.id.split('_')[2] + '_status').html('- Error - Check Picks')
//                           $('#' + table.id.split('_')[2] + '_status').css('background-color', 'red')
//                             return false}

// }


