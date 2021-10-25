$(document).ready(function () {
    start = new Date()
    Promise.all([
    fetch("/golf_app/get_info/" + $('#tournament_key').text()).then(response => response.json()),
    fetch("/golf_app/field_get_picks").then(response=> response.json())
     ])
     .then((responseJSON) => {
         info = $.parseJSON(responseJSON[0])
         picks = $.parseJSON(responseJSON[1])
 
        var pick_array = [];
        for (let i=0; i < picks.length; i++) {
            pick_array.push(picks[i].playerName.id)
        }

        buildHeader()
        groups = []
        $.each($('#groups_list li'), function(i, g) {
            groups.push(g.innerText) })
            var fn = function wrapper(g){ // sample async action

                return new Promise(resolve => resolve(build_field(g, info, pick_array)));
            };

        var actions = groups.map(fn) 
            var results = Promise.all(actions)
            results.then((() => {    
                    $('[data-toggle="tooltip"]').tooltip();                                                    
                    console.log('getting field js')
                    $.getScript('/static/golf_app/js/field.js')

                    $('#field_sect form').append('<div id=bottom_sect class=field_stats_display></div>')

                    $('#bottom_sect').append(
                    '<div id=bottom class=field_stats_display>' +
                    '<div id=stats-dtl-toggle>' +
                 //       '<h5>Show Stats <i class="fa fa-plus-circle show" style="color:lightblue"></i></h5>' +
                    '</div>' +
                    
                    '<div id=pick-status></div>' + 
                    '<div id=grp_6_buttons class=grp_6_buttons>' + 
                    '<p id=jump_to style="background-color:lightgray; color:white; font-weight:bold;"> Jump to: ' +
                    '</p>' +
                    
                    '</div>' +
                    '<input id=sub_button type="submit" class="btn btn-secondary" value="Submit Picks" disabled>' 
                    )

                    $.each(info, function(group, picks) {if (group != "total"){ $('#jump_to').append('<a href=#tbl-group-' + group + '>' + group + '</a>' + ' ')}}) 
                   // $('#grp_6_buttons').append('<button id=show_6_button class="btn btn-primary btn-group-sm">My G-6 Picks</button>')

                    //trying to fix position small screen
                    $('#pick_form').on('submit', function(event){
                        event.preventDefault();
                        console.log("form submitted!")  
                        create_post();
                    });

                    // $('#show_6_button').on('click', function(eve) {
                    //     eve.preventDefault();
                    //     selected = []
                    //     $.each($('input[name=group-6' + ']:checked'), function(){selected.push($(this).parent().attr('id').replace('playerInfo', ''))})
                    //     console.log('selected G6 hide: ', selected)
                        
                    //     table = $('#tbl-group-6')

                    //     if ($('#show_6_button').html() == 'All Group 6') {
                    //         $('input[name=group-6' + ']').parent().parent().parent().prop('hidden', false)    
                    //         $('#show_6_button').html('My Picks G-6')
                    //     }
                    //     else {
                    //         $('input[name=group-6' + ']').parent().parent().parent().prop('hidden', true)
                    //         $('input[name=group-6' + ']:checked').parent().parent().parent().prop('hidden', false)
                    //         $('#show_6_button').html('All Group 6')
                    //     }
                    //     window.location.href = '#tbl-group-6'
                    // })

                    //there should be a faster way to check started and deal with buttons
                    checkStarted()

                    

                    
                        }))
            }
     )

    })        


function build_field(g, info, pick_array) {
    return new Promise (function (resolve, reject) {

        //Intro section
        
        $('#field_sect #pick_form').append('<table id=tbl-group-' + g + ' class=table> \
                                <thead class=total_score> <th> Group: ' + g + ' - Pick ' + info[g] + ' Golfers' + '<i id=expand-grp-' + g + ' class="fa fa-plus-circle show" style="color:white; float:right;"> Show Group Stats</i> </th> </thead>' +
                            '</table>')
        
        $('#expand-grp-' + g).on('click', function() {
            toggle_stats_display(this, $('#tbl-group-' +g))
        })

        const frag = new DocumentFragment()

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
            console.log('data group: ', g, data)
            data_l = data.length
            for (let idx = 0; idx < data_l; idx++) {
                field = data[idx]
                picks = info[field.group.number]
                if (picks == 1) {
                    input_type = 'radio'
                    input_class = 'my-radio'
                }
                else 
                    {input_type = 'checkbox'   
                     input_class = 'my-checkbox'}

                let field_table = document.createElement('table')
                field_table.id = 'player-' + field.id +'-div'
                field_table.style.width = '100%'

                let golfer_row = build_golfer_row(field, pick_array)
                field_table.append(golfer_row)

                let stats_row = build_stats_row(field)
                field_table.append(stats_row)

                frag.appendChild(field_table)

                                resolve() 
            }

            document.getElementById('tbl-group-' + g).appendChild(frag);        
            

               })    
               })
    }


function formatSG(field) {
    
    $('#stats' + field.golfer.espn_number).append('<tr style=background-color:lightblue;><th colspan=8>Shots Gained Stats</th></tr>') 
    try {
        $('#stats' + field.golfer.espn_number).append('<tr><td>Off Tee Rank</td> <td>Off Tee</td> <td>Approach Rank</td> <td>Approach</td><td>Around Green Rank</td><td>Around Green</td> <td>Putting Rank</td> <td>Putting</td></tr>' +
        '<tr>' +
              
              '<td>' + (field.season_stats.off_tee.rank || 'n/a') + '</td>' + 
              '<td>' + field.season_stats.off_tee.average  + '</td>' + 
              '<td>' + field.season_stats.approach_green.rank + '</td>' + 
              '<td>' + field.season_stats.approach_green.average + '</td>' + 
              '<td>' + field.season_stats.around_green.rank + '</td>' + 
              '<td>' + field.season_stats.around_green.average + '</td>' + 
              '<td>' + field.season_stats.putting.rank + '</td>' + 
              '<td>' + field.season_stats.putting.average + '</td>' )
                        }
    catch (e)  {
              $('#stats' + field.golfer.espn_number).append('<tr><td>No Stats Available</td>')
                }

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
//    if (started.started  && ! started.late_picks) {        
        //$("#make_picks").attr('hidden', '')
        //$('#too_late').removeAttr('hidden')
        //$('#sub_button').remove()
//    }
    checkbox_input = document.getElementsByClassName('my-checkbox')
    var checkbox_l = checkbox_input.length
    radio_input = document.getElementsByClassName('my-radio')
    var radio_l = radio_input.length
    lock_classes = ['started', 'lock']

    if (!started.started || started.late_picks) {
        $('#random_btn').removeAttr('disabled').attr('class', 'btn btn-primary');
        for (let i=0; i < checkbox_l; i++){
            checkbox_input[i].disabled = false
            }
        for (let i=0; i < radio_l; i++){
            radio_input[i].disabled = false
            }
                                                }
    else if(started.started && ! started.late_picks) {
        for (let i=0; i < checkbox_l; i++){
            //console.log(checkbox_input[i].parentElement.parentElement.classList)
            //if (pick_array.indexOf(field.id) != -1) {
            if (checkbox_input[i].parentElement.parentElement.classList.contains('started') || checkbox_input[i].parentElement.parentElement.classList.contains('lock')) {
                checkbox_input[i].disabled = true
            }
            else {checkbox_input[i].disabled = false}
        }
        for (let i=0; i < radio_l; i++){
            if (radio_input[i].parentElement.parentElement.classList.contains('started') || radio_input[i].parentElement.parentElement.classList.contains('lock')) {
                //console.log('lock check started ', radio_input[i], radio_input[i].parentElement.parentElement.classList, radio_input[i].parentElement.parentElement.classList.contains('started', 'lock'))
                radio_input[i].disabled = true
                        }
            else {radio_input[i].disabled = false}
        }

        }
    else {
        console.log('unexpected started condiiton, check')
        for (let i=0; i < checkbox_l; i++){
            checkbox_input[i].disabled = false
            }
        for (let i=0; i < radio_l; i++){
            radio_input[i].disabled = false
            }

    }
})
}


function buildHeader() {
    if ($('#pga_t_num').text() == 468) {
        var instructions = '<p style=font-weight:bold;>Instructions:</p><p>One Pick per Group</p> <p>Match win -10 points, -1 point per hole of winning margin</p>' +
        '<p>Match loss +10 points, +1 point per hole of winning margin</p>' +
        '<p>Draw 0 points</p>' + 
        '<p>DNP +5 points (per session)</p>' + 
        '<p>Winning team -25 points</p>' +
        '<p>Closest to winning score -25.  Must pick winning team to qualify for this bonus.</p>' +
        '<p>To bet on a 14/14 tie, choose Europe as the winner and 14 points as the winning score.</p>'
    }
    else {
        var instructions = '<p>Enter 2 picks for group 1, and 1 pick for remaining groups</p>'
    }
    
    $('#top_sect').append('<div id=make_picks><br>' + instructions + '<br>' +
    '<form id="random_form" name="random_form" method="post">' +
    '<input type="hidden" name="csrfmiddlewaretoken" value=' + $.cookie('csrftoken') +  '>' +
    //'<input type="text" name="random" value="random" hidden>' +
    '<p id=random_line>or click for random picks  <input id=random_btn type="submit" class="btn btn-secondary" value="Random" disabled> </p>' +
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

    // $('#top_sect').append('<br> <div id=stats-dtl-toggle>' + 
    //     '<h5>Show Stats <i class="fa fa-plus-circle show" style="color:lightblue"></i></h5>' +
    //     '<br></div>')

    $('#field_sect').append('<form id=pick_form method=post></form>')

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
    if ($('#pga_t_num').text() == 468) {
        $('#field_sect #pick_form').append('<table id=ryderCup_picks' + " class=table> \
        <thead class=total_score> <th colspan=2>Special Ryder Cup Picks " + '</th> </thead>' +
        '</table>')
        $('#ryderCup_picks').append('<p><label for=winning_team style=font-weight:bold>Choose Winning Team</label>' +  
             '<select id=winning_team class="form-control"><option></option><option value=euro>Europe</option><option value-usa>USA</option> </select> </p>' + 
             '<p><label for=winning_points style=font-weight:bold>Enter winning team score, number between 14 - 28</label>' + 
             '<input id=winning_points class="form-control"  type=number placeholder="enter between 14 - 28" step=0.5 min=14 max=28><textbox></textbox></input></p>')

        $('#winning_points').on('change', function() {
            
            if (parseFloat($('#winning_points').val()) % 1 == 0 || parseFloat($('#winning_points').val()) % 1 == 0.5)
                {
                    if (parseFloat($('#winning_points').val()) >= 14 && parseFloat($('#winning_points').val()) <= 28) 
                        {
                             $('#pick-status').empty()
                             check_complete(info)
                        }
                    else {
                        $('#winning_points').val('')                        
                        $('#pick-status').empty()
                        check_complete(info)
                        alert('Bad winning points entry: ' + $('#winning_points').val() + '. Please enter between 14 and 28')}
            
                }   
                else {
                       $('#winning_points').val('')                        
                       $('#pick-status').empty()
                       check_complete(info)
                       alert ('Bad winning points value, must be a whole number or .5')}
            })

        $('#winning_team').change(function() {console.log('selected team '), winning_team;
                $('#pick-status').empty()                            
                check_complete(info)})
        

        $('#random_line').remove()

    }
    
    
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

function formatMenMedals(data) {

    $('#mens_countries_picks').append('<tr><td>Pick 1:  <select id=men_1_country> </select><td> </tr>')
    $('#mens_countries_picks').append('<tr><td>Pick 2:  <select id=men_2_country> </select><td> </tr>')
    $('#mens_countries_picks').append('<tr><td>Pick 3:  <select id=men_3_country> </select><td> </tr>')

    
    $('#mens_countries_picks').on('change', function(evt) {
            $('#pick-status').empty()
            get_info(info, null) })
    
    $.each(data.men, function(country, count) {
        $('#men_1_country').append('<option value=' + country + '>' + country + ': ' + count + '</option>')
        $('#men_2_country').append('<option value=' + country + '>' + country + ': ' + count + '</option>')
        $('#men_3_country').append('<option value=' + country + '>' + country + ': ' + count + '</option>')
        
    })
    }

function formatWomenMedals(date) {
    $('#womens_countries_picks').append('<tr><td>Pick 1:  <select id=women_1_country> </select><td> </tr>')
    $('#womens_countries_picks').append('<tr><td>Pick 2:  <select id=women_2_country> </select><td> </tr>')
    $('#womens_countries_picks').append('<tr><td>Pick 3:  <select id=women_3_country> </select><td> </tr>')

    $('#womens_countries_picks').on('change', function(evt) {
        $('#pick-status').empty()
        get_info(info, null) })
    
    $.each(data.women, function(country, count) {
        $('#women_1_country').append('<option value=' + country + '>' + country + ': ' + count + '</option>')
        $('#women_2_country').append('<option value=' + country + '>' + country + ': ' + count + '</option>')
        $('#women_3_country').append('<option value=' + country + '>' + country + ': ' + count + '</option>')
        
    })

}

function build_golfer_row(field, pick_array) {

    //console.log(field.playerName, field.started, field.tournament.late_picks, field.lock_group)
    let golfer_row = document.createElement('tr')
        golfer_row.id = 'golfer-' + field.id

    let golfer = document.createElement('td')
    golfer.colSpan =1
    
    golfer.id = 'playerInfo' + field.golfer.espn_number
    var status = ' '

    if(field.withdrawn) {
        var status = 'WD' + ' '
        golfer_row.classList.add('started')
        }

    else if (! field.started || field.tournament.late_picks) {
        let inputA =  document.createElement('input');
            inputA.type = 'hidden';
            inputA.name = "csrfmiddlewaretoken";
            inputA.value  = $.cookie('csrftoken')
        golfer.appendChild(inputA)

        let inputB =  document.createElement('input');
            inputB.id = field.id
            inputB.type = input_type
            inputB.classList.add(input_class)
            inputB.name= "group-" + field.group.number
            inputB.value = field.id
            inputB.disabled = true
            inputB.addEventListener('change', function(evt) {
                        $('#pick-status').empty()
                        get_info(info, this);
                                                            });

            if (pick_array.indexOf(field.id) != -1) {
                inputB.checked = true
            }
             
            golfer.appendChild(inputB)
            golfer_row.classList.add('border', 'rounded', 'border-2')
            if (field.lock_group) {
                golfer_row.classList.add('lock')    
            }

                                                                }
    else if(field.started) {

        //clean this up, duplicte from above if
        let inputA =  document.createElement('input');
        inputA.type = 'hidden';
        inputA.name = "csrfmiddlewaretoken";
        inputA.value  = $.cookie('csrftoken')
    golfer.appendChild(inputA)

    let inputB =  document.createElement('input');
        inputB.id = field.id
        inputB.type = input_type
        inputB.classList.add(input_class)
        inputB.disabled = true
        inputB.name= "group-" + field.group.number
        inputB.value = field.id
        //inputB.addEventListener('change', function(evt) {
        //            $('#pick-status').empty()
        //            get_info(info, this);
        //                                                });

        if (pick_array.indexOf(field.id) != -1) {
            inputB.checked = true
        }
                                                            
        golfer.appendChild(inputB)

        var status = 'Started' + ' '
        golfer_row.classList.add('started')
                           // }
        if (field.lock_group) {
           golfer_row.classList.add('lock')    
                        }
    }
    else {
        var status = 'Problem' + ' '
        golfer_row.classList.add('started')
        }
        
    img = document.createElement('img')
    img.src = field.golfer.pic_link
    flag = document.createElement('img')
    flag.src = field.golfer.flag_link
    google = document.createElement('a')
    google.href = 'https://www.google.com/search?q=' + field.playerName
    google.target =  '_blank'
    google.innerHTML = " Google"
    espn = document.createElement('a')
    espn.href = field.espn_link
    espn.innerHTML = "/ESPN"
    espn.target =  '_blank'
    pga = document.createElement('a')
    pga.href = field.pga_link
    pga.innerHTML = "/PGA"
    pga.target =  '_blank'

    golfer.appendChild(img)
    if (field.withdrawn) {
        t = ' ' + field.playerName.strike() + ' ' + status}
    else if (field.started && ! field.tournament.late_picks) {
        t = ' ' + field.playerName.strike() + ' ' + status
                                                           }
    else {
        t = ' ' + field.playerName + ' ' + status
    }

    if (field.fedex_pick) {
        fedex = document.createElement('img')
        fedex.src = '/static/img/fedex.jpg'
        fedex.style.width = '30px'
        //fedex.style.border='1px solid lightblue';
        golfer.appendChild(fedex)
    }

    text = document.createElement('b')
    text.innerHTML = t
    golfer.append(text)
    
    golfer.appendChild(flag)
    golfer.appendChild(google)
    golfer.appendChild(espn)
    golfer.appendChild(pga)

    fed_ex_data = ''
    if (field.season_stats.fed_ex_rank == 'n/a') {
        fed_ex_data = 'n/a'
    }
    else {
        fed_ex_data = field.season_stats.fed_ex_rank + ' / ' + field.season_stats.fed_ex_points + ' pts.'
    }

    t1 = document.createElement('b')
    //t1.innerHTML = '      ' + 'OWGR: ' + field.currentWGR + ' ;  ' + 'Handicap: ' + field.handi + ' ; ' +  "Prior Year: " + field.prior_year

    expand = document.createElement('i')
        expand.classList.add('fa', 'fa-plus-circle', 'expand')
        //expand.style.color = 'white'
        expand.style.float= 'right'
        expand.innerHTML = 'Show Golfer Stats'
        expand.id = 'expand-' + field.id
        expand.addEventListener('click', function() {toggle_golfer_stats(field.id)})


    if ($(window).width() < 650) {
        p1 = document.createElement('p')
        p1.innerHTML = 'OWGR: ' + field.currentWGR + " ; Prior Year: " + field.prior_year
        p2 = document.createElement('p')
        p2.innerHTML = 'Handicap: ' + field.handi + ' ; FedEx: ' + fed_ex_data
        //p2a = document.createElement('p')
        //p2a.innerHTML = 'FedEx Rank: ' + field.season_stats.fed_ex_rank
        //p3 = document.createElement('p')
        //p3.innerHTML = "Prior Year: " + field.prior_year
        //t1.innerHTML = '      ' + 'OWGR: ' + field.currentWGR + ' ;  ' + 'Handicap: ' + field.handi + ' ; ' +  "Prior Year: " + field.prior_year
        t1.appendChild(p1)
        t1.appendChild(p2)
        //t1.appendChild(p2a)
        //t1.appendChild(p3)
                            }
    else {
        t1.innerHTML = '      ' + 'OWGR: ' + field.currentWGR + ' ;  ' + 'Handicap: ' + field.handi + ' ; ' + "FedEx: " +
        fed_ex_data + 
         ' ; ' + "Prior Year: " + field.prior_year
    }

    golfer.appendChild(t1)
    
    
        golfer.appendChild(expand)
    
    //    $('#expand-' + g).on('click', function() {
    //    toggle_stats_display(this, $('#tbl-group-' +g))
    //})


    golfer_row.appendChild(golfer)
    
    return golfer_row
}

function build_stats_row(field) {
    let stats_row = document.createElement('tr');
    stats_row.id = 'stats_row-' + field.id
    stats_row.style.width = '100%'
    stats_row.classList.add('stats_row')
    stats_row.setAttribute('hidden', true)
    stats_cell = document.createElement('td')
    stats_row.appendChild(stats_cell)
    let stats_table = document.createElement('table');
        stats_table.style.width = '100%'
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
                    sg_cellG.innerHTML = field.season_stats.putting.rank
                    stats_rowE.appendChild(sg_cellG)

                let sg_cellH = document.createElement('td')
                    sg_cellH.innerHTML = field.season_stats.putting.average
                    stats_rowE.appendChild(sg_cellH)
       
            }

            stats_table.appendChild(rowE_header)
            stats_table.appendChild(stats_rowE)
            
        stats_cell.append(stats_table)

        return stats_row
}

function  toggle_stats_display(ele, table) {
    t_id = table[0].id
    var toggle_ind = document.getElementById(ele.id).innerHTML.trim()
    
    if (toggle_ind == 'Show Group Stats') {
        $('#' + t_id + ' .stats_row').attr('hidden', false)
                ele.classList.remove('fa-plus-circle')
                ele.classList.add('fa-minus-circle')
                ele.innerHTML = 'Hide Group Stats'
        
        expand_l = table[0].getElementsByClassName('expand').length
        
        for (let i=0; i < expand_l; i++) {
            table[0].getElementsByClassName('expand')[i].classList.remove('fa-plus-circle')
            table[0].getElementsByClassName('expand')[i].classList.add('fa-minus-circle')
            table[0].getElementsByClassName('expand')[i].innerHTML = 'Hide Golfer Stats'
        }
            
        }
    else {$('#' + t_id + ' .stats_row').attr('hidden', true)
        ele.classList.remove('fa-minus-circle')
        ele.classList.add('fa-plus-circle')
        ele.innerHTML = 'Show Group Stats'

        expand_l = table[0].getElementsByClassName('expand').length
    
        for (let i=0; i < expand_l; i++) {
            table[0].getElementsByClassName('expand')[i].classList.remove('fa-minus-circle')
            table[0].getElementsByClassName('expand')[i].classList.add('fa-plus-circle')
            table[0].getElementsByClassName('expand')[i].innerHTML = 'Show Golfer Stats'
        }
        
            
        }
}

function toggle_golfer_stats(field_id) {
    
    indicator = document.getElementById('expand-' + field_id).innerHTML.trim()

    if (indicator == "Show Golfer Stats") {
        $('#stats_row-' + field_id).removeAttr('hidden')
        document.getElementById('expand-' + field_id).innerText = "Hide Golfer Stats"
        document.getElementById('expand-' + field_id).classList.remove('fa-plus-circle')
        document.getElementById('expand-' + field_id).classList.add('fa-minus-circle')
    }
    else {
        $('#stats_row-' + field_id).attr('hidden', true)
        document.getElementById('expand-' + field_id).innerText = "Show Golfer Stats"
        document.getElementById('expand-' + field_id).classList.remove('fa-minus-circle')
        document.getElementById('expand-' + field_id).classList.add('fa-plus-circle')

    }
}
