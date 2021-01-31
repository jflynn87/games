'use strict';

const e = React.createElement;

  class CheckStarted extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loaded: false,
            error: false,
            placeholder: 'checking for espn nums......',
            data: [],
        };  
    }

    componentDidMount() {
        
        fetch("/golf_app/check_espn_nums/", {
          method: 'GET',
        })
        .then(response => {
          //console.log('wd check', response)
          if (response.status > 400) {
            return this.setState(() => {
              return { placeholder: "ESPN Num check, something went wrong!", error: true };
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
         //console.log(this.state)
         var {loaded, error, placeholder, data} = this.state;
         //console.log(data)
          if (!loaded) {
            return (React.createElement(
            'h5',
            {key: 'items'},            
            placeholder))
          }
          else if (error) {
            return (React.createElement(
            'h4', 
            {key: 'error'},
            placeholder))
          }
          else  {
            //console.log('in else')
            console.log(Object.keys(data.field_missing).length)
            if (Object.keys(data.field_missing).length == 0) {
                console.log('espn nums good, returning null')
               return null
               
            }
            else {
                var missing = data['field_missing']

            }
                 console.log(missing)
             return (React.createElement(
               'h5',
               {className: 'bg-warning'},
               //key: 'items'},
              'Missing ESPN Nums: ',
               
               <li>{missing['golfer']}</li>
            ))
      }}
            }


const domContainer = document.querySelector('#espn_missing');ReactDOM.render(e(CheckStarted), domContainer);