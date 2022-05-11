$(document).ready(function () {
    console.log($('#db_t_num').text(), $('#pga_t_num').val())
    if ($('#db_t_num').text() == $('#pga_t_num').val()) {
        $('#pga_t_num').css("background-color", "salmon")
        
    }

    $('#sub-button').click(function() {
        
        //$('#status').append('<p id=field_status>Loading Field...</p>')
        const field = buildField();
        field.then((response) => {//$('#field_status').text("Field Loaded, moving to other functioms");
                                
                                const fUpdates = fieldUpdates()
                                fUpdates.then((response) => {
                                const gResultsUpdate  = golferResultsUpdates()
                                gResultsUpdate.then((response) => {
                                          checkSDs()
                                    })}
                                )
                              }
                                //need a promise here 
                                //summaryStats()}
        )
        })
})

function buildField() {
    return new Promise (function (resolve, reject) {
      $('#field_setup_status').text('Updating....')
        fetch("/golf_app/build_field/",
        {method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': $.cookie('csrftoken')
                    },
        body: JSON.stringify({'pga_t_num': $('#pga_t_num').val(),
                              'espn_t_num': $('#espn_t_num').val()
                              })

        }
              )
        .then((response) => response.json())
        .then((responseJSON) => {
              
              data = responseJSON
              $('#field_setup_status').text('Complete')
              resolve()              
  }
  
)

})
}

function fieldUpdates() {
return new Promise(function (resolve,reject) {
      $('#field_stats_update_status').text('Updating....')
      var firstField = Number($('#first_field_key').text())
      var lastField = Number($('#last_field_key').text())
      console.log('field keys: ', lastField, firstField)
      var loops =  Math.floor(Number(lastField-firstField)/20)
      remainder = Number(lastField-firstField)%20
      for (let i=1; i <= loops; i++) {
            //var updateRange = []  
            if (i == 1) {
                  updateRange = [firstField, firstField + 20]
            }
            else if (i == loops) {
                  updateRange = [firstField + (20 *(i-1)+1), lastField]}
            else {updateRange = [firstField + (20 *(i-1)+1), firstField + (20 * i)]}
            console.log(i, updateRange)        
            console.log(typeof(updateRange[0].toString()), updateRange[0].toString().length, updateRange[1].toString())
              
            fetch("/golf_app/field_updates/" + updateRange[0].toString() + "/" + updateRange[1].toString(), 
            {method: "GET",
                  }
                  )
            .then((response) => response.json())
            .then((responseJSON) => {
            data = responseJSON
            console.log(data)
            //$('#golfer_stats_update_status').text('Complete')
           
            })
            .then((response) => {
                  console.log('all field updates done, resolving')
                  resolve()
                        })
                        
      }

//       fetch("/golf_app/field_updates/", 
//     {method: "GET",
//     }
//           )
//     .then((response) => response.json())
//     .then((responseJSON) => {
//           data = responseJSON
//           console.log(data)
//           $('#field_stats_update_status').text('Complete')
//           resolve()
//     })
      //console.log('all field updates done, resolving')
      //resolve()

})
}

function golferResultsUpdates() {
    console.log('golfer update', $('#total_golfers').text())
    return new Promise (function (resolve, reject) { 
          var firstGolfer = Number($('#first_golfer_key').text())
          var lastGolfer = Number($('#last_golfer_key').text())
          console.log('Golfer Keys: ', lastGolfer, firstGolfer)
          var loops =  Math.floor(Number(lastGolfer-firstGolfer)/200)
          remainder = Number(lastGolfer-firstGolfer)%200
          //console.log('loops: ', loops, remainder)
          $('#setup_table tr:last').after('<tr id=all_golfers_status><td>Updating all golfers</td><td>' + 0 + '</td></tr>')
          for (let i=1; i <= loops; i++) {
            //var updateRange = []  
            if (i == 1) {
                  updateRange = [firstGolfer, firstGolfer + 200]
            }
            else if (i == loops) {
                  updateRange = [firstGolfer + (200 *(i-1)+1), lastGolfer]}
            else {updateRange = [firstGolfer + (200 *(i-1)+1), firstGolfer + (200 * i)]}
            console.log(i, updateRange)        
            console.log(typeof(updateRange[0].toString()), updateRange[0].toString().length, updateRange[1].toString())
              
            fetch("/golf_app/golfer_results_updates/" + updateRange[0].toString() + "/" + updateRange[1].toString(), 
            {method: "GET",
                  }
                  )
            .then((response) => response.json())
            .then((responseJSON) => {
            data = responseJSON
            console.log(data)
            //$('#golfer_stats_update_status').text('Complete')
           
            })
      }
          console.log('resolving golfer update')
          resolve()
    
})
}

function checkSDs() {
      fetch("/golf_app/sds_status/", 
      {method: "GET",
      }
            )
      .then((response) => response.json())
      .then((responseJSON) => {
            data = $.parseJSON(responseJSON)
            console.log(data)
            $.each(data, function (t, status) {
                  $('#sd_status_tbody').append('<tr><td>' + t + '</td><td>' + status.sd_valid + '</td>')
            })
  
            
  })
  
}


function summaryStats() {
    $('#status').append('<p id=field-updates>Getting Summary data....</p>');
    fetch("/golf_app/setup_summary_data/", 
    {method: "GET",
    }
          )
    .then((response) => response.json())
    .then((responseJSON) => {
          data = responseJSON
          console.log(data)
          $('#field-updates').append('<p>Data goes here</p>')


})

}

function emailReport(dist) {
      fetch("/golf_app/fedex_send_summary_email_api/" + dist, 
      {method: "GET",
      }
            )
      .then((response) => response.json())
      .then((responseJSON) => {
            data = responseJSON
            console.log('email: ', data)
 
            
  })
  
}
