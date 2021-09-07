$(document).ready(function () {
    start = new Date()
    Promise.all([
    fetch("/golf_app/get_info/" + $('#tournament_key').text()).then(response => response.json()),
    fetch("/golf_app/field_get_picks").then(response=> response.json())
     ])
     .then((responseJSON) => {
         info = $.parseJSON(responseJSON[0])
         picks = $.parseJSON(responseJSON[1])
     })
    })