const keys = require('./keys');

// Express App Setup
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const crypto = require("crypto");
const helmet = require('helmet');
const morgan = require('morgan');
const jwt = require('express-jwt');
const jwksRsa = require('jwks-rsa');
const AdmZip = require('adm-zip');
const admin = require('firebase-admin');
const functions = require('firebase-functions');


const app = express();

// adding Helmet to enhance your API's security
app.use(helmet());

// using bodyParser to parse JSON bodies into JS objects
// create application/json parser
var jsonParser = bodyParser.json()

// create application/x-www-form-urlencoded parser
var urlencodedParser = bodyParser.urlencoded({ extended: false })

// enabling CORS for all requests
app.use(cors());

// adding morgan to log HTTP requests
app.use(morgan('combined'));


// Firebase Setup
var serviceAccount = require("./synclabd-firebase-adminsdk-ytj92-85babe429d.json");
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: 'https://synclabd.firebaseio.com'
});

const firestore = admin.firestore();
const database = admin.database();

//const firebaseConfig = {
//  apiKey: "AIzaSyAOvaCbz_NpuusIdZAi0BQ4w0OR5r-JIr0",
//  authDomain: "synclabd.firebaseapp.com",
//  databaseURL: "https://synclabd.firebaseio.com",
//  projectId: "synclabd",
//  storageBucket: "synclabd.appspot.com",
//  messagingSenderId: "441483248251",
//  appId: "1:441483248251:web:3f01905a7d95222feb18de",
//  measurementId: "G-FS918METY1"
//};
//firebase.initializeApp(firebaseConfig);




// Redis Client Setup
const redis = require('redis');
const redisClient = redis.createClient({
  host: keys.redisHost,
  port: keys.redisPort,
  retry_strategy: () => 1000,
});
const redisPublisher = redisClient.duplicate();

// Setting up the Java Web Tokens for API

//const checkJwt = jwt({
//  secret: jwksRsa.expressJwtSecret({
//    cache: true,
//    rateLimit: true,
//    jwksRequestsPerMinute: 5,
//    jwksUri: `https://syncenergyai.us.auth0.com/.well-known/jwks.json`
//  }),
//
//  // Validate the audience and the issuer.
//  audience: 'https://dev.gridcoder.com/',
//  issuer: `https://syncenergyai.us.auth0.com/`,
//  algorithms: ['RS256']
//});

// Using JWT Token
//app.use(checkJwt);

// Express route handlers

app.get('/', (req, res) => {
      res.send('API server is working.');
    });

app.post('/simulate', jsonParser, async (req, res) => {

    var projectID = req.body["projectID"];
    var api_key = req.body["apiKey"];

    // Figure out the user id for the Cloud Firestore
    const apiKeyRef = database.ref("Active_APIs/" + api_key + "/");

    apiKeyRef.on('value', (snapshot) => {
        const user_id = snapshot.val();
        const docRef = firestore.collection("Users").doc(user_id);

        // See https://firebase.google.com/docs/firestore/query-data/get-data#get_a_document
        docRef.get().then((doc) => {
            if (doc.exists) {
                var api_calls_made = doc.data()["API_Calls"]
                docRef.set(
                    {
                        "API_Calls": api_calls_made+1
                    }
                )
                const taskID = crypto.randomBytes(16).toString("hex");
                const starttime = Date.now();
                redisPublisher.publish('new-task', JSON.stringify({"projectID":projectID, "starttime": starttime, "taskID": taskID}));
                const response = {working: true, projectID: projectID, "starttime": starttime, "taskID": taskID};
                return res.status(200).json(response);``
            } else {
                return res.status(400).json({"message":"User ID not found."});
            }
        }).catch((error) => {
            return res.status(400).json({"message":"Unable to connect to Firestore."});
        });
    });


});


app.post('/getplotkeys', jsonParser, async(req, res) => {
    // TODO: '/getplotkeys' and '/getdata' API calls can be made more efficient together

    var error = false;
    var projectID = req.body["projectID"];
    var runID = req.body["runID"];
    var bucket = admin.storage().bucket("synclabd.appspot.com");
    var datafile_path = "projects/" + projectID + "/results/" + runID + "/datafile.json";
    var datafile = bucket.file(datafile_path)
    datafile.download(function(err, contents) {
        if (!err) {
            var data = JSON.parse(contents);
            var plotKeys = Object.keys(data);
            res.status(200).json({"Success": "Finding out the plottables ... Done!", "plotKeys": plotKeys})
    }
        else {
            console.log(err)
            res.status(400).json({"Error": "While getting list of keys, the datafile.json could not be found or processed. Make sure dataviz API returns 200 status before making this API call."})
        }
    });

});


app.post('/getdata', jsonParser, async(req, res) => {
    var error = false;
    var projectID = req.body["projectID"];
    var runID = req.body["runID"];
    var xKey = req.body["xKey"];
    var yKey = req.body["yKey"];
    var bucket = admin.storage().bucket("synclabd.appspot.com");
    var datafile_path = "projects/" + projectID + "/results/" + runID + "/datafile.json";
    var datafile = bucket.file(datafile_path)
    datafile.download(function(err, contents) {
        if (!err) {
            var data = JSON.parse(contents);
            res.status(200).json({"Success": "Data received", "xValues": data[xKey], "yValues": data[yKey].toString(), "X": xKey, "Y": yKey})
    }
        else {
            console.log(err)
            res.status(400).json({"Error": "datafile.json could not be found or processed. Make sure dataviz API returns 200 status before making this API call."})
        }
    });
});


app.get('/dataviz', jsonParser, async (req, res) => {
    var projectID = req.body["projectID"];
    var runID = req.body["runID"];
    // TODO: add API key check, and make sure person has access to this project
    var error = false
    var results_path = "projects/" + projectID + "/results/" + runID + "/"
    var bucket = admin.storage().bucket("synclabd.appspot.com");

    // redisPublisher.publish('prep-for-data-viz', JSON.stringify({"projectID":projectID, "taskID": taskID}));

    bucket.getFiles({
            autoPaginate: false,
            delimiter: '/',
            prefix: results_path
        }, function(err, files, nextQuery, apiResponse) {
            files.forEach(file => {
                console.log(file.name)


            });
    });



    if (!error) {
        res.status(200).json({"Success": "All result files downloaded successfully"})
    }
    else {
        res.status(400).json({"Error": "File download failure"})
    }





});

app.post('/checkstatus', async (req, res) => {
  var projectID = req.body["projectID"];
  var taskID = crypto.randomBytes(16).toString("hex");
  var starttime = Date.now()
  redisPublisher.publish('new-task', JSON.stringify({"projectID":projectID, "starttime": starttime, "taskID": taskID}));
  res.send({ working: true, projectID: projectID, "starttime": starttime, "taskID": taskID  });
});

app.listen(5000, (err) => {
  console.log('Listening on port 5000');
});

// Define the Firebase function that will act as Express application
// Note: This `api` must match with `/firebase.json` rewrites rule.
exports.api = functions.https.onRequest(app);