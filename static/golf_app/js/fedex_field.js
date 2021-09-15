$(document).ready(function () {
    start = new Date()
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
                //inputB.addEventListener('change', function(evt) {
                //            $('#pick-status').empty()
                //            get_info(info, this);
                //                                                });
    
                //if (pick_array.indexOf(field.id) != -1) {
                //    inputB.checked = true
                // }
                c_0.appendChild(inputA)
                c_0.appendChild(inputB) 


                c_1 = document.createElement('td')
                c_1.innerHTML = g.golfer.golfer_name
                c_2 = document.createElement('td')
                c_2.innerHTML = g.soy_owgr
                c_3 = document.createElement('td')
                if (g.prior_season_data.rank != undefined) {
                c_3.innerHTML = g.prior_season_data.rank }
                else {c_3.innerHTML = 'n/a'}

                row.appendChild(c_0)
                row.appendChild(c_1)
                row.appendChild(c_2)
                row.appendChild(c_3)
                table.appendChild(row)

         }
            sub_btn = document.createElement('button')
            sub_btn.id = 'sub_btn'
            sub_btn.type = 'button'
            sub_btn.innerHTML = "Submit Picks"
            sub_btn.classList.add('button', 'btn-primary')
/*             $('#pick_form').on('submit', function(event){
                event.preventDefault();
                console.log("form submitted!")  
                create_post();
            });

 */         sub_btn.addEventListener('click', function(event) {
                    event.preventDefault();
                    create_post()                    
                });

            form.appendChild(sub_btn)   

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