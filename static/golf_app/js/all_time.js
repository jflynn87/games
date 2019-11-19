$(document).ready (function() { 
  console.log('first step');
  $('#data').hide()
  
  $.ajax({
    
    type: "GET",
    url: "/golf_app/ajax/get_scores/",
    dataType: 'json',
    success: function (json) {
      console.log('connected', json, json.length);
      
      addTotals(json[0])
      addLeaders(json[1])
      addCut(json[2])
     /* for (i = 0; i < json.length; ++i) {
        console.log(json[i])
        $('#score-tbl').find('tbody')
        .append($('<tr>')
        .append($('<td>').text((json[i][0])))
        .append($('<td>').text((json[i][1])))
        .append($('<td>').text((json[i][2])))
                                             )}
   */
          
          $('#pulse').hide()
          $('#data').show()

                                          },
    failure: function(json) {
      console.log('fail');
      console.log(json);
    }
  })

  $.ajax({
    
    type: "GET",
    url: "/golf_app/ajax/get_leader/",
    dataType: 'json',
    success: function (json) {
      console.log('connected', json, json.length);
      
     /* for (i = 0; i < json.length; ++i) {
        console.log(json[i])
        $('#score-tbl').find('tbody')
        .append($('<tr>')
        .append($('<td>').text((json[i][0])))
        .append($('<td>').text((json[i][1])))
        .append($('<td>').text((json[i][2])))
                                             )}
   */
          
          $('#pulse').hide()
          $('#data').show()

                                          },
    failure: function(json) {
      console.log('fail');
      console.log(json);
    }
  })



function addTotals(scores) {
  
  for (i = 0; i < scores.length; ++i) {
    $('#score-tbl').find('tbody')
    .append($('<tr>')
    .append($('<td>').text((scores[i][0])))
    .append($('<td>').text((scores[i][1])))
    .append($('<td>').text((scores[i][2])))
                                         )}
}

function addLeaders(leaders) {
  console.log('leaders', leaders)
   if (leaders.length == 1) {
     $('#leaders').text('Leader: ' + leaders[0][0] + ':  ' + leaders[0][1])
   }
   else {
   for (j=0; j < leaders.length; ++j) {
     $('#leaders').append($('p').text('Leader:' + leaders[j][0] + ':  ' + leaders[j][1]))
   }
 }
}

function addCut(cutData) {
  console.log('cutData', cutData)
  $('#cut-data').text('Cut Status:  ' + cutData[0][0] + ':  ' + cutData[0][1])
}

})

