import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import * as serviceWorker from './serviceWorker';



var AWS = require("aws-sdk");

// var credentials = new AWS.SharedIniFileCredentials({profile: 'default'});

// var credentials = new AWS.Credentials({
//   accessKeyId: 'AKIA3IHNDBEYY7I2Z5RT', secretAccessKey: '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', sessionToken: null
// });
// AWS.config.credentials = credentials;

AWS.config.update({
  region: "ap-south-1"
});


class MyForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = { location: '', symptoms: '', testresults: '' };
  }
  mySubmitHandler = (event) => {
      event.preventDefault();
      var docClient = new AWS.DynamoDB.DocumentClient();

		var table = "RealTimeUpdates";

		var location = this.state.location;
		var sym = this.state.symptoms;
		var test = this.state.testresults;

		var ProbablyPositive = 0;
		var Positive = 0;

		if(test==="Pos"){
			Positive = 1;
		}
		else if(sym==="Yes"){
			ProbablyPositive = 1;
		}
		else{
			;
		}

		var fetch_params = {
		    TableName:table,
		    Key:{
		        "Location": location
		        // "sym": sym,
		        // "test": test
		    }
		};

		console.log("Fetching existing item...");
		docClient.get(fetch_params, function(err, data) {
		    if (err) {
		        console.error("Unable to fetch item. Error JSON:", JSON.stringify(err, null, 2));
		    } else {
		        console.log("Fetched item:", JSON.stringify(data, null, 2));
		        if(JSON.stringify(data, null, 2)==="{}"){
		        	;
		        }
		        else{
		        	ProbablyPositive += data["Item"]["ProbablyPositive"];
					Positive += data["Item"]["Positive"];
		        }
		        console.log("Pos", Positive);
				console.log("ProbablyPositive", ProbablyPositive);

				var post_params = {
				    TableName:table,
				    Item:{
				        "Location": location,
				        "ProbablyPositive": ProbablyPositive,
						"Positive": Positive
				    }
				};

				console.log("Adding item...");
				docClient.put(post_params, function(err, data) {
				    if (err) {
				        console.error("Unable to add item. Error JSON:", JSON.stringify(err, null, 2));
				    } else {
				        console.log("Added item:", JSON.stringify(data, null, 2));
				    }
				});
		    }
		});

		
    }
  myLocChangeHandler = (event) => {
    this.setState({location: event.target.value});
  }
  mySymChangeHandler = (event) => {
    this.setState({symptoms: event.target.value});
  }
  myTestChangeHandler = (event) => {
    this.setState({testresults: event.target.value});
  }
  render() {
    return (
      <form name="myform" onSubmit={this.mySubmitHandler}>
      <h1>Hello {this.state.location} resident</h1>
      <p>Your City</p>
      <input
        type='text'  name="loc"
        onChange={this.myLocChangeHandler}
      />
      <p>Are you having symptoms of Covid19 (Enter Yes or No)</p>
      <input
        type='text'  name="sym"
        onChange={this.mySymChangeHandler}
      />
      <p>Test Results (Enter Pos or Neg) </p>
      <input
        type='text'  name="test"
        onChange={this.myTestChangeHandler}
      />
      <input
        type='submit'
      />
      </form>
    );
  }
}

ReactDOM.render(<MyForm />, document.getElementById('root'));

serviceWorker.unregister();
