$(document).ready(function() {
    
    fetch("/golf_app/get_api_scores/" + $('#tournament_key').text(),
    {method: "GET",
    }
          )
    .then((response) => response.json())
    .then((responseJSON) => {
          data = responseJSON
          console.log(data)

})
})