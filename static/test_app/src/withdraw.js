'use strict';

const e = React.createElement;

  class CheckStarted extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loaded: false,
            error: false,
            placeholder: 'checking for withdraws......',
            data: [],
        };  
    }

    componentDidMount() {
        
        fetch("/golf_app/golf_withdraw/", {
          method: 'GET',
        })
        .then(response => {
          //console.log('wd check', response)
          if (response.status > 400) {
            return this.setState(() => {
              return { placeholder: "WD Something went wrong!", error: true };
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
         console.log('WD Check data: ', data)
          if (!loaded) {
            return (React.createElement(
            'p',
            {key: 'items'},            
            placeholder))
          }
          else if (error) {
            return (React.createElement(
            'p', 
            {key: 'error'},
            placeholder))
          }
          else  {
            console.log('data', data)
            console.log(data.wd_list, Object.keys(data.wd_list).length)
            if ((Object.keys(data.wd_list).length == 0)) {
              return (React.createElement(
                'p',
                {key: 'items'},
                'Withdraws: None'
                ))
            }
            else {
                var wds = data
                var wd_picks = data.wd_picks
                console.log(wd_picks, typeof(wd_picks))
                
            }
            return (React.createElement(
              'h5',
              {className: 'bg-warning'},
              //key: 'items'},
              'Withdraws: ',
              
              wds.wd_list.map(wd => <li>{wd}, Picked by: {wd_picks[wd]}</li>),
              

              )) 
                 
            }}
            }


const domContainer = document.querySelector('#withdraw');ReactDOM.render(e(CheckStarted), domContainer);
