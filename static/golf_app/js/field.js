console.log('field js loaded')

//get existing picks on update
$(document).ready(function() {
  console.log('field js executing')
  //$('#main').hide()
  // $.ajax({
  //   type: "GET",
  //   url: "/golf_app/get_info/",
  //   dataType: 'json',
  //   data: {'tournament' : $('#tournament_key').text()},
  //   success: function (json) {
  //     info = $.parseJSON((json))
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
            $('#pulse').hide()
            $('#main').show()
            get_info(info)
        },
        failure: function(json) {
          console.log('fail');
          console.log(json);
        }
      
      })
 //    },
 //   failure: function(json) {
 //     console.log('get info fail');
 //     console.log(json);
 //   }

  //)
 })
  
$(document).on("click", "#download", function() {
  console.log('clicked download')
          
          let csv = "data:text/csv;charset=utf-8," 
//          csv +=  'Golfer' + ',' + 'PGA ID' + ',' + 'Group Number' + ',' + 'currentWGR' + ',' + 'sow_WGR' + 
//          ',' + 'soy_WGR' + ',' + 'prior year finish' + ',' + 'handicap' + 
//          ',' + $('#t_1').text() + 
//          ',' + $('#t_2').text() + 
//          ',' + $('#t_3').text() + 
//          ',' + $('#t_4').text() + 
//         ',' + 'Google Search' + '\n'


         
          $.ajax({
            type: "GET",
            url: "/golf_app/get_field_csv/",
            dataType: 'json',
            data: {'tournament' : $('#tournament_key').text()},
            success: function (json) {
                golfers = $.parseJSON(json)
                console.log(golfers)
                let tournaments = []
                $.each(golfers[0].fields.recent, function(key, info) {
                  console.log(key, info)
                  tournaments.push(info.name)
                })
                console.log('tournaments: ', tournaments)

                csv +=  'Golfer' + ',' + 'PGA ID' + ',' + 'Group Number' + ',' + 'currentWGR' + ',' + 'sow_WGR' + 
                ',' + 'soy_WGR' + ',' + 'prior year finish' + ',' + 'handicap' + 
                ',' + tournaments[0] + 
                ',' + tournaments[1] + 
                ',' + tournaments[2] + 
                ',' + tournaments[3] + 
                ',' + 'Season Played' + 
                ',' + 'Season Won' + 
                ',' + 'Season 2-10' + 
                ',' + 'Season 11-29' + 
                ',' + 'Season 30 - 49' + 
                ',' + 'Season > 50' + 
                ',' + 'Season Cut' + 
                ',' + 'Google Search' + '\n'
      
                $.each(golfers, function(i, golfer) {
                if (!golfer['fields']['withdrawn']){
                  let recent = []
                  $.each(golfer.fields.recent, function(key, result) {
                    //console.log('recent data: ', key, result)
                    recent.push(result.rank)
                  })
                  
                  
                  csv += golfer['fields']['playerName'].replace(',', '') + ',' +
                  golfer.fields.golfer + ',' +
                  golfer.fields.group + ',' +
                  golfer['fields']['currentWGR']  + ',' +
                  golfer['fields']['sow_WGR'] + ',' +
                  golfer['fields']['soy_WGR'] + ',' +
                  //$('#prior' + golfer['fields']['golfer']).text().replace('prior: ', '').trim() + ',' + 
                  golfer.fields.prior_year + ',' +
                  golfer['fields']['handi'] + ',' +  
                  recent[0] + ',' +
                  recent[1] + ',' +
                  recent[2] + ',' +
                  recent[3] + ',' +
                  golfer.fields.season_stats.played + ',' +
                  golfer.fields.season_stats.won + ',' +
                  golfer.fields.season_stats.top10 + ',' +
                  golfer.fields.season_stats.bet11_29 + ',' +
                  golfer.fields.season_stats.bet30_49 + ',' +
                  golfer.fields.season_stats.over50 + ',' +
                  golfer.fields.season_stats.cuts + ',' +

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


// $(document).ready(function () {
// var limit = 5;
// $('input.my-checkbox').on('change', function(evt) {
//    if($("input[name='multi-group-6']:checked").length > limit) {
//        this.checked = false;
//        alert (limit.toString() + ' picks already selected.  Deselect a pick first to change your picks')
//    }
//    get_info(info)
// })
// });

// $(document).ready(function () {
//  $('input.my-radio').on('change', function(evt) {
//    console.log('caught clck')
//    $('#pick-status').empty()
//    get_info(info)
//  })
//  })

function get_info(info, ele) {
    if (ele) {
      group = ele.name.split('-')[1]
      picks = info[ele.name.split('-')[1]]
      
      if($("#tbl-group-" + group + ' input:checked').length > parseInt(picks)) {
        ele.checked = false;
        alert (picks.toString() + ' picks already selected.  Deselect a pick first to change your picks')
                  }
    //else {
    //  $('#pick-status').empty()
    //  check_complete(info)
 // }
}
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
        $('#sub_button').removeAttr('disabled').attr('class', 'btn btn-primary').val('Submit Picks');
        $('#actual-grouptotal').css('background-color', '')  
        $('#required-groupcomplete').text('True')
      }
      else 
      {$('#sub_button').prop('disabled', true).attr('class', 'btn btn-secondary').val(total + ' of ' + info.total + ' picks');
      $('#actual-grouptotal').css('background-color', '#FFF300')}
      })
  
})
}

function count_actual(group, picks) {
  //if (picks == 1) {
      var selected = $('input[name=group-' + group + ']:checked').length
      //}
  //else {var selected = $('input[name=multi-group-' + group + ']:checked').length } 
  //console.log(group, picks, selected)
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

//Excel Download section



$(document).on("click", "#download_excel", function() {
  $.ajax({
    type: "GET",
    url: "/golf_app/get_golfers/",
    dataType: 'json',
    //data: {'tournament' : $('#tournament_key').text()},
    success: function (json) {
        golfers = json.golfers
        field = $.parseJSON(json.field)
        console.log('excel sect golfers ', golfers)
        var createXLSLFormatObj = [];

/* XLS Head Columns */
xlsHeader = []
xlsHeader.push('Golfer Name', 'PGA Number')
$.each(golfers[0].results, function(i, data) {
      xlsHeader.push(data.t_name)

})

/* XLS Rows Data */
xlsRows = []

$.each(golfers, function(i, results) {
  var row = {}
  var t_data = Object.values(results.results)
  row['golfer'] = results.golfer_name;
  row['pga_num'] = results.golfer_pga_num
 
  $.each(t_data, function(idx, data) {
    if (data) {
      var t_name = data.t_name;
      var r = data.rank;
      //need idx as some tournaments happened 2 times in 2021, need unique key
      row[t_name + idx] =r;
       }
    else {
      conssole.log(results.golfer_name,  'NO DATA')
      row['no data'] = 'no data';
                    
}
})
xlsRows.push(row)
})

createXLSLFormatObj.push(xlsHeader);

$.each(xlsRows, function(index, value) {
    var innerRowData = [];
    $.each(value, function(ind, val) {
        innerRowData.push(val);
    });
    createXLSLFormatObj.push(innerRowData);
});

/* File Name */
var filename = "golf game data " + $('#t-name').text() + '.xlsx';
/* Sheet Name */
var ws_name = "All Golfer Results";
if (typeof console !== 'undefined') console.log(new Date());
var wb = XLSX.utils.book_new(),
    ws = XLSX.utils.aoa_to_sheet(createXLSLFormatObj);
/* Add worksheet to workbook */
XLSX.utils.book_append_sheet(wb, ws, ws_name);

var createXLSXFieldObj = [];
ws2_name = "Current Week Field";
field_header = ['Golfer',	'PGA ID',	'Group ID',	'currentWGR',	'sow_WGR',	'soy_WGR',	'prior year finish',	'handicap',	'Season Played',	'Season Won',	'Season 2-10',	'Season 11-29',	'Season 30 - 49',	'Season > 50',	'Season Cut']
fieldRows = []
$.each(field, function(i, golfer) {
  row = {}
  if (!golfer['fields']['withdrawn']){
    row['golfer'] = golfer['fields']['playerName'].replace(',', '') 
    row['pga_num'] = golfer.fields.golfer
    row['group'] = golfer.fields.group
    row['current_wgr'] = golfer['fields']['currentWGR']
    row['sow_wgr'] = golfer['fields']['sow_WGR'] 
    row['soy_wgr'] = golfer['fields']['soy_WGR']
    row['prior_year'] = golfer.fields.prior_year
    row['handi'] = golfer['fields']['handi']
    row['played'] = golfer.fields.season_stats.played 
    row['won'] = golfer.fields.season_stats.won
    row['top10'] = golfer.fields.season_stats.top10
    row['bet11_29'] = golfer.fields.season_stats.bet11_29
    row['bet30_49'] = golfer.fields.season_stats.bet30_49
    row['over50'] = golfer.fields.season_stats.over50
    row['cuts'] = golfer.fields.season_stats.cuts
    //row['google'] = golfer['fields']['playerName'].replace(',', '') 
    //row['google'] = 
    //    '=HYPERLINK("https://www.google.com/search?q=' + golfer['fields']['playerName'].replace('  ', '%20').replace(',', '') + '")' 
         

   fieldRows.push(row)
   //console.log('fieldRow: ', typeof(fieldRows), fieldRows.length)
  }
  
})

createXLSXFieldObj.push(field_header)
//createXLSXFieldObj.push(fieldRows);
//console.log('golfer xcel:', createXLSLFormatObj)
//console.log('excl obj: ', createXLSXFieldObj)

$.each(fieldRows, function(index, value) {
  //console.log('value: ', value)
  var innerRowData = [];
  //$("tbody").append('<tr><td>' + value.EmployeeID + '</td><td>' + value.FullName + '</td></tr>');
  $.each(value, function(ind, val) {
      //console.log('val data ', val)
      innerRowData.push(val);
  });
  createXLSXFieldObj.push(innerRowData);
});

//.then((response) => response)
//.then((response) => {


//console.log('field: ', response, typeof(response))


var field_ws = XLSX.utils.aoa_to_sheet(createXLSXFieldObj);

console.log(field_ws)
for (i=0; i < fieldRows.length; i++) {
  
  //link = '=HYPERLINK("https://www.google.com/search?q=' + fieldRows[i].golfer.replace('  ', '%20').replace(',', '') + ')"'
  link = "https://www.google.com/", "Google"
  field_ws[XLSX.utils.encode_cell({
    c: 0,
    r: i+1,
    v: fieldRows[i].golfer
  })] = {
  //.l = { Target: 'www.google.com'};
  // works -- f: '=HYPERLINK("http://www.google.com","Google")'}
  f: '=HYPERLINK("http://www.google.com/search?q=' + fieldRows[i].golfer.replace('  ', '%20').replace(',', '') + '","' + fieldRows[i].golfer + '")'}
}

//console.log('field_ws', field_ws)
XLSX.utils.book_append_sheet(wb, field_ws, ws2_name);

/* Write workbook and Download */
if (typeof console !== 'undefined') console.log(new Date());
XLSX.writeFile(wb, filename);
if (typeof console !== 'undefined') console.log(new Date());

  //})
}
  })
})
// function formatFieldXLSData(field) {
//   return new Promise (function (resolve, reject) {
//   fieldRows = []
//   $.each(field, function(i, golfer) {
//     row = {}
//     if (!golfer['fields']['withdrawn']){
      
      
//       row['golfer'] = golfer['fields']['playerName'].replace(',', '') 
//       row['pga_num'] = golfer.fields.golfer.golfer_pga_num
//       row['group'] = golfer.fields.group
//       row['current_wgr'] = golfer['fields']['currentWGR']
//       row['sow_wgr'] = golfer['fields']['sow_WGR'] 
//       row['soy_wgr'] = golfer['fields']['soy_WGR']
//       row['prior_year'] = golfer.fields.prior_year
//       row['handi'] = golfer['fields']['handi']
//       row['played'] = golfer.fields.season_stats.played 
//       row['won'] = golfer.fields.season_stats.won
//       row['top10'] = golfer.fields.season_stats.top10
//       row['bet11_29'] = golfer.fields.season_stats.bet11_29
//       row['bet30_49'] = golfer.fields.season_stats.bet30_49
//       row['over50'] = golfer.fields.season_stats.over50
//       row['cuts'] = golfer.fields.season_stats.cuts
//       row['google'] = 
//        '=HYPERLINK("https://www.google.com/search?q=' + golfer['fields']['playerName'].replace('  ', '%20').replace(',', '') + '")' 
      
//       fieldRows.push(row)
//     }
//   })
//   resolve(fieldRows)
// }
//   )

  
//}