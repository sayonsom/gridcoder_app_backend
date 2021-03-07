Services and their roles:

1. `api` : gets the requests for which project ID to work on, and update the database, project status queries etc. Basically handles the backend routing.
   Need to make sure I connect redis and fast api with it.
2. `client`: documentation 
3. `nginx`: routing 
4. `worker`: For listening to the redis queue and performing simulations

