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
    "projectID": "4f0d5097-d66f-46ba-8eb6-dfb129a05c1c"
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