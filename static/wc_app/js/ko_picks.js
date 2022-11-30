$(document).ready(function() {
       fetch("/wc_app/wc_ko_bracket_api",         
         {method: "GET",
         })
         .then((response) => response.json())
         .then((responseJSON) => {
                data = responseJSON
                console.log('games: ', data)
                
                picks = JSON.parse(data.picks)
                
                //picks = data.picks
                console.log('picks: ', picks)

                var matches = createMatches(data)
                matches.then(initPicks(picks, data))

            //     $.each(data, function(match_num, teams) {
                    
            //         $('#m' + match_num.split('_')[1] + '_fav').text(teams.fav + '(' + teams.fav_fifa_rank + ')')
            //         .append('<img id=m' + match_num.split('_')[1] + '_fav_flag style=height:20;width:20; src=' + teams.fav_flag + '>')
            //         .attr('data-key', teams.fav_pk)
                    
            //         $('#m' + match_num.split('_')[1] + '_fav').on('click', function() {teamPicked(this)})
                    
            //         $('#m' + match_num.split('_')[1] + '_dog').text(teams.dog + '(' + teams.dog_fifa_rank + ')')
            //         .append('<img id=m' + match_num.split('_')[1] + '_dog_flag style=height:20;width:20; src=' + teams.dog_flag + '>')
            //         .attr('data-key', teams.dog_pk)
                    
            //         $('#m' + match_num.split('_')[1] + '_dog').on('click', function() {teamPicked(this)})
            //     })
                
            })

        })

function createMatches(data) {
    return new Promise(function (resolve,reject) {
        $.each(data, function(match_num, teams) {
                    
            $('#m' + match_num.split('_')[1] + '_fav').text(teams.fav + '(' + teams.fav_fifa_rank + ')')
            .append('<img id=m' + match_num.split('_')[1] + '_fav_flag style=height:20;width:20; src=' + teams.fav_flag + '>')
            .attr('data-key', teams.fav_pk)
            
            $('#m' + match_num.split('_')[1] + '_fav').on('click', function() {teamPicked(this)})
            
            $('#m' + match_num.split('_')[1] + '_dog').text(teams.dog + '(' + teams.dog_fifa_rank + ')')
            .append('<img id=m' + match_num.split('_')[1] + '_dog_flag style=height:20;width:20; src=' + teams.dog_flag + '>')
            .attr('data-key', teams.dog_pk)
            
            $('#m' + match_num.split('_')[1] + '_dog').on('click', function() {teamPicked(this)})
        })
        resolve()        
    })
   
}

function initPicks(picks, data) {
    $.each(picks, function(i, pick) {
        //console.log('init pick ', pick.fields.data.from_ele , $('#' + pick.fields.data.from_ele)[0])
        //teamPicked($('#' + pick.fields.data.from_ele))
        $('#' + pick.fields.data.from_ele).trigger('click')
    })
}




function teamPicked(ele) {
    //console.log('teamPicked', ele.id)
    var path = findPath(ele)
    var matchId = ele.id.split('_')[0].substring(1)
    var i = path.indexOf(parseInt(matchId))
    
    //console.log('click ', matchId, i)
    if (i == -1) {
        console.log(' -1 error')
    }
    else if (i == 0 || i == 1) {
       // console.log('AA')

            if (i %2 == 0) {
                $('#m' + path[i+2]  + '_fav').text($('#' + ele.id).text())
                .attr('data-key', $('#' + ele.id).attr('data-key'))
                .append('<img id=m' + path[i+2] + '_fav_flag style=height:20;width:20; src=' + $('#' + ele.id + '_flag').attr('src') + '>')
                .append('<input type=hidden value=' + $('#' + ele.id).attr('data-key') +' name=' + ele.id + '></>')}
            else {$('#m' + path[i+1] + '_dog').text($('#' + ele.id).text())
                .attr('data-key', $('#' + ele.id).attr('data-key'))
                .append('<img id=m' + path[i+1] + '_dog_flag style=height:20;width:20; src=' + $('#' + ele.id + '_flag').attr('src') + '>')
                .append('<input type=hidden value=' + $('#' + ele.id).attr('data-key') +' name=' + ele.id + '></>')}
    }
    else if (i ==2) {
        //console.log('22', matchId, ele.id, $('#' + ele.id).attr('data-key'))
        if (path[i]%2 == 0) {
            $('#m' + path[i+1]  + '_dog').text($('#' + ele.id).text())
            .attr('data-key', $('#' + ele.id).attr('data-key'))
            .append('<img id=m' + path[i+1] + '_dog_flag style=height:20;width:20; src=' + $('#' + ele.id + '_flag').attr('src') + '>')
            .append('<input type=hidden value=' + $('#' + ele.id).attr('data-key') +' name=' + ele.id +'></>')}
        else {
            $('#m' + path[i+1]  + '_fav').text($('#' + ele.id).text())
            .attr('data-key', $('#' + ele.id).attr('data-key'))
            .append('<img id=m' + path[i+1] + '_fav_flag style=height:20;width:20; src=' + $('#' + ele.id + '_flag').attr('src') + '>')
            .append('<input type=hidden value=' + $('#' + ele.id).attr('data-key') +' name=' + ele.id +'></>')}
    }
    else if (matchId == 13) {
          //  console.log('match 13')
            //champioship team
            $('#m' + path[i+1]  + '_fav').text($('#' + ele.id).text())
            .attr('data-key', $('#' + ele.id).attr('data-key'))
            .append('<img id=m' + path[i+1] + '_fav_flag style=height:20;width:20; src=' + $('#' + ele.id + '_flag').attr('src') + '>')
            .append('<input type=hidden value=' + $('#' + ele.id).attr('data-key')  +' name=' + ele.id +'></>')
            //consolsaion game team
            if (ele.id.split('_')[1] == 'dog' && $('#m13_fav').text() != '') {
                $('#m16_fav').text($('#m13_fav').text())
                .attr('data-key', $('#m13_fav').attr('data-key'))
                .append('<img id=m16_fav_flag style=height:20;width:20; src=' + $('#m13_fav_flag').attr('src') + '>')
                .append('<input type=hidden value=' + $('#m13_fav').attr('data-key') +' name=' + ele.id +'></>')}   
            else if (ele.id.split('_')[1] == 'dog' && $('#m13_fav').text() == '') {
                    //do nothing
                } 
            else if (ele.id.split('_')[1] == 'fav' && $('#m13_dog').text() == '') {
                    //do nothing
                }
            else {
                $('#m16_fav').text($('#m13_dog').text())
                .attr('data-key', $('#m13_dog').attr('data-key'))
                .append('<img id=m16_fav_flag style=height:20;width:20; src=' + $('#m13_dog_flag').attr('src') + '>')
                .append('<input type=hidden value=' + $('#m13_dog').attr('data-key') +' name=' + ele.id +'></>')}   
    }
    else if(matchId == 14){
            //console.log('match 14', ele.id)
            //championship team
            $('#m' + path[i+1] + '_dog').text($('#' + ele.id).text())
            .attr('data-key', $('#' + ele.id).attr('data-key'))
            .append('<img id=m' + path[i+1] + '_dog_flag style=height:20;width:20; src=' + $('#' + ele.id + '_flag').attr('src') + '>')
            .append('<input type=hidden value=' + $('#' + ele.id).attr('data-key')  +' name=' + ele.id +'></>')
            //consolation game team
            //console.log('tect: ', $('#m14_fav').text())
            //if (ele.id.split('_')[1] == 'dog') {
            if (ele.id.split('_')[1] == 'dog' && $('#m14_fav').text() != '') {
                $('#m16_dog').text($('#m14_fav').text())
                .attr('data-key', $('#m14_fav').attr('data-key'))
                .append('<img id=m16_dog_flag style=height:20;width:20; src=' + $('#m14_fav_flag').attr('src') + '>')
                .append('<input type=hidden value=' + $('#m14_fav').attr('data-key') +' name=' + ele.id +'></>')}
            else if (ele.id.split('_')[1] == 'dog' && $('#m14_fav').text() == '') {
                //do nothing
            } 
            else if (ele.id.split('_')[1] == 'fav' && $('#m14_dog').text() == '') {
                //do nothing
            }
            else {
                $('#m16_dog').text($('#m14_dog').text())
                .attr('data-key', $('#m14_dog').attr('data-key'))
                .append('<img id=m16_dog_flag style=height:20;width:20; src=' + $('#m14_dog_flag').attr('src') + '>')
                .append('<input type=hidden value=' + $('#m14_dog').attr('data-key') +' name=' + ele.id +'></>')}   
    }
    //championship game
    else if (matchId == 15) {
        //console.log('champion' , ele.id, matchId)
        $('#champion').text($('#' + ele.id).text())
        .attr('data-key', $('#' + ele.id).attr('data-key'))
        .append('<img id=champion_flag style=height:20;width:20; src=' + $('#' + ele.id + '_flag').attr('src') + '>')
        //.append('<input type=hidden value=' + $('#' + ele.id).attr('data-key') +' name=champ></>')
        .append('<input type=hidden value=' + $('#' + ele.id).attr('data-key') +' name=' + ele.id +'></>')
    }
    //consolation game
    else if (matchId == 16) {
        //console.log('consolation winner' ,ele.id)
        $('#third_place').text($('#' + ele.id).text())
        .attr('data-key', $('#' + ele.id).attr('data-key'))
        .append('<img id=third_place_flag style=height:20;width:20; src=' + $('#' + ele.id + '_flag').attr('src') + '>')
        //.append('<input type=hidden value=' + $('#' + ele.id).attr('data-key') +' name=third></>')
        .append('<input type=hidden value=' + $('#' + ele.id).attr('data-key') +' name=' + ele.id +'></>')
    }
    else {console.log('else error')}
var cf = checkForward(ele, matchId)
cf.then(checkComplete())
}
    
function findPath(ele) {
    pathArray = [
        [1, 2, 9, 13, 15, 16], 
        [3, 4, 10, 13, 15, 16], 
        [5, 6, 11, 14, 15, 16], 
        [7, 8, 12, 14, 15, 16]
            ]

    var p = []        
    $.each(pathArray, function(i, path) {
        if (path.indexOf(parseInt(ele.id.split('_')[0].substring(1))) != -1) {
            p = path
            return false
        }
    } )
    return p
}

function checkForward(ele, matchId) {
    return new Promise(function (resolve,reject) {
    var team = ele
    //console.log('------------------------------')
    //console.log('CF', team.dataset.key, ele.id)
    if (ele.id.split('_')[1] == 'dog') {
        var opponent = $('#' + ele.id.split('_')[0] + '_fav')[0].dataset.key}
    else {var opponent = $('#' + ele.id.split('_')[0] + '_dog')[0].dataset.key}
    //console.log('opp', opponent)

    picks = $(document).find('[data-key="' + opponent + '"]')
    //console.log('picks array ', picks)

    for (let i=0; i < picks.length; i++) {
        pickMatch = picks[i].id.split('_')[0].substring(1)
      //  console.log('key: ', pickMatch, matchId, picks[i].dataset.key, opponent)
        if (parseInt(pickMatch) > parseInt(matchId) && picks[i].dataset.key == opponent &&  pickMatch != '16') {
            
            var reset=resetEle($('#' + picks[i].id))
            reset.then(resetChamp())
            
        }
        else if (pickMatch == '16' && matchId != '13' && matchId != '14' && matchId != '16') {
        //    console.log('consolaion logic')
            var reset=resetEle($('#' + picks[i].id))
            reset.then(resetChamp())

        }
        else if (pickMatch == 'hird' || pickMatch == 'hampion') {
          //  console.log('third place')
          var reset=resetEle($('#' + picks[i].id))
          reset.then(resetChamp())

            
        }
        else {
            resetChamp()
        }
    }
    //console.log('check forward resolving')
    resolve()})
}

function resetEle(ele) {
    return new Promise(function (resolve,reject) {
    console.log('resetEle: ', ele.text(), ele.attr('data-key'), ele.attr('id'), $('#third_place').attr('data-key'),$('#m16_fav').attr('data-key') )
    ele.text('')
    ele.data('key', '')
    $('input[name=' + ele.attr('id').split('_')[0].substring(1) + ']').val('')
    console.log('resolve ele reset')
    resolve()    
    })
}

function resetChamp() {
    console.log('reset chanp')
    console.log('third ', $('#third_place').attr('data-key'), $('#m16_fav').attr('data-key'),  $('#m16_dog').attr('data-key'))
    if ($('#champion').attr('data-key') != $('#m15_fav').attr('data-key') && $('#champion').attr('data-key') != $('#m15_dog').attr('data-key')) {
        $('#champion').text('')
        $('#champion').data('key', '')
    }
    if ($('#third_place').attr('data-key') != $('#m16_fav').attr('data-key') && $('#third_place').attr('data-key') != $('#m16_dog').attr('data-key')) {
        console.log("IF OK")
        $('#third_place').text('')
        $('#third_place').data('key', '')
    }
    return
}

function checkComplete() {
    picks = $('input').filter(function() {return $(this).val() > ''})
    //console.log(picks)
    //console.log('picks len ', picks.length)
    if (picks.length == 19) {  //19 to skip token
        $('#sub_btn').text('Submit Picks').attr('disabled', false)
    }
    else {
        $('#sub_btn').text(picks.length -1 + ' of 18 picks').attr('disabled', true)
    }
}

