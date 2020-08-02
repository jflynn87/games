import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import * as serviceWorker from './serviceWorker';


console.log('connected to index.js')
ReactDOM.render(<App />, document.getElementById('runs'));
ReactDOM.render(<App />, document.getElementById('root'));

let runData = document.getElementById('runs')
if (runData !== null) {
    console.log('found ')
    ReactDOM.render(<App />, runData)
}


let runData1 = document.getElementById('root')
if (runData1 !== null) {
    console.log('rund 1 found ')
    ReactDOM.render(<App />, runData1)
}


// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
