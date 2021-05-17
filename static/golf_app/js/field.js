//get existing picks on update
$(document).ready(function() {
  //$('#main').hide()
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
        success: function (json) {
          var i;
          var data = $.parseJSON(json)
          for (i = 0; i < data.length; ++i) {
              $('#' + data[i]).attr('checked', 'checked');
            }
           // $('#pulse').hide()
           // $('#main').show()
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
          
          let csv = "data:text/csv;charset=utf-8," 
          csv +=  'Golfer' + ',' + 'Group Number' + ',' + 'currentWGR' + ',' + 'sow_WGR' + 
          ',' + 'soy_WGR' + ',' + 'prior year finish' + ',' + 'handicap' + 
          ',' + $('#t_1').text() + 
          ',' + $('#t_2').text() + 
          ',' + $('#t_3').text() + 
          ',' + $('#t_4').text() + 
          ',' + 'Google Search' + '\n'


         
          $.ajax({
            type: "GET",
            url: "/golf_app/get_field_csv/",
            dataType: 'json',
            data: {'tournament' : $('#tournament_key').text()},
            success: function (json) {
                golfers = $.parseJSON(json)
                //console.log(json)

                $.each(golfers, function(i, golfer) {
                if (!golfer['fields']['withdrawn']){
//                  group_pk = golfer['fields']['group']
//                  group_num = golfer.group  

                  csv += golfer['fields']['playerName'].replace(',', '') + ',' +
                  golfer.fields.group + ',' +
                  golfer['fields']['currentWGR']  + ',' +
                  golfer['fields']['sow_WGR'] + ',' +
                  golfer['fields']['soy_WGR'] + ',' +
                  $('#prior' + golfer['fields']['golfer']).text().replace('prior: ', '').trim() + ',' + 
                  golfer['fields']['handi'] + ',' +  
                  $('#recent' + golfer['fields']['golfer']).text().replace('recent form: ', '').trim() + ',' + 
                   '=HYPERLINK("https://www.google.com/search?q=' + golfers[i]['fields']['playerName'].replace('  ', '%20').replace(',', '') + '")' 
                  csv += '\n'
          
                }
              })
      
          var encodedUri = encodeURI(csv);
          var link = document.createElement("a");
          link.setAttribute("href", encodedUri);
          link.setAttribute("download", $('#t-name').text() + " field.csv");
          document.body.appendChild(link); // Required for FF
          link.click();
 
          }
         
      ,
      failure: function(json) {
        console.log('get csv data fail');
        console.log(json);
        alert('sorry, download failed.  please tell John')
      }
          })
      
      })  
      

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
  //console.log(info)
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
   //console.log('a ', group, picks, count_actual(group, picks))
   if (group != "complete") {
    $('#actual-row').append('<td id=actual-group'+ group + '>' + count_actual(group, picks) + '</td>')
   }
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
        $('#required-groupcomplete').text('True')
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


//there should be a cleaner way to do these next 2 functions.
$('#stats-dtl-toggle').on('click', function() {
  
  if ($('#stats-dtl-toggle').text().includes('Hide')) {
  $('#stats-dtl-toggle').html('<h4> Show Stats <i class="fa fa-plus-circle" style="color:lightblue;"></i> </h4>')
  $('#bottom #stats-dtl-toggle').html('<h4> Show Stats <i class="fa fa-plus-circle" style="color:lightblue;"></i> </h4>')
  $('.stats-row').attr('hidden', '')
  }
 else if ($('#stats-dtl-toggle').text().includes('Show')) {
    $('#stats-dtl-toggle').html('<h4> Hide Stats <i class="fa fa-minus-circle" style="color:lightblue;"></i> </h4>')
    $('#bottom #stats-dtl-toggle').html('<h4> Hide Stats <i class="fa fa-minus-circle" style="color:lightblue;"></i> </h4>')
    $('.stats-row').removeAttr('hidden')
    }
    
})

$('#bottom #stats-dtl-toggle').on('click', function() {

  if ($('#bottom #stats-dtl-toggle').text().includes('Hide')) {
  $('#bottom #stats-dtl-toggle').html('<h4> Show Stats <i class="fa fa-plus-circle" style="color:lightblue;"></i> </h4>')
  $('#stats-dtl-toggle').html('<h4> Show Stats <i class="fa fa-plus-circle" style="color:lightblue;"></i> </h4>')
  $('.stats-row').attr('hidden', '')
  }
 else if ($('#bottom #stats-dtl-toggle').text().includes('Show')) {
    $('#bottom #stats-dtl-toggle').html('<h4> Hide Stats <i class="fa fa-minus-circle" style="color:lightblue;"></i> </h4>')
    $('#stats-dtl-toggle').html('<h4> Hide Stats <i class="fa fa-minus-circle" style="color:lightblue;"></i> </h4>')
    $('.stats-row').removeAttr('hidden')
    }
    
})
