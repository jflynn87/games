$(document).ready(function () {
    get_spreads()  })


function get_spreads() {
    //$(document).ready(function () {
      console.log('getting spreads')
      $('#status').text('updating spreads ....').attr('class', 'status')
      fetch("/fb_app/get_spreads/" + $('#week_key').text(),
      {method: "GET",
    //  headers: {
    //    'Accept': 'application/json',
    //    'Content-Type': 'application/json',
    //    'X-CSRFToken': $.cookie('csrftoken')
    //          },
    //   body: JSON.stringify({'week_key': $('#week-list').val()})
      })
    .then((response) =>  response.json())
    .then((responseJSON) => {
      json = $.parseJSON(responseJSON)
      console.log(json)
          for (i = 0; i < json.length; ++i) {
    
            console.log(json[i][0])
            row = $('tr[name=' + json[i][0] + ']')
    
            $('td', row).each(function () {
    
              if ($(this).prop('id').startsWith('spread')) {
                $(this).html(json[i][5])
              }
              else if ($(this).prop('id').startsWith('fav')) {
                $(this).html(json[i][1] +"<span class='record'>" + json[i][2] + "</span>")
                
              }
              else if ($(this).prop('id').startsWith('dog')) {
                $(this).html(json[i][3] + "<span class='record'>" + json[i][4] + "</span>")
    
              }
            })
          }
          var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
          now = new Date()
          console.log(now)
          $('#status').text('spreads updated: ' + now).attr('class', 'updated-status')
        })
      }
    
    