$(document).ready(function() {
    console.log('first step');
    $('#picks-tbl').hide()
  
    $.ajax({
      type: "GET",
      url: "/golf_app/ajax/get_scores/",
      dataType: 'json',
      //context: document.body
      success: function (json) {
        console.log('connected');
        
        var i;
        for (i = 0; i < json.length; ++i) {
            console.log(json[i])
            console.log(json[i][0], json[i][1], json[i][2])
            $('#picks-tbl').find('tbody')
           .append($('<tr>')
           .append($('<td>').text((json[i][0])))
           .append($('<td>').text((json[i][1])))
           .append($('<td>').text((json[i][2])))
                                                )}
            $('#pulse').hide()
            $('#picks-tbl').show()

                                            },
      failure: function(json) {
        console.log('fail');
        console.log(json);
      }
    })
  
})

  