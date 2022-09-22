function weekDtls() {
    console.log('clicked details')
    fetch("/fb_app/sp_weekly_scores/" + 'john',
    {method: "GET",
    })
    .then((response) =>  response.json())
    .then((responseJSON) => {
        data = responseJSON
        console.log(data)
        console.log(Object.keys(data))
        $('#' + Object.keys(data) + '_row').append('<table><tr><td>Test</td></tr></table>') 
})
}