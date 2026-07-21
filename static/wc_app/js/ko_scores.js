$(document).ready(function () {
    fetch("/wc_app/wc_scores_api/" + $('#stage_key').text(), {method: "GET"})
    .then((response) => response.json())
    .then((responseJSON) => {
        data = responseJSON
        console.log(data)
        if (data.error) {
            $('#scores_div').append("<h3>John is a crappy programmer, send him a line msg </h3>")
            $('#status').html('<p> Error Message: ' + data.error + '<p>')
        } else {
            if (data.results.complete) {
                $('#stage_name').text('Tournament Complete. Congrats to the winner ' + data.results.winner)
            }
            $('#scores_div').append('<p><a href=wc_scores/group>Group Stage Scores</a></p>')
            $('#scores_div').append('<table id=score_table class="table table-bordered table-sm"></table>')
            $('#score_table').append('<thead></thead>')

            if ($('#event_type').text() == 'wbc') {
                var t = buildWBCTable(data)
                t.then(sort_table('score_table'))
            } else {
                $('#score_table').find('thead').append(
                    '<th class=border>Player</th>' +
                    '<th class=border>Total</th>' +
                    '<th class=border>KO</th>' +
                    '<th class=border>Group</th>' +
                    '<th class=border>Best</th>' +
                    '<th class=border>Champion</th>'
                )
                $('#score_table').append('<tbody id=score_table_body></tbody>')

                $.each(data, function(user, d) {
                    if (user != 'results') {
                        $('#score_table').append(
                            '<tr id=' + user + '_row class="small picks-header" style="cursor:pointer">' +
                                '<td>' + user + ' <small>▼</small></td>' +
                                '<td><strong>' + d.Score + '</strong></td>' +
                                '<td><a href=/wc_app/wc_ko_picks_view/' + user + '>' + d.ko_stage_score + '</a></td>' +
                                '<td>' + d.group_stage_score + '</td>' +
                                '<td>' + d.best_score + '</td>' +
                                '<td id="' + user + '_champion"></td>' +
                            '</tr>' +
                            '<tr id=' + user + '_details class="picks-detail" style="display:none">' +
                                '<td colspan=5><div id=' + user + '_picks_div class="picks-container"></div></td>' +
                            '</tr>'
                        )
                        addPicks(user, d.picks, data.results)
                        
                    }
                })

                sortWCTable('score_table')
                $('#status').remove()

                $(document).on('click', '.picks-header', function() {
                    var detailRow = $(this).next('.picks-detail')
                    var arrow = $(this).find('small')
                    detailRow.toggle()
                    arrow.text(detailRow.is(':visible') ? '▲' : '▼')
                })
            }
        }
    })
})

function buildWBCTable(data) {
    return new Promise(function (resolve, reject) {
        $('#score_table').find('thead').append(
            '<th class=border>Player</th><th class=border>Total Score</th>' +
            '<th class=border>Quarters</th><th class=border>Semis</th><th class=border>Champion</th>'
        )
        $('#score_table').append('<tbody id=score_table_body></tbody>')

        $.each(data, function(user, d) {
            if (user != 'results') {
                $('#score_table').append(
                    '<tr id=' + user + '_row class=small><td>' + user + '</td>' +
                    '<td><p style=font-weight:bold;>Total: ' + d.Score + '</p>' +
                    '<p><a href=/wc_app/wc_ko_picks_view/' + user + '>KO:  ' + d.ko_stage_score + '</a></p>' +
                    '<p>Group Stage: ' + d.group_stage_score + '</p>' +
                    '<p>Best possible score: ' + d.best_score + '</p>' +
                    '</td>' +
                    '<td id=' + user + '_quarters_cell></td>' +
                    '<td id=' + user + '_semis_cell></td>' +
                    '<td id=' + user + '_champ_cell></td>' +
                    '</tr>'
                )
                addWBCPicks(user, d.picks, data.results)
            }
        })
        resolve()
    })
}

function sort_table(tableId) {
    var table, rows, switching, i, x, y, shouldSwitch;
    table = $('#' + tableId)
    switching = true;
    console.log('Sorting table', tableId)

    while (switching) {
        switching = false;
        rows = table[0].rows;
        l = rows.length
        for (i = 0; i < (l - 1); i++) {
            console.log('Comparing rows', i, 'and', i + 1, rows[i], $(rows[i+1]).hasClass('picks-detail'))
            shouldSwitch = false;
            // skip detail rows
            if ($(rows[i]).hasClass('picks-detail') || $(rows[i+1]).hasClass('picks-detail')) continue;

            x = rows[i].getElementsByTagName('td')[1].innerHTML.replace(/<[^>]+>/g, '').trim().split(/\s+/)[0];
            y = rows[i + 1].getElementsByTagName('td')[1].innerHTML.replace(/<[^>]+>/g, '').trim().split(/\s+/)[0];

            console.log('Comparing:', x, y, 'as numbers:', Number(x), Number(y))
            if (Number(x) < Number(y)) {
                shouldSwitch = true;
                break;
            }
        }
        if (shouldSwitch) {
            // move both the header row and its detail row together
            var detailRow = rows[i + 1].nextElementSibling
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i])
            if (detailRow && $(detailRow).hasClass('picks-detail')) {
                rows[i].parentNode.insertBefore(detailRow, rows[i])
            }
            switching = true;
        }
    }
}

function sortWCTable(tableId) {
    var tbody = document.querySelector('#' + tableId + ' tbody');
    var switching = true;

    while (switching) {
        switching = false;
        var summaryRows = Array.from(tbody.querySelectorAll('tr.picks-header'));
        for (var i = 0; i < summaryRows.length - 1; i++) {
            var x = Number($(summaryRows[i]).find('td').eq(1).text().trim());
            var y = Number($(summaryRows[i + 1]).find('td').eq(1).text().trim());
            if (x < y) {
                var detailB = summaryRows[i + 1].nextElementSibling;
                tbody.insertBefore(summaryRows[i + 1], summaryRows[i]);
                if (detailB && $(detailB).hasClass('picks-detail')) {
                    tbody.insertBefore(detailB, summaryRows[i]);
                }
                switching = true;
                break;
            }
        }
    }
}

function addPicks(user, data, results) {
    $('#' + user + '_champion').html(pickHTML(data.final[0]))
    $.each(data, function(group, pickList) {
        var groupHtml = '<div class="pick-group"><strong>' + group + '</strong><div class="pick-group-items">'
        $.each(pickList, function(i, pick) {
            var eleClass = pick[4] == 'out' ? 'loser' : 'winner'
            groupHtml += '<span class="pick-item"><img src=' + pick[1] + ' style="height:20px;width:20px;"> ' +
                         '<span class=' + eleClass + '>' + pick[0] + ': ' + pick[3] + ' pts</span></span>'
        })
        groupHtml += '</div></div>'
        $('#' + user + '_picks_div').append(groupHtml)
    })
}

function pickHTML(pick) {
        var eleClass = pick[4] == 'out' ? 'loser' : 'winner'
        return '<span class="pick-item"><img src=' + pick[1] + ' style="height:20px;width:20px;"> ' +
                         '<span class=' + eleClass + '>' + pick[0] + ': ' + pick[3] + ' pts</span></span>'
}

function addWBCPicks(user, data, results) {
    $.each(data, function(i, info) {
        console.log('A', results)
        console.log(results['2nd Round'], i)
        if (i + 1 < 5) {
            if (results['2nd Round'].losers.indexOf(info[0]) != -1) {
                c = 'loser'
            } else if (results['2nd Round'].winners.indexOf(info[0]) != -1) {
                c = 'winner'
            } else { c = '' }
            $('#' + user + '_quarters_cell').append('<p><img src=' + info[1] + ' style=height:20;width:20;><span class=' + c + ' >' + info[0] + ' : ' + info[3] + ' pts</span></p>')
        } else if (i + 1 == 5 || i + 1 == 6) {
            if (results['Semi-Finals'].losers.indexOf(info[0]) != -1 || info[4] == 'out') {
                c = 'loser'
            } else if (results['Semi-Finals'].winners.indexOf(info[0]) != -1) {
                c = 'winner'
            } else { c = '' }
            $('#' + user + '_semis_cell').append('<p><img src=' + info[1] + ' style=height:20;width:20;><span class=' + c + ' >' + info[0] + ' : ' + info[3] + ' pts</span></p>')
        } else if (i + 1 == 7) {
            if (results['Finals'].losers.indexOf(info[0]) != -1 || info[4] == 'out') {
                c = 'loser'
            } else if (results['Finals'].winners.indexOf(info[0]) != -1) {
                c = 'winner'
            } else { c = '' }
            $('#' + user + '_champ_cell').append('<p><img src=' + info[1] + ' style=height:20;width:20;><span class=' + c + ' >' + info[0] + ' : ' + info[3] + ' pts</span></p>')
        }
    })
}


