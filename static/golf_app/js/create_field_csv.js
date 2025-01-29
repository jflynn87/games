function createFieldCSV() {
    console.log('Create CSV')
    fetch('/golf_app/create_field_csv')
    .then((response) =>{
        if (! response.ok) {
            $('#create_csv').removeClass('btn-primary')
            $('#create_csv').addClass('btn-danger')
            $('#create_csv').text('Error')
            console.log('csv error resp: ', response)
            throw new Error('Network response was not ok');
        }
       return response.json()
        })
    .then((responseJSON) => {
    resp = $.parseJSON(responseJSON)
    console.log('Create CSV response: ', resp)
    $('#create_csv').removeClass('btn-primary')
    $('#create_csv').addClass('btn-success')
    $('#create_csv').text('File Created')

         })
    }