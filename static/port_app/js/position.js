$(document).ready(function() {
  $('#search').keyup(function() {
    $('#result').html('');
    var searchField = $('#search').val();
    var expression = new RegExp(searchField, "i");
    $.ajax({
      type: "GET",
      url: "/port_app/ajax/symbol_lookup/",
      dataType: 'json',
      data: {'symbol': searchField},
      success: function (json) {
        console.log(searchField);
        data = json['bestMatches']
        $.each(data, function(key, value) {
          //$('#result').append('<li class="list-group-item">' + value['2. name'] + ' - ' + value['1. symbol'])
          var ticker = value['1. symbol']
          $('#result').append('<li class="list-group-item"' + 'value="' + ticker + '" >' + value['2. name'] + ' - ' + value['1. symbol'])
        })
          $('#result li').on('click', function() {console.log($(this).text()); $('#search').val($(this).text()); $('#result').css('display:none')})
      },
      failure: function(json) {
        console.log('fail');
        console.log(json);
      }
    })
  })

})
