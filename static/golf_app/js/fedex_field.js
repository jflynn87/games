$(document).ready(function () {
    start = new Date()
    $('#field').append('<p>Pick 30 the golfers who will make the Tour Championship</p> \
     <p>-30 points for any correct pick</p><p>Additional -50 for any pick that was outside the top 30 OWGR as of the start of the season</p> \
     <p>+20 for any pick that was in the top 30 OWGR but doesn' + "'" + 't make it</p> \
     <p>Total points included in season total like a regular tournament.</p> <br>')


    $('#field').append('<div><h4 id=loading_msg>Loading .... </h4></div>')
    fetch("/golf_app/fedex_field")
    .then(response=> response.json())
    .then((responseJSON) => {
         field = responseJSON
         console.log(field)
         
         const frag = new DocumentFragment()
         form = document.createElement('form')
         form.method = 'post'

         table = document.createElement('table')
         table.classList.add('table')
         header = document.createElement('thead')
             h_0 = document.createElement('th')
             h_0.innerHTML = 'Select'
             h_1 = document.createElement('th')
             h_1.innerHTML = 'Golfer'
             h_1.colSpan = 2
             h_2 = document.createElement('th')
             h_2.innerHTML = 'OWGR - start of year'
             h_3 = document.createElement('th')
             h_3.innerHTML = 'Prior FedEx Rank'

         header.appendChild(h_0)
         header.appendChild(h_1)
         header.appendChild(h_2)
         header.appendChild(h_3)
         table.appendChild(header)


         field_l = field.length

         for (let i=0; i < field_l; i++) {
             g = field[i]
             row = document.createElement('tr')
             row.id = g.id
                c_0 = document.createElement('td')

                let inputA =  document.createElement('input');
                inputA.type = 'hidden';
                inputA.name = "csrfmiddlewaretoken";
                inputA.value  = $.cookie('csrftoken')
                
    
                let inputB =  document.createElement('input');
                inputB.id = g.id
                inputB.type = 'checkbox'   
                inputB.classList.add('my-checkbox')
                inputB.name= g.id
                inputB.value = g.id
                //inputB.disabled = true
                inputB.addEventListener('change', function(evt) {
                            count_actual();
                                                                });
    
                //if (pick_array.indexOf(field.id) != -1) {
                //    inputB.checked = true
                // }
                c_0.appendChild(inputA)
                c_0.appendChild(inputB) 


                c_1 = document.createElement('td')
                img = document.createElement('img')
                img.src = g.golfer.pic_link

                //c_1.innerHTML = g.golfer.golfer_name


                flag = document.createElement('img')
                flag.src = g.golfer.flag_link

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

                row.appendChild(c_0)
                row.appendChild(c_1)
                row.appendChild(c_1a)
                row.appendChild(c_2)
                row.appendChild(c_3)
                table.appendChild(row)

         }
            sub_btn = document.createElement('button')
            sub_btn.id = 'sub_button'
            sub_btn.type = 'button'
            sub_btn.innerHTML = "0 of 30 Picks"
            sub_btn.disabled = true
            sub_btn.classList.add('btn', 'btn-secondary')
/*             $('#pick_form').on('submit', function(event){
                event.preventDefault();
                console.log("form submitted!")  
                create_post();
            });

 */         sub_btn.addEventListener('click', function(event) {
                    event.preventDefault();
                    create_post()                    
                });

            //form.appendChild(sub_btn)   
            $('#bottom_sect').append(sub_btn)
            form.appendChild(table)
            
            frag.appendChild(form)
            document.getElementById('loading_msg').hidden = true
            document.getElementById('field').appendChild(frag);


         
     })
    })

function create_post() {
    console.log('submit form')
    //toggle_submitting()    
    checked = $('input:checked')
    //console.log(checked)
    pick_list = []
    $.each(checked, function(i, pick){
        pick_list.push(pick.value)
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


function count_actual(group, picks) {
        var selected = $('input[class=my-checkbox]:checked').length
        console.log('selected', selected)
        $('#sub_button').text(selected + ' of 30 Picks')
        if (selected === 30) {
            $('#sub_button').removeAttr('disabled').attr('class', 'btn btn-primary').text('Submit Picks')
        }
        else {
            $('#sub_button').attr('disabled', true).attr('class', 'btn btn-secondary').text(selected + ' of 30 Picks')
        }
    return selected
  }
  