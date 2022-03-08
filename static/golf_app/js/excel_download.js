
// $(document).on("click", "#download_excel", function() {
function downloadExcel() {
$('#download_excel').html('Preparing Data...')
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
              
        fieldRows.push(row)
  
        }
        
      })
  
      createXLSXFieldObj.push(field_header)
  
      $.each(fieldRows, function(index, value) {
        var innerRowData = [];
        $.each(value, function(ind, val) {
            innerRowData.push(val);
        });
        createXLSXFieldObj.push(innerRowData);
      });
  
      var field_ws = XLSX.utils.aoa_to_sheet(createXLSXFieldObj);
  
      XLSX.utils.book_append_sheet(wb, field_ws, ws2_name);
  
      /* Write workbook and Download */
      if (typeof console !== 'undefined') console.log(new Date());
      XLSX.writeFile(wb, filename);
      if (typeof console !== 'undefined') console.log(new Date());
  
        //})
      }
    })
  }
  
  