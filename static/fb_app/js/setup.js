function rollWeek() {
    $('#status_msg').html('<h3>Status</h3><p>Rolling Week<span class=status>...<span><p>')

    fetch("/fb_app/roll_week/",
    {method: "GET",
    })
    .then((response) =>  response.json())
    .then((responseJSON) => {
        data = $.parseJSON(responseJSON)
        console.log('data ', data)
        $('#status_msg').html('<h3>Week Role complete </h3><p>' + JSON.stringify(data) + '<p>')
  
    })
}
