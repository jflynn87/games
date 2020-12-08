'use strict';

const e = React.createElement;

  class CheckStarted extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loaded: false,
            error: false,
            placeholder: 'checking if started......',
            data: [],
        };  
    }

    componentDidMount() {
        
        var token = $.cookie('csrftoken')
        
        fetch("/golf_app/started/", {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': $.cookie('csrftoken')
          },

          //body  : {'key': $('#tournament_key').text()}
          body  : JSON.stringify({'key': $('#tournament_key').text()})
        })
        .then(response => {
          console.log(response)
          if (response.status > 400) {
            return this.setState(() => {
              return { placeholder: "Something went wrong!", error: true };
            });
          }
            return response.json();
          })
        .then (data => {
              this.setState(() => {
             return {
              data,
              loaded: true
            };
          });
            });  
     }
      render() {
         console.log(this.state)
         var {loaded, error, placeholder, data} = this.state;
         console.log(typeof(data))
          if (!loaded) {
            return (React.createElement(
            'h5',
            {key: 'items'},            
            placeholder))
          }
          else if (error) {
            return (React.createElement(
            'h2', 
            {key: 'error'},
            placeholder))
          }
          else {
              console.log('in else')
              console.log(JSON.parse(data))
              console.log(JSON.parse(data)['status'])
              if (!JSON.parse(data)['status']) {
                 return (React.createElement(
                  'h5',
                  {key: 'items'},          
                  'Not Started'   
                 ))}
                 return (React.createElement(
                  'h5',
                  {key: 'items'}, 
                  JSON.parse(data)['status']           
                 ))
              }
          }
      }


const domContainer = document.querySelector('#status');ReactDOM.render(e(CheckStarted), domContainer);








// $(document).ready(function () {
//     console.log('checking started')
//     console.log($('#tournament_key').text())
    
    
    
//     $.ajax({
//         type: "GET",
//         url: "/golf_app/started/",
//         data: {'t_pk' : $('#tournament_key').text()},
//         dataType: 'json',
//         success: function (text) {
//           console.log('started check', text)
     
//                                               },
//         failure: function(json_update) {
//           console.log('fail');
//           console.log(text);
//         }
//       })
    
// })