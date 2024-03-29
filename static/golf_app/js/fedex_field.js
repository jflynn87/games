$(document).ready(function () {
    start = new Date()


    if ($('#allow_picks').text() == 'true') {
        $('#intro').append('<p>Pick 30 the golfers who will make the Tour Championship</p>')
        //$('#field').append('<div><h4 id=loading_msg>Loading .... </h4></div>')
        $('#all_picks').hide()
        user_picks()
    }
    else {
        $('#field').hide()
        //$('#all_picks').append('<div><h4 id=loading_msg>Loading .... </h4></div>')
        //get_all_picks()  maybe figure out how to toggle to this 
        score_view()
    }
    $('#intro').append('<p>-30 points for any correct pick</p><p>Additional -50 for any pick that was outside the top 30 OWGR as of the start of the season</p> \
    <p>+20 for any pick that was in the top 30 OWGR but doesn' + "'" + 't make it</p> \
    <p>Total points included in season total like a regular tournament.</p> <br>')
    $('#intro').append('<p>Field and fantasy data sourced from <a href=https://www.pgatour.com/news/2022/09/08/2022-2023-pga-tour-full-membership-fantasy-rankings.html> this link</a>.  OWGR from owgr website as of start of 2022/2023 season</p>')

})
    
function user_picks() {
    fetch("/golf_app/fedex_field" + '/player')
    .then(response=> response.json())
    .then((responseJSON) => {
         field = responseJSON
         console.log(field)
         //get_all_picks()
         
         const frag = new DocumentFragment()
         top_30 = document.createElement('div')
         top_30.classList.add('form-check')
            
            top_30_input = document.createElement('input')
            top_30_input.type = 'checkbox'   
            top_30_input.id = 'top_30'
            top_30_input.classList.add('form-check-input')
            top_30_input.addEventListener('click', function(evt) {
                checked_items = $('input[name^=owgr]:checked').length
                if (checked_items === 30) {
                    $('input[name^=owgr]:checked').attr('checked', false)
                    $('input[name^=owgr]:checked').attr('checked', '')
                }
                else {
                l = 41  //figure out how to count the owgr of the #30 golfer rather than manually setting here
                for (let i=0; i < l; i++){
                    $('input[name=owgr-' + i).attr('checked', true)
                                        }    
                }
                count_actual()
            })
            label = document.createElement('label')
            label.setAttribute('for', 'top_30')
            label.innerText = 'Select top 30 OWGR'
            label.classList.add('form-check-label')
            label.style.fontWeight = 'bold'
            
            if ($('#allow_picks').text() == 'false') {
                top_30_input.disabled = true
            }

            top_30.appendChild(top_30_input)

            top_30.appendChild(label)
            
        frag.appendChild(top_30)

         form = document.createElement('form')
         form.method = 'post'
         
         table = document.createElement('table')
         table.id = 'fedex_table'
         table.classList.add('table')
         header = document.createElement('thead')
             h_0 = document.createElement('th')
             h_0.innerHTML = 'Select Top 30'
             h_0_a = document.createElement('th')
             h_0_a.innerHTML = 'Select Top 3'
   
             h_1 = document.createElement('th')
             h_1.innerHTML = 'Golfer'
             h_1.colSpan = 2
             h_2 = document.createElement('th')
             h_2.id = 'curr_owgr'
             h_2.innerHTML = 'Start of Year OWGR'
             h_2_i = document.createElement('i')
             h_2_i.classList.add("fas", "fa-sort")
             h_2.appendChild(h_2_i)
             h_2.addEventListener('click', function(evt) {
                th = this
                const cell_i = 3
                const order = document.getElementById('curr_owgr_sort').innerHTML
                sort_table($('#fedex_table'), cell_i, order);  //index or pointer to clicked cell
                if (document.getElementById('curr_owgr_sort').innerHTML == 'asc') {
                    document.getElementById('curr_owgr_sort').innerHTML = 'desc'
                }
                else {document.getElementById('curr_owgr_sort').innerHTML = 'asc'}
                
                                                    });



             h_3 = document.createElement('th')
             h_3.id = 'prior_fedex'
             h_3.innerHTML = 'Prior Season FedEx Rank'
             h_3_i = document.createElement('i')
             h_3_i.classList.add("fas", "fa-sort")
             h_3.appendChild(h_3_i)

             h_3.addEventListener('click', function(evt) {
                th = this
                const cell_i = 4
                const order = document.getElementById('prior_fedex_sort').innerHTML
                sort_table($('#fedex_table'), cell_i, order);  //index or pointer to clicked cell
                if (document.getElementById('prior_fedex_sort').innerHTML == 'asc') {
                    document.getElementById('prior_fedex_sort').innerHTML = 'desc'
                }
                else {document.getElementById('prior_fedex_sort').innerHTML = 'asc'}
                
                                                    });


            h_3_a = document.createElement('th')
            h_3_a.innerHTML = 'Last Season Played'                                                         
            
            h_3_b = document.createElement('th')
            h_3_b.innerHTML = 'Qualification Method'                                                        
                                        
            h_3_c = document.createElement('th')
            h_3_c.innerHTML = 'Fantasy Projection'                                                        
                                       

             h_4 = document.createElement('th')
             //h_4.id = 'prior_owgr'
             h_4.innerHTML = 'Fantasy Comments'
             //h_4_i = document.createElement('i')
             //h_4_i.classList.add("fas", "fa-sort")
             //h_4.appendChild(h_4_i)

             //h_4.addEventListener('click', function(evt) {
             //   th = this
             //   const cell_i = 5
             //   const order = document.getElementById('prior_season_owgr_sort').innerHTML
             //   sort_table($('#fedex_table'), cell_i, order);  //index or pointer to clicked cell
             //   if (document.getElementById('prior_season_owgr_sort').innerHTML == 'asc') {
             //       document.getElementById('prior_season_owgr_sort').innerHTML = 'desc'
             //   }
             //   else {document.getElementById('prior_season_owgr_sort').innerHTML = 'asc'}
             //   
             //                                      });



         curr_owgr_sort = document.createElement('p')
            curr_owgr_sort.id = 'curr_owgr_sort'
            curr_owgr_sort.innerHTML = 'asc'
            curr_owgr_sort.hidden = true
         prior_fedex_sort = document.createElement('p')
            prior_fedex_sort.id = 'prior_fedex_sort'
            prior_fedex_sort.innerHTML = 'asc'
            prior_fedex_sort.hidden = true

        //  prior_season_owgr_sort = document.createElement('p')
        //     prior_season_owgr_sort.id = 'prior_season_owgr_sort'
        //     prior_season_owgr_sort.innerHTML = 'asc'
        //     prior_season_owgr_sort.hidden = true

         header.appendChild(h_0)
         header.appendChild(h_0_a)
         header.appendChild(h_1)
         header.appendChild(h_2)
         header.appendChild(h_3)
         header.appendChild(h_3_a)
         header.appendChild(h_3_b)
         header.appendChild(h_3_c)
         header.appendChild(h_4)
         table.appendChild(header)

        t_body = document.createElement('tbody')                                                    
      

         field_l = field.length

         for (let i=0; i < field_l; i++) {
             g = field[i]
             row = document.createElement('tr')
             row.id = 'row' + g.id
                c_0 = document.createElement('td')

                let inputA =  document.createElement('input');
                inputA.type = 'hidden';
                inputA.name = "csrfmiddlewaretoken";
                inputA.value  = $.cookie('csrftoken')

    
                let inputB =  document.createElement('input');
                inputB.id = g.id
                inputB.type = 'checkbox'   
                inputB.classList.add('my-checkbox', 'top-30')
                inputB.name= 'owgr-' + g.soy_owgr
                inputB.value = g.id

                if (g.picked) {
                    inputB.checked = true
                }

                if ($('#allow_picks').text() == 'false') {
                            inputB.disabled = true }

                inputB.addEventListener('change', function(evt) {
                            count_actual(this);
                                                                });

                c_0_a = document.createElement('td')
                let inputC =  document.createElement('input');
                inputC.id = g.id + '_top3'
                inputC.type = 'checkbox'   
                inputC.classList.add('my-checkbox', 'top_3')
                inputC.name= 'top3-' + g.soy_owgr
                inputC.value = g.id

                if (g.top_3) {
                    inputC.checked = true
                }

                if ($('#allow_picks').text() == 'false') {
                    inputC.disabled = true }


                inputC.addEventListener('change', function(evt) {
                    count_actual(this);
                                                        });

                c_0.appendChild(inputA)
                c_0.appendChild(inputB) 
                c_0_a.appendChild(inputC) 

                c_1 = document.createElement('td')
                img = document.createElement('img')
                if (typeof(g.golfer.pic_link) === 'string')
                {img.src = g.golfer.pic_link}
                else
                 {img.src = 'https://www.pgatour.com/etc/designs/pgatour-libs/img/flags/24x24/USA.png'}

                flag = document.createElement('img')
                //console.log(g.golfer.flag_link, typeof(g.golfer.flag_link))
                
                if (typeof(g.golfer.flag_link) === 'string') {
                      
                    flag.src = g.golfer.flag_link }
                                    
                else {console.log(g, 'IN ELSE ') 
                    flag.src = ''}
                
                c_1.append(img)
                c_1.append(flag)
                c_1a = document.createElement('td')
                c_1a.innerText = g.golfer.golfer_name


                c_2 = document.createElement('td')
                c_2.innerHTML = g.soy_owgr
                c_3 = document.createElement('td')
                if (g.prior_season_data.rank != undefined) {
                c_3.innerHTML = g.prior_season_data.rank }
                else {c_3.innerHTML = 'n/a'}

                c_3_a = document.createElement('td')
                c_3_a.innerHTML = g.prior_season_data.starts

                c_3_b = document.createElement('td')
                c_3_b.innerHTML = g.prior_season_data.status

                c_3_c = document.createElement('td')
                c_3_c.innerHTML = g.prior_season_data.fantasy_rank
                
                c_4 = document.createElement('td')
                //c_4.innerHTML = g.prior_owgr
                c_4.innerHTML = g.prior_season_data.comment

                row.appendChild(c_0)
                row.appendChild(c_0_a)
                row.appendChild(c_1)
                row.appendChild(c_1a)
                row.appendChild(c_2)
                row.appendChild(c_3)
                row.appendChild(c_3_a)
                row.appendChild(c_3_b)
                row.appendChild(c_3_c)
                row.appendChild(c_4)
                t_body.appendChild(row)

         }
            if ($('#allow_picks').text() == 'true') {
                console.log('allow picks')
                sub_btn = document.createElement('button')
                sub_btn.id = 'sub_button'
                sub_btn.type = 'button'
                sub_btn.innerHTML = "0 of 30 Picks"
                sub_btn.disabled = true
                sub_btn.classList.add('btn', 'btn-secondary')
    
              sub_btn.addEventListener('click', function(event) {
                        event.preventDefault();
                        create_post()                    
                    });
    
            }
            else {console.log('picks closed')
                    sub_btn = document.createElement('button')
                    sub_btn.classList.add('btn', 'btn-secondary')
                    sub_btn.innerHTML = 'Too Late for Picks'
                }


            //form.appendChild(sub_btn)   
            $('#bottom_sect').append(sub_btn)
            table.appendChild(t_body)
            form.appendChild(table)
            
            frag.appendChild(form)
            
            //document.getElementById('loading_msg').hidden = true
            document.getElementById('status').hidden = true
            document.getElementById('field').appendChild(frag);
            document.getElementById('field').append(curr_owgr_sort)
            document.getElementById('field').append(prior_fedex_sort)
            //document.getElementById('field').append(prior_season_owgr_sort)
            count_actual()
            $('#field').attr('hidden', false)
        })
    
}


function create_post() {
    console.log('submit form')
    $('#sub_button').attr('disabled', true).text('Submitting...')
    //toggle_submitting()    
    checked = $('input[class="my-checkbox top-30"]:checked')
    //console.log(checked)
    pick_list = []
    $.each(checked, function(i, pick){
        pick_list.push(pick.value)
    })
    top3 = $('input[class="my-checkbox top_3"]:checked')
    top3_list = []
    $.each(top3, function(i, pick){
        console.log('top3', pick)
        top3_list.push(pick.value)
    })

    console.log(pick_list)
    fetch("/golf_app/fedex_picks_view/",         
    {method: "POST",
     headers: {
     'Accept': 'application/json',
     'Content-Type': 'application/json',
     'X-CSRFToken': $.cookie('csrftoken')
             },
     body: JSON.stringify({'pick_list': pick_list, 
                           'top3_list': top3_list
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


function count_actual(ele) {
        var selected = $('input[class="my-checkbox top-30"]:checked').length
        var top3_selected = $('input[class="my-checkbox top_3"]:checked').length
        
        if (ele && selected > 30) {
            alert('top 30 - 30 already picked, deselect one pick');
            console.log(ele)
            ele.checked = false;
            selected = $('input[class="my-checkbox top-30"]:checked').length
                                            
        }

        if (ele && top3_selected > 3){
            alert('Top 3 - 3 already picked, deselect one pick');
            console.log(ele)
            ele.checked = false;
            selected = $('input[class="my-checkbox top-30"]:checked').length
                                            
        }

        console.log('picks selected', selected, top3_selected)

        if (selected  >= 30 && top3_selected >= 3) {
            $('#sub_button').removeAttr('disabled').attr('class', 'btn btn-primary').text('Submit Picks')
        }
        else {
            $('#sub_button').attr('disabled', true).attr('class', 'btn btn-secondary').text((selected + top3_selected) + ' of 33 Picks')
        }
    return selected
  }

// function count_top3(ele) {
//     var selected = $('input[class="my-checkbox top_3"]:checked').length
    
//     if (ele && selected > 3) {
//         alert('Top 3 already picked, deselect one pick');
//         console.log(ele)
//         ele.checked = false;
//         selected = $('input[class="my-checkbox top_3"]:checked').length
                                        
//     }
//     console.log('top3 selected', selected)
//     //$('#sub_button').text(selected + ' of 30 Picks')
//     if (selected === 3 && top30 == 3) {
//         $('#sub_button').removeAttr('disabled').attr('class', 'btn btn-primary').text('Submit Picks')
//     }
//     else {
//         $('#sub_button').attr('disabled', true).attr('class', 'btn btn-secondary').text(selected + ' of 30 Picks')
//     }
// return selected
// }


function sort_table(table, cell_i, order) {
    
    const tRows = Array.from(table[0].rows)
    tRows.sort( ( x, y) => {
        //console.log(x.cells[cell_i].innerHTML, x.cells[cell_i].innerHTML.length)
        if (x.cells[cell_i].innerHTML != '' && x.cells[cell_i].innerHTML != 'n/a') {
        var xValue = x.cells[cell_i].innerHTML;}
        else {var xValue = '999'}

        if (y.cells[cell_i].innerHTML != '' && y.cells[cell_i].innerHTML != 'n/a') {
        var yValue = y.cells[cell_i].innerHTML; }
        else {var yValue = '999'}
        
       // console.log(xValue, yValue)

        const xNum = parseInt( xValue );
        const yNum = parseInt( yValue );
        var ascending = true
        if (order != 'asc') {var ascending = false}
        return ascending ? ( xNum - yNum ) : ( yNum - xNum );

    })
        
    for( let row of tRows ) {
        table[0].appendChild( row );

    }

}

function toggle_picks() {
    if ($('#picks_toggle').text() == 'Show All Picks') {
    $('#field').hide()
    $('#picks_toggle').text('Show My Picks')
    $('#picks_toggle').removeClass("fa-toggle-on")
    $('#picks_toggle').addClass("fa-toggle-off")
    }
    else if ($('#picks_toggle').text() == 'Show My Picks') {
        $('#field').show()
        $('#picks_toggle').text('Show All Picks')
        $('#picks_toggle').removeClass("fa-toggle-off")
        $('#picks_toggle').addClass("fa-toggle-on")
                                                        }
}

function get_all_picks() {
    fetch("/golf_app/fedex_field" + '/all')
    .then(response=> response.json())
    .then((responseJSON) => {
        picks = responseJSON.picks
        users = $.parseJSON(responseJSON.users)

        //console.log(picks)
        //console.log(users)
        console.log('get_all_picks')
        console.log($('#allow_picks').text())
        if ($('#allow_picks').text() == "true") {
            console.log('if')
            //new logic
        }
        else {

        const picks_frag = new DocumentFragment()

        pick_tbl = document.createElement('table')
        pick_tbl.classList.add('table', 'table-sm', 'table-bordered', 'table-stripped')
        pick_tbl.id = 'all_picks_tbl'
        header = document.createElement('thead')
        
        th0 = document.createElement('th')
        th0.innerHTML = 'Golfer'
        th0a = document.createElement('th')
        th0a.innerHTML = 'SoY OWGR'
        th0b = document.createElement('th')
        th0b.innerHTML = 'Points'

        th1 = document.createElement('th')
        th1.innerHTML = '# Picks'
        th2 = document.createElement('th')
        th2.innerHTML = 'Rank/Points'

        header.appendChild(th0)
        header.appendChild(th0a)
        header.appendChild(th0b)
        header.appendChild(th1)
        header.appendChild(th2)

        user_l = users.length

        if ($(window).width() > 649) {
        var user_order = []
        $.each(users, function(i, user) {
            th = document.createElement('th')
            th.innerHTML = user.fields.username
            header.appendChild(th)
            user_order.push(user.fields.username)
        })
            }
        else {th = document.createElement('th')
                th.innerHTML = 'Picked By'
                header.appendChild(th)}
        

        body = document.createElement('tbody')
        $.each(picks, function(espn_num, data) {
            tr = document.createElement('tr')
            tdA = document.createElement('td')
            tdA.innerHTML = data.golfer
            tdA1 = document.createElement('td')
            tdA1.innerHTML = data.soy_owgr
            tdA10 = document.createElement('td')
            tdA10.innerHTML = data.score


            tdB = document.createElement('td')
            tdB.innerHTML = data.num_picks
            tdC = document.createElement('td')
            if (data.rank)
            {tdC.innerHTML = data.rank + ' / ' + data.points}

            tr.appendChild(tdA)
            tr.appendChild(tdA1)
            tr.appendChild(tdA10)
            tr.appendChild(tdB)
            tr.appendChild(tdC)

            if ($(window).width() > 649) {
            for (let i=0; i < user_l; i++) {
                user_td = document.createElement('td')
                if (data.picked_by.indexOf(user_order[i]) != -1) {
                    user_td_i = document.createElement('i')
                    user_td_i.classList.add("fas", "fa-check")
                    user_td_i.style.color = 'green'
                    user_td_i.innerHTML = user_order[i]
                    user_td.appendChild(user_td_i)
       
                }
                else {user_td.innerHTML = ''}
                tr.appendChild(user_td)
            }            
            }
            else {
                user_td = document.createElement('td')
                if (data.num_picks == user_l) {
                    user_td.innerHTML = 'All'
                }
                else if (parseInt(data.num_picks) >= parseInt(user_l) / 2) {
                    //console.log(users)
                    top_p = document.createElement('p')
                    bot_p = document.createElement('p')

                    for (const u in Object.values(users)){
                        console.log(users[u].fields.username)
                        p = document.createElement('p')
                        p.innerHTML = users[u].fields.username
                        if (data.picked_by.indexOf(users[u].fields.username) == -1) {
                            p.style.textDecoration = 'line-through'
                            bot_p.appendChild(p)
                        }
                        else {
                            p.style.color = 'green'
                            top_p.appendChild(p)
                        }
                        user_td.appendChild(top_p)
                        user_td.appendChild(bot_p)
                    }
                    
                }
                else {
                for (let i=0; i < data.picked_by.length; i++) {
                    p = document.createElement('p')
                    p.innerHTML = data.picked_by[i]
                    user_td.appendChild(p)
                }
            }
                tr.appendChild(user_td)
            }

            body.appendChild(tr)
        
        
        })
       
    
    

        pick_tbl.appendChild(header)
        pick_tbl.appendChild(body)
        picks_frag.appendChild(pick_tbl)
        document.getElementById('all_picks').appendChild(picks_frag)
        sort_table($('#all_picks_tbl'), 3, 'asc')
        $('#status').attr('hidden', true)
        $('#all+picks_tbl').attr('hidden', false)
        $('#loading_msg').hide()
    
}

})
}

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