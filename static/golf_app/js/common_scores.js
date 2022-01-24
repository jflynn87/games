//let not_playing = ['CUT', 'WD', 'DQ']

function format_move(score) {

    if (score == null) {
      return '  '} 
      else if (Number.isInteger(score) && score > 0) {
        return '<i class="fa fa-arrow-down text-danger">'+ score + '</i>'  
      }
      else if (Number.isInteger(score) && score < 0) {
        return '<i class="fa fa-arrow-up text-success">' + score +'</i>'  
      }
      else if (Number.isInteger(score) && score == 0) {
        return '--'  
      }
      else if (score.includes('down')) {
      return '<i class="fa fa-arrow-down text-danger"></i>'
             } 
      else if (score.includes('up')) {
      return '<i class="fa fa-arrow-up text-success"></i>'
       } 
      else {return "  "}
  }
  
  function sort_table(tableId) {
    var table, rows, swtiching, i, x, y, shouldSwitch;
    table = $('#' + tableId)
    
    switching = true;
    
    while(switching) {
      switching = false;
      rows = table[0].rows;
      //console.log(rows.length)
      l = rows.length
      for (i=1; i < (l - 3); i++) {
        //console.log('for loop', i)
        shouldSwitch = false;
        
        x = rows[i].getElementsByTagName('td')[0].getElementsByTagName('p')[1].innerHTML.split('/')[0].replace(/\s/g, '');
        y = rows[i + 1].getElementsByTagName('td')[0].getElementsByTagName('p')[1].innerHTML.split('/')[0].replace(/\s/g, '');
        //console.log(x, y)
        
        if (Number(x) > Number(y)) {
          //console.log(i, Number(x), Number(y))
          shouldSwitch = true;
          break;
        }
      }
        if (shouldSwitch) {
          rows[i].parentNode.insertBefore(rows[i+1], rows[i]);
          switching = true;
        }
      }
    }


//works with ESPN API based data    
function buildLeaderboard(t) {
  return new Promise (function (resolve, reject) {
    fetch("/golf_app/get_pga_leaderboard/" + t,
    {method: "GET",
    }
          )
    .then((response) => response.json())
    .then((responseJSON) => {
          data = $.parseJSON(responseJSON).leaderboard
          //console.log(data)
          $('#det-list').empty()
          $('#det-list').append('<table id="det-table" class="table">' + '</table>');
        
          top_header_fields = ['Tournament Scores', ' ', '<a href="#"> <button> return to top</button> </a>', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
          thf_l = top_header_fields.length
          th_cells = []
          let top_header = document.createElement('tr')
          top_header.style.background = 'lightblue';
          for (let i=0; i < thf_l; i++) {
              th_cells.push(document.createElement('th'))
              th_cells[i].innerHTML = top_header_fields[i]
              top_header.append(th_cells[i])
                                        }
        
          second_header_fields = ['Position', 'Change ', 'Golfer', 'Total ', 'Thru ', 'Round', 'R1 ', 'R2 ', 'R3 ', 'R4']
          shf_l = top_header_fields.length
          sh_cells = []
          let second_header = document.createElement('tr');
          for (let i=0; i < shf_l; i++) {
            sh_cells.push(document.createElement('th'))
            sh_cells[i].innerHTML = second_header_fields[i]
            second_header.append(sh_cells[i])
                                        }
        
          const c = new DocumentFragment();
          data_l = Object.keys(data).length;
          values = Object.values(data)
          for (let i=1; i <= data_l; i++) {
            let d = data[i]
            let row_fields = [d.rank, d.change, d.golfer_name, d.total_score, d.thru, d.curr_round_score, 
                                d.r1, d.r2, d.r3, d.r4]
              
              let row_fields_l = row_fields.length
              let row = document.createElement('tr')
              row.classList.add('small');
        
              row_cells = []
              for (let j=0; j< row_fields_l; j++) {

                row_cells.push(document.createElement('td'))
                if (j == 1) {arrow = format_move(row_fields[j])
                          row_cells[j].innerHTML == row_fields[j]
                        row_cells[j].innerHTML = arrow}
                else if (j == 2) {row_cells[j].innerHTML = row_fields[j]
                              row_cells[j].style.fontWeight = 'bold' }
                else if (j==4 && row_fields[j].toString().length <  4){
                  row_cells[j].innerHTML = row_fields[j]
                }
                else if (j == 4 && row_fields[j].slice(-1) == 'Z') {
                      var utcDate = row_fields[j];
                      row_cells[j].innerHTML = new Date (utcDate).toLocaleTimeString([], {hour: 'numeric', minute:'2-digit'})
                      
                    }
                else {row_cells[j].innerHTML = row_fields[j]}
  
                row.append(row_cells[j])
                                                  }
              c.appendChild(row)
          
                                }
                                          
         
            document.getElementById('det-table').appendChild(top_header)
            document.getElementById('det-table').appendChild(second_header)
            document.getElementById('det-table').appendChild(c)
          
            $('#det-list').attr('class', 'none')
        
                  resolve(data)})

})
}



    