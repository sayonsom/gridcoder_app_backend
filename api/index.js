const keys = require('./keys');

// Express App Setup
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const crypto = require("crypto");

const app = express();
app.use(cors());
app.use(bodyParser.json());


// Redis Client Setup
const redis = require('redis');
const redisClient = redis.createClient({
  host: keys.redisHost,
  port: keys.redisPort,
  retry_strategy: () => 1000,
});
const redisPublisher = redisClient.duplicate();

// Express route handlers

app.get('/', (req, res) => {
  res.send('API server is working');
});

app.post('/simulate', async (req, res) => {
  var projectID = req.body["projectID"];
  var taskID = crypto.randomBytes(16).toString("hex");
  var starttime = Date.now()
  redisPublisher.publish('new-task', JSON.stringify({"projectID":projectID, "starttime": starttime, "taskID": taskID}));
  res.send({ working: true, projectID: projectID, "starttime": starttime, "taskID": taskID  });
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
