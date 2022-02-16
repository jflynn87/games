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
    fetch("/golf_app/field_updates/", 
    {method: "GET",
    }
          )
    .then((response) => response.json())
    .then((responseJSON) => {
          data = responseJSON
          console.log(data)
          $('#field_stats_update_status').text('Complete')
          resolve()
    })

})
}

function golferResultsUpdates() {
    console.log('golfer update')
    return new Promise (function (resolve, reject) {
      $('#golfer_stats_update_status').text('Updating....')
    fetch("/golf_app/golfer_results_updates/", 
    {method: "GET",
    }
          )
    .then((response) => response.json())
    .then((responseJSON) => {
          data = responseJSON
          console.log(data)
          $('#golfer_stats_update_status').text('Complete')
            resolve()
    })

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