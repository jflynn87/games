'use strict';

const e = React.createElement;


  class GetRuns extends React.Component {
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
        fetch("/run_app/get_run_data")
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
              return (
                  <table className='table'>
                      <thead>
                       <tr>
                        <th>Date</th>
                        <th>Distance</th>
                        <th>Time</th>
                        <th>Calories</th>
                        </tr>
                      </thead>
                      <tbody>
                      {JSON.parse(data).map(data => 
                       (<tr key={data.date}>
                           <td>{data.date}</td>
                           <td>{data.distance}</td>
                           <td>{data.time}</td>
                           <td>{data.calories}</td>
                           </tr>
                  ))}
                      </tbody>
                  </table>

               )  
          }
          
                  
          }
      }
  


const domContainer = document.querySelector('#run-data');ReactDOM.render(e(GetRuns), domContainer);

