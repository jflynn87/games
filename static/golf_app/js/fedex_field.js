$(document).ready(function () {
    start = new Date()
    fetch("/golf_app/fedex_field")
    .then(response=> response.json())
    .then((responseJSON) => {
         field = responseJSON
         console.log(field)
         
         const frag = new DocumentFragment()

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
                c_3.innerHTML = g.prior_season_data.rank 

                row.appendChild(c_0)
                row.appendChild(c_1)
                row.appendChild(c_2)
                row.appendChild(c_3)
                table.appendChild(row)

         }
            frag.appendChild(table)
            document.getElementById('field').appendChild(frag);


         
     })
    })