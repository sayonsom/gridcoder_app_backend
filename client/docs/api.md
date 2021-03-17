---
id: api
title: GridCoder API
---
## Available APIs

### Start a new simulation

To start a new simulation, make the following `POST` request with the project ID on the body:

```shell
POST https://dev.gridcoder.com/simulate
```

In the body of the post, we add the project ID

```
{
    "projectID": "12926131-c149-487a-8529-5b836ca37815",
    "apiKey" : "secret-API-key"
}
```

## Coming Soon 

We are working on these APIs next, and will be updated shortly

### Check status of a simulation 

```shell
GET https://dev.gridcoder.com/checkstatus/<PROJECT-ID>
```

### Getting the output files of a simulation 

```shell
GET https://dev.gridcoder.com/outputs/<PROJECT-ID>
```