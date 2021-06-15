$(document).ready(function () {
    start = new Date()
    $.ajax({
        type: "GET",
        url: "/golf_app/get_info/",
        dataType: 'json',
        data: {'tournament' : $('#tournament_key').text()},
        success: function (json) {
            info = $.parseJSON((json))
            buildHeader()
            groups = []
            $.each($('#groups_list li'), function(i, g) {
                groups.push(g.innerText) })
                var fn = function wrapper(g){ // sample async action
                    return new Promise(resolve => resolve(build_field(g, info)));
                };

            var actions = groups.map(fn) 
            var results = Promise.all(actions)
            results.then((() => {    
                    $.getScript('/static/golf_app/js/field.js')

                    $('#field_sect form').append('<div id=bottom_sect class=field_stats_display></div>')
    
                    $('#bottom_sect').append(
                    '<div id=bottom class=field_stats_display>' +
                    '<div id=stats-dtl-toggle>' +
                        '<h5>Hide Stats <i class="fa fa-minus-circle show" style="color:lightblue"></i></h5>' +
                    '</div>' +
            
                    '<div id=pick-status></div>' + 
                    '<input id=sub_button type="submit" class="btn btn-secondary" value="Submit Picks" disabled>' 
                    )
                    //trying to fix position small screen
                    $('#pick_form').on('submit', function(event){
                        event.preventDefault();
                        console.log("form submitted!")  
                        create_post();
                    });

                    checkStarted()
                    $('input').prop('disabled', false)
                        }))
            }
    })        
})

function build_field(g, info) {
    return new Promise (function (resolve, reject) {
        
        //Intro section

        $('#field_sect #pick_form').append('<table id=tbl-group-' + g + ' class=table> \
                                <thead class=total_score> <th> Group: ' + g + '</th> </thead>' +
                            '</table>')

        //picks tables/groups
        fetch("/golf_app/get_prior_result/",         
                {method: "POST",
                headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': $.cookie('csrftoken')
                        },
                body: JSON.stringify({'tournament_key': $('#tournament_key').text(),
                                    'golfer_list': [],
                                    'group': g})
            })
        .then((response) => response.json())
        .then((responseJSON) => {
            data = responseJSON
            console.log('data', data)
            $.each(data, function(i, field) {
                
                picks = info[field.group.number]
                if (picks == 1) {
                    input_type = 'radio'
                    input_class = 'my-radio'
                }
                else 
                    {input_type = 'checkbox'   
                     input_class = 'my-checkbox'}
                $('#tbl-group-' + field.group.number.toString()).append('<tr id=player' + field.golfer.espn_number + ' class=top_row>' +
                                                            '<td id=playerInfo' + field.golfer.espn_number + '>' +
                                                                '<input type="hidden" name="csrfmiddlewaretoken" value=' + $.cookie('csrftoken') +  '>' +
                                                               // '<input id=' + field.id +  ' type="radio" class="my-radio" name=group-' + field.group.number + ' value=' + field.id +  '>' +
                                                               '<input id=' + field.id +  ' type=' + input_type + ' class=' + input_class + ' name=group-' + field.group.number + ' value=' + field.id +  ' disabled>' +
                                                                '<img src=' + field.golfer.pic_link + ' alt="">' + field.playerName + ' ' + 
                                                                '<img src=' + field.golfer.flag_link + ' alt="">' +
                                                                '<a href="https://www.google.com/search?q=' + field.playerName + '" target="_blank" style="padding-left: 1em;">Google</a> / ' +
                                                                '<a href=' + field.espn_link + ' target="_blank">ESPN</a> / ' +
                                                                '<a href=' + field.pga_link + ' target="_blank">PGA</a>' +
                                                            '</td>' + 
                                                          '</tr>' + 
                                                          '<tr class="small stats-row" >' +
                                                          '<td>' +
                                                          '<table id=stats' + field.golfer.espn_number +' class=table table-bordered table-sm>' +
                                                              '<tr style=background-color:lightblue;>' +
                                                                 '<th colspan=2>Current OWGR</th>' +
                                                                 '<th colspan=2>Last Week OWGR</th>' +
                                                                 '<th colspan=3>Last Season OWGR</th>' +
                                                              '</tr>' +
                                                              '<tr>' +
                                                                 '<td colspan=2>' + field.currentWGR + '</td>' + 
                                                                 '<td colspan=2>' + field.sow_WGR + '</td>' +
                                                                 '<td colspan=3>' + field.soy_WGR + '</td>' +
                                                               '</tr>' +
                                                              '<tr style=background-color:lightblue;>' +
                                                                 '<th colspan=2>Handicap</th>' +
                                                                 '<th colspan=2>This event last year</th>' +
                                                                 '<th colspan=3>Recent Form</th>' +
                                                              '</tr>' + 
                                                              '<tr>' +
                                                                 '<td colspan=2>' + field.handi + '</td>' +
                                                                 '<td colspan=2>' + field.prior_year + '</td>' +
                                                                 '<td colspan=3 id=recent' + field.golfer.espn_number + '> </td>' +
                                                              '</tr>' +
                                                              '<tr style=background-color:lightblue;><th colspan=7>Season Stats</th></tr>' +
                                                              '<tr><td>Played</td> <td>Won</td> <td>2-10</td> <td>11-29</td><td>30-49</td><td>> 50</td> <td>Cuts</td></tr>' +
                                                              '<tr>' +
                                                                    '<td>' + field.season_stats.played + '</td>' + 
                                                                    '<td>' + field.season_stats.won + '</td>' + 
                                                                    '<td>' + field.season_stats.top10 + '</td>' +
                                                                    '<td>' + field.season_stats.bet11_29 + '</td>' +
                                                                    '<td>' + field.season_stats.bet30_49 + '</td>' +
                                                                    '<td>' + field.season_stats.over50 + '</td>' +
                                                                    '<td>' + field.season_stats.cuts +  '</td>'  +
                                                              '</tr>' + 
                                                          '</table>' +
                                                        '</td>' +
                                                        '</tr>'
                                          
                                                           )

                                                $('input#' + field.id).on('change', function(evt) {
                                                    $('#pick-status').empty()
                                                    get_info(info, this)
                                                })
                                                           
                                                ranks = ''
                                                $.each(field.recent, function(i, rank){ranks += rank.rank + ', '})
                                                            var items = ''
                                                            $.each(field.recent, function(i, rank){items += rank.name + ': ' + rank.rank + '\n'})
                                                            
                                                            $('#recent' + field.golfer.espn_number).html('<p>' + ranks + '<span> <a id=tt-recent' + field.golfer.espn_number + 
                                                                ' data-toggle="tooltip" html="true" > <i class="fa fa-info-circle" style="color:blue"></i> </a> </span> </p>')
                                                            $('#tt-recent' + field.golfer.espn_number + '[data-toggle="tooltip"]').tooltip({trigger:"hover",
                                                                 delay:{"show":400,"hide":800}, "title": items
                                                        })
                                                           resolve() })                                                          

               })    
                })
                }



function checkStarted() {
    fetch("/golf_app/started/",         
    {method: "POST",
    headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'X-CSRFToken': $.cookie('csrftoken')
            },
    body: JSON.stringify({'key': $('#tournament_key').text(),
                            })
})
.then((response) => response.json())
.then((responseJSON) => {
    started = $.parseJSON(responseJSON)
    console.log('started ', started, started.started, started.late_picks)
    if (started.started  && ! started.late_picks) {        
        $("#make_picks").attr('hidden', '')
        $('#too_late').removeAttr('hidden')
        $('#sub_button').remove()
    }
    else {
        $('#random_btn').removeAttr('disabled').attr('class', 'btn btn-primary');
    }
})
}


function buildHeader() {
    $('#top_sect').append('<div id=make_picks><br> <p>Please make 1 pick for each group below</p>' +
    '<form id="random_form" name="random_form" method="post">' +
    '<input type="hidden" name="csrfmiddlewaretoken" value=' + $.cookie('csrftoken') +  '>' +
    //'<input type="text" name="random" value="random" hidden>' +
    '<p>or click for random picks  <input id=random_btn type="submit" class="btn btn-secondary" value="Random" disabled> </p>' +
    '</form>')

    $('#top_sect').append('<div id=too_late hidden><br> <p>Tournament Started, too late for picks</p></div>')

    // $('#top_sect').append('<span style="float: right;" >' + 
    //     '<a href="#" id="download" >' +
    //     '<i class="fas fa-file-download" title="Download CSV" data-toggle="tooltip"> Download Data</i>' +
    //     '</a>' +
    //     '</span>')

    $('#top_sect').append('<span style="float: right;" >' + 
        '<a href="#" id="download_excel" >' +
        '<i class="fas fa-file-download" title="Download Excel" data-toggle="tooltip"> Download Excel</i>' +
        '</a>' +
        '</span>')

    $('#top_sect').append('<br> <div id=stats-dtl-toggle>' + 
        '<h5>Hide Stats <i class="fa fa-minus-circle show" style="color:lightblue"></i></h5>' +
        '<br></div>')

    $('#field_sect').append('<form id=pick_form method=post></form>')
    
    //$('#field_sect form').append('<div id=bottom_sect class=field_stats_display></div>')
    
    // $('#pick_form').on('submit', function(event){
    //     event.preventDefault();
    //     console.log("form submitted!")  
    //     create_post();
    // });

    $('#random_form').on('submit', function(event){
        event.preventDefault();
        console.log("random submitted!")  
        create_post_random();
    });
}


function create_post() {
    toggle_submitting()    
    checked = $('input:checked')
    //console.log(checked)
    pick_list = []
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