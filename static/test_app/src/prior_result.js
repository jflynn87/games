'use strict';


const e = React.createElement;


  class PriorResult extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loaded: false,
            error: false,
            placeholder: 'loading......',
            data: [],
            
        };  
    }

    componentDidMount() {
        fetch("/golf_app/prior_result")
        .then(response => {
          if (response.status > 400) {
            return this.setState(() => {
              return { placeholder: "Something went wrong!", error: true };
            });
          }
          return response.json();
        })
        .then(data => {
            this.setState(() => {
              return {data,
                      loaded: true,
                     };
                }) 
            })
     }
       
      render() {
         var {loaded, error, placeholder, data} = this.state;
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
            console.log(this.state)
            return (
                  <table className='table'>
                      <thead>
                       <tr>
                        <th>Golfer</th>
                        <th>Finish</th>
                        </tr>
                      </thead>
                      <tbody>
                      {JSON.parse(data).map(data => 
                       (
                       <tr key={data.golfer}>
                           <td>{data.golfer}</td>
                           <td>{data.score}</td>
                           </tr>
                  ))}
                      </tbody>
                  </table>
               )  
          }
          }
      }
  

const domContainer = document.querySelector('#prior-results');ReactDOM.render(e(PriorResult), domContainer);

