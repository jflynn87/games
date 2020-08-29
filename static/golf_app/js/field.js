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
        get_info(info)

    },
    failure: function(json) {
      console.log('fail');
      console.log(json);
    }
  })
})


$.ajax({
  type: "GET",
  url: "/golf_app/get_info/",
  dataType: 'json',
  //context: document.body
  success: function (json) {
    info = $.parseJSON((json))
   // check_complete(info)
  },
  failure: function(json) {
    console.log('get info fail');
    console.log(json);
  }
})

$(function () {
  $('[data-toggle="tooltip"]').tooltip({trigger:"hover",
                                        delay:{"show":400,"hide":800}})})
 
$(document).ready(function () {
var limit = 5;
$('input.my-checkbox').on('change', function(evt) {
   if($("input[name='multi-group-6']:checked").length > limit) {
       this.checked = false;
   }
   get_info(info)
})
});

$(document).ready(function () {
$('input.my-radio').on('change', function(evt) {
  $('#pick-status').empty()
  get_info(info)
})
})

function get_info(info) {
  $('#pick-status').empty()
  check_complete(info)
}

function check_complete(info) {
  $('#pick-status').append('<table id=status-tbl class=table small> </table>')
  $('#status-tbl').append('<tr id=picks-row> <td> Groups: </td> </tr>')
  $.each(info,  function(group, picks) {
     $('#picks-row').append('<td id=status-group'+ group + '>' + group + '</td>')
  })  
     $('#status-tbl').append('<tr id=required-row> <td> Picks required: </td> </tr>')
     $.each(info,  function(group, picks) {
        $('#required-row').append('<td id=required-group'+ group + '>' + picks + '</td>')
 })
 $('#status-tbl').append('<tr id=actual-row> <td> Total Picks: </td> </tr>')
 $.each(info,  function(group, picks) {
    $('#actual-row').append('<td id=actual-group'+ group + '>' + count_actual(group, picks) + '</td>')
})
var total = 0
$("#actual-row").each(function () {
    $('td', this).slice(1,-1).each(function () {
      total += parseInt(($(this).text()))
      $('#actual-grouptotal').text(total)
      console.log('info1', info)
      if (total == parseInt(info['total'])) {
        $('#sub_button').removeAttr('disabled')
      }
      else $('#sub_button').prop('disabled', true)
      })
  
})
}

function count_actual(group, picks) {
  if (picks == 1) {
      var selected = $('input[name=group-' + group + ']:checked').length
  }
  else {var selected = $('input[name=multi-group-' + group + ']:checked').length } 
  
  return selected
}
 
