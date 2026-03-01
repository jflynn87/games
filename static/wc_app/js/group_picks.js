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
        document.getElementById('sel_' + d.pk).addEventListener('change', function () {checkComplete()})
       
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

function checkComplete() {
    console.log('checking complete')
    $('#sub_btn').attr('disabled', true)
    
    var tables = $('table[id^="picks_table_"]')
    var fns = []
    
    tables.each(function() {
        var table = this
        var picks = $(table).find('.pick_input')
        var pickCount = picks.length
        fns.push(checkGroup(table, pickCount))
    })

    if (fns.length > 0) {
        Promise.all(fns).then((response) => {
            console.log('Group check results:', response)
            if (response.indexOf(false) == -1) {
                $('#sub_btn').attr('disabled', false)
            }
        })
    }
}



function checkGroup(table, pickCnt) {
    console.log('checking group ', table.id)
    return new Promise(function(resolve, reject) {
        var picks = table.getElementsByClassName('pick_input')
        var pickArray = []
        for (var i=0; i < picks.length; i++) {
            pickArray.push(picks[i].value)
        }
        
        // Check if all required picks (1 through pickCnt) are present exactly once
        for (var j=1; j <= pickCnt; j++) {
            if (pickArray.filter(p => p === j.toString()).length !== 1) {
                $('#' + table.id.split('_')[2] + '_status').html('- Error - Check Picks')
                $('#' + table.id.split('_')[2] + '_status').css('background-color', 'red')
                resolve(false)
                return
            }
        }
        
        // Only reach here if all picks are good
        $('#' + table.id.split('_')[2] + '_status').html(' - Picks Good')
        $('#' + table.id.split('_')[2] + '_status').css('background-color', 'blue')
        resolve(true)
    })
}
