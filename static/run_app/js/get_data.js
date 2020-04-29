$( document ).ready(function() {
  
  get_run_data()


function get_run_data() {
    console.log('get data', new Date())
    $('#status').text('Updating .....')
    $.ajax({
        type: "GET",
        url: "/run_app/get_run_data/",
        /* data: {'tournament' : $('#tournament_key').text()}, */
        dataType: 'json',
        success: function (data) {
                console.log(data)
                $('#status').text('Update Complete')   
                console.log('done', new Date())
              },
        failure: function(data) {
          console.log('fail');
          console.log(json_update);
          $('#status').text('Update Fail')
          console.log('failed done', new Date())
        }
      })
    }
  })