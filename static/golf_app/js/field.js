//get existing picks on update
$(document).ready(function() {
  $('#main').hide()
  $.ajax({
    type: "GET",
    url: "/golf_app/get_info/",
    dataType: 'json',
    data: {'tournament' : $('#tournament_key').text()},
    success: function (json) {
      info = $.parseJSON((json))
      $.ajax({
        type: "GET",
        url: "/golf_app/ajax/get_picks/",
        dataType: 'json',
        //context: document.body
        success: function (json) {
          var i;
          var data = $.parseJSON(json)
          for (i = 0; i < data.length; ++i) {
              $('#' + data[i]).attr('checked', 'checked');
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
    
    },
    failure: function(json) {
      console.log('get info fail');
      console.log(json);
    }
  })
 

})
  
$(document).on("click", "#download", function() {
  console.log('clicked download')
  $.ajax({
    type: "GET",
    url: "/golf_app/get_field_csv/",
    dataType: 'json',
    data: {'tournament' : $('#tournament_key').text()},
    success: function (json) {
          data = $.parseJSON(json)
          let csv = "data:text/csv;charset=utf-8," 
          csv += 'Golfer' + ',' + 'currentWGR' + ',' + 'sow_WGR' + 
          ',' + 'soy_WGR' + ',' + 'prior year finish' + ',' + 'handicap' + '\n'
          $.each(data, function(i) {
            console.log(data[i]['fields'])
          csv += data[i]['fields']['playerName'] + ',' + data[i]['fields']['currentWGR']  + ',' + data[i]['fields']['sow_WGR'] + 
          ',' + data[i]['fields']['soy_WGR'] + ',' + $('#prior' + data[i]['fields']['playerID']).text().replace('prior: ', '').trim() + ',' + data[i]['fields']['handi']
          csv += '\n'
          })
          var file = encodeURI(csv)
          window.open(file)
          

        },
        failure: function(json) {
          console.log('fail');
          console.log(json);
        }

      })
      
})




/*
  $.ajax({
    type: "GET",
    url: "/golf_app/ajax/get_picks/",
    dataType: 'json',
    //context: document.body
    success: function (json) {
      var i;
      var data = $.parseJSON(json)
      for (i = 0; i < data.length; ++i) {
          $('#' + data[i]).attr('checked', 'checked');
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
*/
//create global variable of the tournament groups and required picks
/*$('#tournament_key').ready(function() {
$.ajax({
  type: "GET",
  url: "/golf_app/get_info/",
  dataType: 'json',
  data: {'tournament' : $('#tournament_key').text()},
  success: function (json) {
    info = $.parseJSON((json))
  },
  failure: function(json) {
    console.log('get info fail');
    console.log(json);
  }
})
})
*/

$(function () {
  $('[data-toggle="tooltip"]').tooltip({trigger:"hover",
                                        delay:{"show":400,"hide":800}})})


$(document).ready(function () {
var limit = 5;
$('input.my-checkbox').on('change', function(evt) {
   if($("input[name='multi-group-6']:checked").length > limit) {
       this.checked = false;
       alert (limit.toString() + ' picks already selected.  Deselect a pick first to change your picks')
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
     $('#picks-row').append('<td id=status-group' + group + '> <a href=#tbl-group-' + group + '>' + group + '</a> </td>')
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
    $('td', this).slice(1,-1).each(function (i) {
      if ($(this).text() != info[i+1]) {
        $(this).css('background-color', '#FFF300')
      }

      total += parseInt(($(this).text()))
      $('#actual-grouptotal').text(total)

      if (total == parseInt(info['total'])) {
        $('#sub_button').removeAttr('disabled').attr('class', 'btn btn-primary');
        $('#actual-grouptotal').css('background-color', '')  
      }
      else 
      {$('#sub_button').prop('disabled', true).attr('class', 'btn btn-secondary');
      $('#actual-grouptotal').css('background-color', '#FFF300')}
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
