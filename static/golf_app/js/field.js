$(document).ready(function() {
  $('#main').hide()

  $.ajax({
    type: "GET",
    url: "/golf_app/ajax/get_picks/",
    dataType: 'json',
    //context: document.body
    success: function (json) {
      var i;
      for (i = 0; i < json.length; ++i) {
          $('#' + json[i]).attr('checked', 'checked');
        }
        $('#pulse').hide()
        $('#main').show()

    },
    failure: function(json) {
      console.log('fail');
      console.log(json);
    }
  })
})

$(document).ready(function() {
var ul = document.getElementById('old_picks');
var items = ul.getElementsByTagName('li');
for (var j = 0; j < items.length; ++j) {
  $('#' + items[j].innerHTML).attr('checked', 'checked');
}
})
 
$(function () {
  $('[data-toggle="tooltip"]').tooltip({trigger:"hover",
                                        delay:{"show":400,"hide":800}})})
 