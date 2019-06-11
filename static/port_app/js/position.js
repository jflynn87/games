$(document).ready(function() {
 $('#id_type').change(function () {
   if ($(this).val() == 1) {
 var i = 0
 $('#search').focusout(function () {$('#result').css('display', 'none')})
  $('#search').keyup(function(e) {
    if (e.originalEvent.key.match(/[a-z]/)) {console.log('letter')};
    console.log(e.originalEvent.key, i);
    console.log('len', $('#result option').length);
    if (e.originalEvent.key == 'ArrowDown') {
      if (i < $('#result option').length -1) {i ++};
      $('#search').val($('#item'+i).text())
      $('#result option').removeClass('autocomplete-active')
      $('#item'+i).addClass('autocomplete-active')
    }
    else if (e.originalEvent.key == 'ArrowUp') {
      if (i != 0) {i--};
      $('#search').val($('#item'+i).text())
      $('#result option').removeClass('autocomplete-active')
      $('#item'+i).addClass('autocomplete-active')
    }
    else {
    console.log('keyup');
    $('#result').css('display', '')
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
        $.each(data, function(index, value) {
          console.log(index, value);
          var ticker = value['1. symbol']
          $('#result').append('<option id= "item' + index + '" class="list-group-item"' + 'value="' + ticker + '" >' + value['2. name'] + ' - ' + value['1. symbol'])
        })

          $('#search').val($('#item0').text())
          $('#item0').addClass('autocomplete-active')
          $('#result option').on('click', function() {$('#search').val($(this).text()); $('#search').text($(this).text());
                  $('#id_symbol').text(ticker)
                  $('#result').css('display', 'none')})
      },
      failure: function(json) {
        console.log('fail');
        console.log(json);
      }
    })

}
})
}
})
})
