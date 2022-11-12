$(document).ready(function () {
    fetch("/wc_app/wc_scores_api",         
    {method: "GET",
    })
.then((response) => response.json())
.then((responseJSON) => {
    data = responseJSON
    console.log('countries: ', data)
    })

})