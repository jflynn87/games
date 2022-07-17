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
      //$('#field_stats_update_status').text('Updating....')
      const fieldKeys = getFeldKeys()
      fieldKeys
      //.then((response) => response.json())
      .then((responseJSON) => {
            keys = responseJSON
      console.log('back from funct: ', keys)
      var firstField = keys.first_field_key
      var lastField = keys.last_field_key
      //var firstField = Number($('#first_field_key').text())
      //var lastField = Number($('#last_field_key').text())
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
            $('#setup_table tbody').append('<tr id=field_update' + i + '><td>Updating Field batch ' + i + ' pk range: ' +  updateRange +  
                                          '</td><td id=field_update' + i + '-status>updating....</td>')              
            fetch("/golf_app/field_updates/" + updateRange[0].toString() + "/" + updateRange[1].toString(), 
            {method: "GET",
                  }
                  )
            .then((response) => response.json())
            .then((responseJSON) => {
            data = responseJSON
            console.log(data)
            $('#field_update' + i + '-status').html('Complete')
           
            })
            .then((response) => {
                  console.log('all field updates done, resolving')
                  resolve()
                        })
                        
                  }
      
      })

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
          var loop_s = 100
          var loops =  Math.floor(Number(lastGolfer-firstGolfer)/loop_s)
          remainder = Number(lastGolfer-firstGolfer)%200
          //console.log('loops: ', loops, remainder)
          //$('#setup_table tr:last').after('<tr id=all_golfers_status><td>Updating all golfers</td><td>' + 0 + '</td></tr>')
          
          for (let i=1; i <= loops; i++) {
            //var updateRange = []  
            if (i == 1) {
                  updateRange = [firstGolfer, firstGolfer + loop_s]
            }
            else if (i == loops) {
                  updateRange = [firstGolfer + (loop_s *(i-1)+1), lastGolfer]}
            else {updateRange = [firstGolfer + (loop_s *(i-1)+1), firstGolfer + (loop_s * i)]}
            console.log(i, updateRange)        
            console.log(typeof(updateRange[0].toString()), updateRange[0].toString().length, updateRange[1].toString())
            $('#setup_table tbody').append('<tr id=golfers_update' + i + '><td>Updating Golfers batch ' + i + ' pk range: ' +  updateRange +  
            '</td><td id=golfers_update' + i + '-status>updating....</td>')              
                
            fetch("/golf_app/golfer_results_updates/" + updateRange[0].toString() + "/" + updateRange[1].toString(), 
            {method: "GET",
                  }
                  )
            .then((response) => response.json())
            .then((responseJSON) => {
            data = responseJSON
            console.log(data)
            $('#golfers_update' + i + '-status').html('Complete')
           
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

function getFeldKeys() { 
      console.log('getFieldKeys')
      return new Promise (function (resolve, reject) { 
            fetch("/golf_app/get_field_keys_api/", 
              {method: "GET",
                    }
                    )
              .then((response) => response.json())
              .then((responseJSON) => {
              data = responseJSON
              console.log('field keys api result: ', data)
              console.log('resolving field keys')
              resolve(data)
                
             
              })
      
  })
  
}
