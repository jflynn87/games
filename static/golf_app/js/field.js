console.log('field js loaded')
get_info(info) 

//get existing picks on update
//$(document).ready(function() {
function get_picks_data(field) {
    return new Promise(function (resolve) {
  console.log('field js executing')
      $.ajax({
        type: "GET",
        url: "/golf_app/ajax/get_picks/",
        dataType: 'json',
        success: function (json) {
          var i;
          var data = json
          console.log('picks update data? ', data)
          for (i = 0; i < data.length; ++i) {
              $('#' + data[i].playerName.id).attr('checked', 'checked');

            }
            let started_l = Object.values(data.start).filter(item => item.started).length
            let field_l = Object.values(data.start).length
            console.log(field_l)
            if (started_l > 0) {
                for (let i=0; i < field_l; i++){
                  if (Object.values(data.start)[i].started) {
                  document.getElementById(Object.keys(data.start)[i]).disabled = true
                  row= document.getElementById(Object.keys(data.start)[i]).parentElement
                  row.style.background="gray";
                  newCell = document.createElement('td')
                  newCell.innerHTML = 'Started'
                  newCell.style.color = "white"
                  row.appendChild(newCell)

                  if (data.picks.indexOf(document.getElementById(Object.keys(data.picks)[i]) != -1) && ! document.getElementById(Object.keys(data.start)[i]).checked)
                   {document.getElementById(Object.keys(data.start)[i]).style.display = 'none'}

                          }
                  else (document.getElementById(Object.keys(data.start)[i]).prop.disabled=False)
                  }
            }
            else($('input').prop('disabled', false))  //added 8/25 and commmented same code in field_Sect/ks
            
            $('#pulse').hide()
            $('#main').show()
            get_info(info)
        },
        failure: function(json) {
          console.log('fail');
          console.log(json);
        }
      
      })
      if ($('#pga_t_num').text() == '999') {
        fetch("/golf_app/get_country_picks/" + $('#pga_t_num').text() + '/user',         
        {method: "GET",
        })
    .then((response) => response.json())
    .then((responseJSON) => {
        data = $.parseJSON(responseJSON)
        //console.log('Country Picks responsn', data)
        $.each(data, function(i, pick) {
          //var pick_i = i
          if (i == 3) {pick_i = 1}
          else if (i == 4) {pick_i = 2}
          else if (i == 5) {pick_i = 3}
          else (pick_i = i +1)
          console.log(i, pick_i)
          $('#' + pick.fields.gender + '_' + pick_i + '_' + 'country').val(pick.fields.country);
        })

      })
    }
    resolve() 
 })
}

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


function get_info(info, ele) {
    if (typeof(info) == 'string') {var info = $.parseJSON(info)}

    if (ele) {
      group = ele.name.split('-')[1]
      if (parseInt(info)) {picks = info}
      else {picks = info[ele.name.split('-')[1]]}

      if($("#tbl-group-" + group + ' input:checked').length > parseInt(picks)) {
        ele.checked = false;
        alert (picks.toString() + ' picks already selected.  Deselect a pick first to change your picks')
                  }
      //console.log(picks, 'group: ', group)
      //console.log('checked: ', $("#tbl-group-" + group + ' input:checked').length)
      //adjust this section to take an int of the picks from the event handler rather than api
                  
    //else {
      
    //  $('#pick-status').empty()
    //  check_complete(info)
 //}
}
  $('#pick-status').empty()
  check_complete(info)
  
}

function check_complete(info) {
  //console.log(info)
  $('#pick-status').append('<table id=status-tbl class="table table-sm"> </table>')
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

      var countries_ok = true
      if ($('#pga_t_num').text() == '999') {
        var picks = {}
        //console.log(countries_ok)
        picks['m' + $('#men_1_country').val()] = true
        picks['m' + $('#men_2_country').val()] = true
        picks['m' + $('#men_3_country').val()] = true
        picks['w' + $('#women_1_country').val()] = true
        picks['w' + $('#women_2_country').val()] = true
        picks['w' + $('#women_3_country').val()] = true
        if (Object.keys(picks).length == 6) {countries_ok = true}
        else {countries_ok = false}
      }

      if ($('#pga_t_num').text() == 468) {var ryder_ok = false}
      else {var ryder_ok = true}

      if ($('#pga_t_num').text() == '468') {
        console.log('complete chk ', $('#winning_points').val())
        if ($('#winning_team').val() && parseFloat($('#winning_points').val()) > 14) {
            ryder_ok = true
        }
      else {ryder_o = false}
   //   console.log(ryder_o)
      }

      //console.log(Object.keys(picks).length, countries_ok)
      if (total == parseInt(info['total']) && countries_ok == true && ryder_ok == true) {
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
  //$('.stats-row').attr('hidden', '')
  $('.stats_row').attr('hidden', '')
  }
 else if ($('#stats-dtl-toggle').text().includes('Show')) {
    $('#stats-dtl-toggle').html('<h4> Hide Stats <i class="fa fa-minus-circle" style="color:lightblue;"></i> </h4>')
    $('#bottom #stats-dtl-toggle').html('<h4> Hide Stats <i class="fa fa-minus-circle" style="color:lightblue;"></i> </h4>')
    //$('.stats-row').removeAttr('hidden')
    $('.stats_row').removeAttr('hidden')
    }
    
})

$('#bottom #stats-dtl-toggle').on('click', function() {

  if ($('#bottom #stats-dtl-toggle').text().includes('Hide')) {
  $('#bottom #stats-dtl-toggle').html('<h4> Show Stats <i class="fa fa-plus-circle" style="color:lightblue;"></i> </h4>')
  $('#stats-dtl-toggle').html('<h4> Show Stats <i class="fa fa-plus-circle" style="color:lightblue;"></i> </h4>')
  //$('.stats-row').attr('hidden', '')
  $('.stats_row').attr('hidden', '')
  }
 else if ($('#bottom #stats-dtl-toggle').text().includes('Show')) {
    $('#bottom #stats-dtl-toggle').html('<h4> Hide Stats <i class="fa fa-minus-circle" style="color:lightblue;"></i> </h4>')
    $('#stats-dtl-toggle').html('<h4> Hide Stats <i class="fa fa-minus-circle" style="color:lightblue;"></i> </h4>')
    //$('.stats-row').removeAttr('hidden')
    $('.stats_row').removeAttr('hidden')
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
        //console.log(json.golfers)
        golfers = json.golfers
        field = $.parseJSON(json.field)
        var createXLSLFormatObj = [];
        
        //use order to sort from most recent tournament to first
        order = Object.keys(golfers[0].results).sort(function(a,b) {return b - a})

    /* XLS Head Columns */
    xlsHeader = []
    xlsHeader.push('PGA ID', 'Golfer')
    for (i=0; i < order.length; i++) {
      xlsHeader.push(golfers[0].results[order[i]].t_name)
    }

    /* XLS Rows Data */
    xlsRows = []

    $.each(golfers, function(i, results) {
      var row = {}
      var t_data = []
      //console.log('result: ', order.length, Object.keys(results.results).length)

      if (Object.keys(results.results).length > 0) {
      //if (Object.keys(results.results).length == order.length) {
      //for (j=0; j < order.length; j++) {
        for (j=0; j < Object.keys(results.results).length; j++) {
        t_data.push({'t_name': results.results[order[j]].t_name,
                    'rank': results.results[order[j]].rank})
      }

      row['pga_num'] = results.golfer_pga_num
      row['golfer'] = results.golfer_name;
      
      $.each(t_data, function(idx, data) {
        if (data) {
          var t_name = data.t_name;
          var r = data.rank;
          //need idx as some tournaments happened 2 times in 2021, need unique key
          row[t_name + idx] =r;
          }
        else {
          conssole.log(results.golfer_name,  'NO DATA')
          row[idx] = 'no data';
                        
    }
    })
  }
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
    field_header = ['PGA ID', 'Golfer',	'Group ID',	'currentWGR',	'sow_WGR',	'soy_WGR',	'prior year finish',	'handicap',	'FedEx Rank',
    'FedEx Points', 'Season Played',	'Season Won',	'Season 2-10',	'Season 11-29',	'Season 30 - 49',	'Season > 50',	'Season Cut',
     'SG Off Tee Rank', 'SG Off Tee', 'SG Approach Rank', 'SG Approach', 'SG Around Green Rank', 
     'SG Around Green', 'SG Putting Rank', 'SG Putting']
    
     for (let k=0; k<4; k++) {field_header.push(golfers[0].results[order[k]].t_name)}
     
    fieldRows = []
    $.each(field, function(i, golfer) {
      row = {}
      if (!golfer['fields']['withdrawn']){
        row['pga_num'] = golfer.fields.golfer
        row['golfer'] = golfer['fields']['playerName'].replace(',', '') 
        row['group'] = golfer.fields.group
        row['current_wgr'] = golfer['fields']['currentWGR']
        row['sow_wgr'] = golfer['fields']['sow_WGR'] 
        row['soy_wgr'] = golfer['fields']['soy_WGR']
        row['prior_year'] = golfer.fields.prior_year
        row['handi'] = golfer['fields']['handi']
        row['fedex_rank'] = golfer.fields.season_stats.fed_ex_rank
        row['fedex_points'] = golfer.fields.season_stats.fed_ex_points
        row['played'] = golfer.fields.season_stats.played 
        row['won'] = golfer.fields.season_stats.won
        row['top10'] = golfer.fields.season_stats.top10
        row['bet11_29'] = golfer.fields.season_stats.bet11_29
        row['bet30_49'] = golfer.fields.season_stats.bet30_49
        row['over50'] = golfer.fields.season_stats.over50
        row['cuts'] = golfer.fields.season_stats.cuts
        try {
          row['sg_off_tee_rank'] = golfer.fields.season_stats.off_tee.rank
        }
        catch (e) {row['sg_off_tee_rank'] = 'n/a'}
        try {
          row['sg_off_tee'] = golfer.fields.season_stats.off_tee.average
        }
        catch (e) {row['sg_off_tee'] = 'n/a'}
        try {
          row['sg_approach_green_rank'] = golfer.fields.season_stats.approach_green.rank
        }
        catch (e) {row['sg_approach_green_rank'] = 'n/a'}
        try {
          row['sg_approach_green'] = golfer.fields.season_stats.approach_green.average
        }
        catch (e) {row['sg_approach_green'] = 'n/a'}
        try {
          row['sg_around_green_rank'] = golfer.fields.season_stats.around_green.rank
        }
        catch (e) {row['sg_around_green_rank'] = 'n/a'}
        try {
          row['sg_around_green'] = golfer.fields.season_stats.around_green.average
        }
        catch (e) {row['sg_around_green'] = 'n/a'}
        try {
          row['sg_putting_rank'] = golfer.fields.season_stats.putting.rank
        }
        catch (e) {row['sg_putting_rank'] = 'n/a'}
        try {
          row['sg_putting'] = golfer.fields.season_stats.putting.average
        }
        catch (e) {row['sg_putting'] = 'n/a'}

        row['t0'] = Object.values(golfer.fields.recent)[3].rank
        row['t1'] = Object.values(golfer.fields.recent)[2].rank
        row['t2'] = Object.values(golfer.fields.recent)[2].rank
        row['t3'] = Object.values(golfer.fields.recent)[0].rank
        // row['t1'] = golfers.golfer_pga_num[golfer.fields.golfer].results[1].rank
        // row['t2'] = golfers.golfer_pga_num[golfer.fields.golfer].results[2].rank
        // row['t3'] = golfers.golfer_pga_num[golfer.fields.golfer].results[3].rank



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

    //console.log(field_ws)
    //for (i=0; i < fieldRows.length; i++) {
      
      //link = '=HYPERLINK("https://www.google.com/search?q=' + fieldRows[i].golfer.replace('  ', '%20').replace(',', '') + ')"'
      //link = "https://www.google.com/", "Google"
    //  field_ws[XLSX.utils.encode_cell({
    //    c: 0,
    //    r: i+1,
    //    v: fieldRows[i].golfer
    //  })] = {
      //.l = { Target: 'www.google.com'};
      // works -- f: '=HYPERLINK("http://www.google.com","Google")'}
    //  f: '=HYPERLINK("http://www.google.com/search?q=' + fieldRows[i].golfer.replace('  ', '%20').replace(',', '') + '","' + fieldRows[i].golfer + '")'}
    //}

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

function togglePick(ele) {
  var start = new Date()
 //$('#' + ele.id).css('background-color', 'lightblue')
}


function showStats(field_id, golfer_id) {
  row = document.getElementById('stats_row-' + field_id)
  
  if (row.hidden) {

    
    fetch("/golf_app/get_prior_result/",         
    {method: "POST",
    headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'X-CSRFToken': $.cookie('csrftoken')
            },
    body: JSON.stringify({'tournament_key': $('#tournament_key').text(),
                        'golfer_list': [golfer_id],
                        'group': '',
                        'no_api': true})
  })
  .then((response) => response.json())
  .then((responseJSON) => {
  data = responseJSON

  var stats = build_stats_row(data[0])
  console.log(row)
  row.appendChild(stats)
  row.hidden = false

  })
}
else {
      console.log('row in else : ', row)
      row.innerHTML = ''
      row.hidden = true}

console.log('dur: ', new Date() - start)


}
