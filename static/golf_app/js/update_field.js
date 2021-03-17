$(document).ready(function() {
         
    $.ajax({
        type: "GET",
        url: "/golf_app/get_field_csv/",
        dataType: 'json',
        data: {'tournament' : $('#t_key').text()},
        success: function (json) {
            golfers = $.parseJSON(json)
            console.log(golfers)
            update_groups(golfers)
        },
        failure: function(json) {
            console.log('get field failed')
            console.log(json)
        }
})
})

function update_groups(golfers) {
    $.each(golfers, function(i, golfer) {
        
    })
    table = document.getElementById('field-tbl')
    for (var i=1; i < table.rows.length; i++) {
        golfer = golfers[]
    }

}
