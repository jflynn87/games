$(document).ready(function () {
    console.log($('#db_t_num').text(), $('#pga_t_num').val())
    if ($('#db_t_num').text() == $('#pga_t_num').val()) {
        $('#pga_t_num').css("background-color", "salmon")
        
    }

    $('#sub-button').click(function() {
        
        $('#status').append('<p id=field_status>Loading Field...</p>')
        const field = buildField();
        field.then((response) => {$('#field_status').text("Field Loaded");
                                
                                fieldUpdates()}
        )
        })
})

function buildField() {
    return new Promise (function (resolve, reject) {
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
              console.log('build field api returned')
              data = responseJSON
              console.log(data)
              resolve()              
  }
  
)

})
}

function fieldUpdates() {
    $('#status').append('<p id=field-updates>Updating Stats....</p>');
    fetch("/golf_app/field_updates/", 
    {method: "GET",
    }
          )
    .then((response) => response.json())
    .then((responseJSON) => {
          data = responseJSON
          console.log(data)
          $('#field-updates').text("Updates complete, Field complete")


})
}
    
