$(document).ready(function() {
       fetch("/wc_app/wc_ko_bracket_api/" + $('#picks_user').text(),
         {method: "GET",
         })
         .then((response) => response.json())
         .then((responseJSON) => {
                data = responseJSON
                console.log('games: ', data)
                picks = JSON.parse(data.picks)
                console.log('picks: ', picks)

                var matches = createMatches(data)
                matches.then(initPicks(picks, data))
            })
        })

function createMatches(data) {
    return new Promise(function (resolve,reject) {

        $.each(data, function(match_num, teams) {

            $('#m' + match_num.split('_')[1] + '_fav').text(teams.fav + '(' + teams.fav_fifa_rank + ')')
            .append('<img id=m' + match_num.split('_')[1] + '_fav_flag style=height:20;width:20; src=' + teams.fav_flag + '>')
            .attr('data-key', teams.fav_pk)

            $('#m' + match_num.split('_')[1] + '_dog').text(teams.dog + '(' + teams.dog_fifa_rank + ')')
            .append('<img id=m' + match_num.split('_')[1] + '_dog_flag style=height:20;width:20; src=' + teams.dog_flag + '>')
            .attr('data-key', teams.dog_pk)

            $('#m' + match_num.split('_')[1] + '_fav').on('click', function() {teamPicked(this)})
            $('#m' + match_num.split('_')[1] + '_dog').on('click', function() {teamPicked(this)})
        })
        var ep = earlyPicks(data)
        ep.then((response) => {console.log('early picks resolved');
                                resolve()
         })
    })
}

function earlyPicks(data) {
    return new Promise(function (resolve,reject) {

        $.each($('.matchup li'), function(i, ele) {
            if ($('#early_picks_period').text() == 'True') {
                var key = 'match_' + ele.id[1]
                if (data[key]) {
                    $('#m' + ele.id[1] + '_fav').on('click', function() {teamPicked(this)})
                    $('#m' + ele.id[1] + '_dog').on('click', function() {teamPicked(this)})
                } else {
                    $('#m' + ele.id[1] + '_fav').off('click').text('coming soon...')
                    $('#m' + ele.id[1] + '_dog').off('click').text('coming soon...')
                }
            } else {
                $('#m' + ele.id[1] + '_fav').on('click', function() {teamPicked(this)})
                $('#m' + ele.id[1] + '_dog').on('click', function() {teamPicked(this)})
                if (data['match_' + ele.id[1]] && data['match_' + ele.id[1]].early_game == true) {
                    $('#m' + ele.id[1] + '_fav').off('click')
                    $('#m' + ele.id[1] + '_dog').off('click')
                }
            }
        })
        resolve()
    })
}

function initPicks(picks, data) {
    $.each(picks, function(i, pick) {
        teamPicked($('#' + pick.fields.data.from_ele)[0])
        $('#' + pick.fields.data.from_ele).trigger('click')
    })
}

// Maps each R32/R16/QF/SF match_id to the slot it fills in the next match.
// Derived from ko_data.json home_team/away_team qualifier_source.
var feedsSlot = {
    73:'fav', 75:'dog',   // → m90
    74:'fav', 77:'dog',   // → m89
    76:'fav', 78:'dog',   // → m91
    79:'fav', 80:'dog',   // → m92
    83:'fav', 84:'dog',   // → m93
    81:'fav', 82:'dog',   // → m94
    86:'fav', 88:'dog',   // → m95
    85:'fav', 87:'dog',   // → m96
    89:'fav', 90:'dog',   // → m97
    93:'fav', 94:'dog',   // → m98
    91:'fav', 92:'dog',   // → m99
    95:'fav', 96:'dog',   // → m100
    97:'fav', 98:'dog',   // → m101
    99:'fav',100:'dog',   // → m102
   101:'fav',102:'dog'    // → m104
}

function teamPicked(ele) {
    var path = findPath(ele)
    var matchId = ele.id.split('_')[0].substring(1)
    var i = path.indexOf(parseInt(matchId))

    if ($('#event_type').text() == 'wbc') {wbcPath(ele, matchId, path)}
    else {
        if (i == -1) {
            console.log(' -1 error')
        }
        // R32: pairs at positions 0,1 feed the R16 match at position 2
        else if (i == 0 || i == 1) {
            if (i % 2 == 0) {
                $('#m' + path[i+2] + '_fav').text($('#' + ele.id).text())
                .attr('data-key', $('#' + ele.id).attr('data-key'))
                .append('<img id=m' + path[i+2] + '_fav_flag style=height:20;width:20; src=' + $('#' + ele.id + '_flag').attr('src') + '>')
                .append('<input type=hidden value=' + $('#' + ele.id).attr('data-key') + ' name=' + ele.id + '></>')
            } else {
                $('#m' + path[i+1] + '_dog').text($('#' + ele.id).text())
                .attr('data-key', $('#' + ele.id).attr('data-key'))
                .append('<img id=m' + path[i+1] + '_dog_flag style=height:20;width:20; src=' + $('#' + ele.id + '_flag').attr('src') + '>')
                .append('<input type=hidden value=' + $('#' + ele.id).attr('data-key') + ' name=' + ele.id + '></>')
            }
        }
        // R16, QF: use feedsSlot to determine fav/dog in the next match
        else if (i == 2 || i == 3) {
            var slot = feedsSlot[parseInt(matchId)]
            $('#m' + path[i+1] + '_' + slot).text($('#' + ele.id).text())
            .attr('data-key', $('#' + ele.id).attr('data-key'))
            .append('<img id=m' + path[i+1] + '_' + slot + '_flag style=height:20;width:20; src=' + $('#' + ele.id + '_flag').attr('src') + '>')
            .append('<input type=hidden value=' + $('#' + ele.id).attr('data-key') + ' name=' + ele.id + '></>')
        }
        // SF left (101): winner → m104_fav, loser → m103_fav
        else if (matchId == 101) {
            $('#m104_fav').text($('#' + ele.id).text())
            .attr('data-key', $('#' + ele.id).attr('data-key'))
            .append('<img id=m104_fav_flag style=height:20;width:20; src=' + $('#' + ele.id + '_flag').attr('src') + '>')
            .append('<input type=hidden value=' + $('#' + ele.id).attr('data-key') + ' name=' + ele.id + '></>')
            // loser → consolation fav slot
            if (ele.id.split('_')[1] == 'dog' && $('#m101_fav').text() != '') {
                $('#m103_fav').text($('#m101_fav').text())
                .attr('data-key', $('#m101_fav').attr('data-key'))
                .append('<img id=m103_fav_flag style=height:20;width:20; src=' + $('#m101_fav_flag').attr('src') + '>')
                .append('<input type=hidden value=' + $('#m101_fav').attr('data-key') + ' name=' + ele.id + '></>')
            } else if (ele.id.split('_')[1] == 'dog' && $('#m101_fav').text() == '') {
                // do nothing
            } else if (ele.id.split('_')[1] == 'fav' && $('#m101_dog').text() == '') {
                // do nothing
            } else {
                $('#m103_fav').text($('#m101_dog').text())
                .attr('data-key', $('#m101_dog').attr('data-key'))
                .append('<img id=m103_fav_flag style=height:20;width:20; src=' + $('#m101_dog_flag').attr('src') + '>')
                .append('<input type=hidden value=' + $('#m101_dog').attr('data-key') + ' name=' + ele.id + '></>')
            }
        }
        // SF right (102): winner → m104_dog, loser → m103_dog
        else if (matchId == 102) {
            $('#m104_dog').text($('#' + ele.id).text())
            .attr('data-key', $('#' + ele.id).attr('data-key'))
            .append('<img id=m104_dog_flag style=height:20;width:20; src=' + $('#' + ele.id + '_flag').attr('src') + '>')
            .append('<input type=hidden value=' + $('#' + ele.id).attr('data-key') + ' name=' + ele.id + '></>')
            // loser → consolation dog slot
            if (ele.id.split('_')[1] == 'dog' && $('#m102_fav').text() != '') {
                $('#m103_dog').text($('#m102_fav').text())
                .attr('data-key', $('#m102_fav').attr('data-key'))
                .append('<img id=m103_dog_flag style=height:20;width:20; src=' + $('#m102_fav_flag').attr('src') + '>')
                .append('<input type=hidden value=' + $('#m102_fav').attr('data-key') + ' name=' + ele.id + '></>')
            } else if (ele.id.split('_')[1] == 'dog' && $('#m102_fav').text() == '') {
                // do nothing
            } else if (ele.id.split('_')[1] == 'fav' && $('#m102_dog').text() == '') {
                // do nothing
            } else {
                $('#m103_dog').text($('#m102_dog').text())
                .attr('data-key', $('#m102_dog').attr('data-key'))
                .append('<img id=m103_dog_flag style=height:20;width:20; src=' + $('#m102_dog_flag').attr('src') + '>')
                .append('<input type=hidden value=' + $('#m102_dog').attr('data-key') + ' name=' + ele.id + '></>')
            }
        }
        // Final (104): winner → #champion
        else if (matchId == 104) {
            $('#champion').text($('#' + ele.id).text())
            .attr('data-key', $('#' + ele.id).attr('data-key'))
            .append('<img id=champion_flag style=height:20;width:20; src=' + $('#' + ele.id + '_flag').attr('src') + '>')
            .append('<input type=hidden value=' + $('#' + ele.id).attr('data-key') + ' name=' + ele.id + '></>')
        }
        // Consolation (103): winner → #third_place
        else if (matchId == 103) {
            $('#third_place').text($('#' + ele.id).text())
            .attr('data-key', $('#' + ele.id).attr('data-key'))
            .append('<img id=third_place_flag style=height:20;width:20; src=' + $('#' + ele.id + '_flag').attr('src') + '>')
            .append('<input type=hidden value=' + $('#' + ele.id).attr('data-key') + ' name=' + ele.id + '></>')
        }
        else {console.log('else error')}

        var cf = checkForward(ele, matchId)
        cf.then(checkComplete())
    }
}

function wbcPath(ele, matchId, path) {
    var i = path.indexOf(parseInt(matchId))

    if (i == -1) {
        alert('Something went wrong, please try again')
    } else {
        if (parseInt(matchId) <= 4) {
            if (parseInt(matchId) == 1) {
                $('#m5_fav').text($('#' + ele.id).text())
                .attr('data-key', $('#' + ele.id).attr('data-key'))
                .append('<img id=m5_fav_flag style=height:20;width:20; src=' + $('#' + ele.id + '_flag').attr('src') + '>')
                .append('<input type=hidden value=' + $('#' + ele.id).attr('data-key') + ' name=' + ele.id + '></>')
            } else if (parseInt(matchId) == 3) {
                $('#m5_dog').text($('#' + ele.id).text())
                .attr('data-key', $('#' + ele.id).attr('data-key'))
                .append('<img id=m5_dog_flag style=height:20;width:20; src=' + $('#' + ele.id + '_flag').attr('src') + '>')
                .append('<input type=hidden value=' + $('#' + ele.id).attr('data-key') + ' name=' + ele.id + '></>')
            } else if (parseInt(matchId) == 2) {
                $('#m6_fav').text($('#' + ele.id).text())
                .attr('data-key', $('#' + ele.id).attr('data-key'))
                .append('<img id=m6_fav_flag style=height:20;width:20; src=' + $('#' + ele.id + '_flag').attr('src') + '>')
                .append('<input type=hidden value=' + $('#' + ele.id).attr('data-key') + ' name=' + ele.id + '></>')
            } else {
                $('#m6_dog').text($('#' + ele.id).text())
                .attr('data-key', $('#' + ele.id).attr('data-key'))
                .append('<img id=m6_dog_flag style=height:20;width:20; src=' + $('#' + ele.id + '_flag').attr('src') + '>')
                .append('<input type=hidden value=' + $('#' + ele.id).attr('data-key') + ' name=' + ele.id + '></>')
            }
        } else if (matchId == '5') {
            $('#m7_fav').text($('#' + ele.id).text())
            .attr('data-key', $('#' + ele.id).attr('data-key'))
            .append('<img id=m7_fav_flag style=height:20;width:20; src=' + $('#' + ele.id + '_flag').attr('src') + '>')
            .append('<input type=hidden value=' + $('#' + ele.id).attr('data-key') + ' name=' + ele.id + '></>')
        } else if (matchId == '6') {
            $('#m7_dog').text($('#' + ele.id).text())
            .attr('data-key', $('#' + ele.id).attr('data-key'))
            .append('<img id=m7_dog_flag style=height:20;width:20; src=' + $('#' + ele.id + '_flag').attr('src') + '>')
            .append('<input type=hidden value=' + $('#' + ele.id).attr('data-key') + ' name=' + ele.id + '></>')
        } else if (matchId == '7') {
            $('#m8_fav').text($('#' + ele.id).text())
            .attr('data-key', $('#' + ele.id).attr('data-key'))
            .append('<img id=m8_fav_flag style=height:20;width:20; src=' + $('#' + ele.id + '_flag').attr('src') + '>')
            .append('<input type=hidden value=' + $('#' + ele.id).attr('data-key') + ' name=' + ele.id + '></>')
        }
    }
    var cf = checkForward(ele, matchId)
    cf.then(checkComplete())
}

function findPath(ele) {
    if ($('#event_type').text() == 'wbc') {
        pathArray = [
            [1, 5, 7, 8],
            [2, 6, 7, 8],
            [3, 5, 7, 8],
            [4, 6, 7, 8],
            [5, 7, 8],
            [6, 7, 8],
            [7, 8],
            [8]
        ]
    } else {
        // Paths derived from ko_data.json next_match_id chain.
        // Format: [R32_home, R32_away, R16, QF, SF, Final, Consolation]
        // R32 pairs ordered to match bracket groupings (adjacent pairs → same R16)
        pathArray = [
            [74, 77, 89, 97, 101, 104, 103],  // → m89 → m97 → m101
            [73, 75, 90, 97, 101, 104, 103],  // → m90 → m97 → m101
            [81, 82, 94, 98, 101, 104, 103],  // → m94 → m98 → m101
            [83, 84, 93, 98, 101, 104, 103],  // → m93 → m98 → m101
            [76, 78, 91, 99, 102, 104, 103],  // → m91 → m99 → m102
            [79, 80, 92, 99, 102, 104, 103],  // → m92 → m99 → m102
            [86, 88, 95, 100, 102, 104, 103], // → m95 → m100 → m102
            [85, 87, 96, 100, 102, 104, 103]  // → m96 → m100 → m102
        ]
    }
    var p = []
    $.each(pathArray, function(i, path) {
        if (path.indexOf(parseInt(ele.id.split('_')[0].substring(1))) != -1) {
            p = path
            return false
        }
    })
    return p
}

function checkForward(ele, matchId) {
    return new Promise(function (resolve,reject) {
        var team = ele
        if (ele.id.split('_')[1] == 'dog') {
            var opponent = $('#' + ele.id.split('_')[0] + '_fav')[0].dataset.key
        } else {
            var opponent = $('#' + ele.id.split('_')[0] + '_dog')[0].dataset.key
        }

        picks = $(document).find('[data-key="' + opponent + '"]')

        for (let i=0; i < picks.length; i++) {
            pickMatch = picks[i].id.split('_')[0].substring(1)
            if (parseInt(pickMatch) > parseInt(matchId) && picks[i].dataset.key == opponent && pickMatch != '103') {
                var reset = resetEle($('#' + picks[i].id))
                reset.then(resetChamp())
            } else if (pickMatch == '103' && matchId != '101' && matchId != '102' && matchId != '103') {
                var reset = resetEle($('#' + picks[i].id))
                reset.then(resetChamp())
            } else if (pickMatch == 'hird' || pickMatch == 'hampion') {
                var reset = resetEle($('#' + picks[i].id))
                reset.then(resetChamp())
            } else {
                resetChamp()
            }
        }
        resolve()
    })
}

function resetEle(ele) {
    return new Promise(function (resolve,reject) {
        ele.text('')
        ele.data('key', '')
        $('input[name=' + ele.attr('id').split('_')[0].substring(1) + ']').val('')
        console.log('resolve ele reset')
        resolve()
    })
}

function resetChamp() {
    if ($('#event_type').text() == 'wbc') {
        if ($('#m8_fav').attr('data-key') != $('#m7_fav').attr('data-key') && $('#m8_fav').attr('data-key') != $('#m7_dog').attr('data-key')) {
            $('#m8_fav').text('')
            $('#m8_fav').data('key', '')
        }
    } else {
        if ($('#champion').attr('data-key') != $('#m104_fav').attr('data-key') && $('#champion').attr('data-key') != $('#m104_dog').attr('data-key')) {
            $('#champion').text('')
            $('#champion').data('key', '')
        }
        if ($('#third_place').attr('data-key') != $('#m103_fav').attr('data-key') && $('#third_place').attr('data-key') != $('#m103_dog').attr('data-key')) {
            $('#third_place').text('')
            $('#third_place').data('key', '')
        }
    }
    return
}

function checkComplete() {
    picks = $('input').filter(function() {return $(this).val() > ''})
    if ($('#early_picks_period').text() == 'True') {
        if (picks.length == parseInt($('#early_picks').text())) {
            $('#sub_btn').text('Submit Picks').attr('disabled', false)
        } else {
            $('#sub_btn').text(picks.length + ' of ' + $('#early_picks').text() + ' picks').attr('disabled', true)
        }
    } else {
        if (picks.length - 1 == parseInt($('#picks').text())) {
            $('#sub_btn').text('Submit Picks').attr('disabled', false)
        } else {
            $('#sub_btn').text(picks.length - 1 + ' of ' + $('#picks').text() + ' picks').attr('disabled', true)
        }
    }
}
