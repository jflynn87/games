function createFieldCSV(pk) {
    console.log('Create CSV')
    $('#create_csv').attr('disabled', true).text('Creating...')

    const isLocalhost = window.location.hostname === 'localhost' || 
                       window.location.hostname === '127.0.0.1';
    
    const endpoint = isLocalhost 
        ? '/golf_app/create_field_csv' 
        : '/golf_app/async_create_field_csv';

    const mode = isLocalhost ? '' : 'async';

    fetch(`${endpoint}?pk=${pk}&mode=${mode}`)
    .then((response) => {
        if (!response.ok) {
            handleError('Failed to start CSV creation');
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then((data) => {
        console.log('Create CSV initiated: ', data);
        // Now using Cognito token
        if (! isLocalhost){
        pollStatus(data.task_id, data.cognitoToken, data.lambdaUrl);
        }
        else {
            $('#create_csv')
            .removeClass('btn-primary')
            .addClass('btn-success')
            .text('File Created');
 
        }
    })
    .catch(error => {
        handleError(error.message);
    });
}

function pollStatus(taskId, token, lambdaUrl) {
    const maxAttempts = 30;
    const pollInterval = 4000;
    let attempts = 0;

    const checkStatus = () => {
        let lambdaUrl = 'https://qfb3lcyhphpqb3rzembdi3jipe0zciqn.lambda-url.us-west-2.on.aws/'
        const headers = {
            'Authorization': token,
            'Content-Type': 'application/json',
        };
        
        fetch(lambdaUrl, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                taskId: taskId
            })
        })
        .then(response => {
            if (!response.ok) {
                handleError('Status check failed');
                throw new Error('Status check failed');
            }
            return response.json();
        })
        .then(status => {
            console.log('Status response:', status);
            
            if (status.status === 'COMPLETED') {
                $('#create_csv')
                    .removeClass('btn-primary')
                    .addClass('btn-success')
                    .text('File Created');
                return;
            } 
            
            if (status.status === 'FAILED') {
                handleError('CSV creation failed');
                return;
            }
            $('#create_csv').text(status.progress);
            attempts++;
            if (attempts < maxAttempts) {
                setTimeout(checkStatus, pollInterval);
            } else {
                handleError('Operation timed out');
            }
        })
        .catch(error => {
            handleError(error.message);
        });
    };

    checkStatus();
}

function handleError(message) {
    $('#create_csv')
    .removeClass('btn-primary')
    .addClass('btn-danger')
    .text('Error');    
    throw new Error(message);

}

function createCSVDiv(pk) {

    fetch('/golf_app/field_csv_signed_url?pk=' + pk)
    .then((response) => {
        if (!response.ok) {
            
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then((data) => {
        console.log('CSV Div initiated: ', data);
        // Now using Cognito token
        buildCSVDiv(data, pk);
    })
    .catch(error => {
        throw new Error(error.message);
    });

}

function buildCSVDiv(data, pk) {
    console.log('buildCSVDiv: ', data)
    $('#csv_div').empty()
    if (data.url) {
    $('#csv_div').append('<div id="download_file_div">' +
                            '<a href=' + data.url + ' id="download_excel" >' +
                            '<i class="fas fa-file-download" title="Download CSV" data-toggle="tooltip">Download CSV</i>' +
                            '</a></div>')
                }
    else {
        $('#csv_div').append('<div id="generate_file_div">' +
                            '<button class="btn btn-primary" id="create_csv" onclick="createFieldCSV(' + pk + ')">Generate CSV</button>' +
                            '</div>')
        }
}