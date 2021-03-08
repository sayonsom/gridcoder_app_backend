#docker build -t sayonsync/gridcoder-api:latest -t sayonsync/gridcoder-api:$SHA -f ./api/Dockerfile ./api
#docker build -t sayonsync/gridcoder-client:latest -t sayonsync/gridcoder-client:$SHA -f ./client/Dockerfile ./client
#docker build -t sayonsync/gridcoder-worker:latest -t sayonsync/gridcoder-worker:$SHA -f ./worker/Dockerfile ./worker
#
#docker push sayonsync/gridcoder-api:latest
#docker push sayonsync/gridcoder-client:latest
#docker push sayonsync/gridcoder-worker:latest
#
#docker push sayonsync/gridcoder-api:$SHA
#docker push sayonsync/gridcoder-client:$SHA
#docker push sayonsync/gridcoder-worker:$SHA
#
#kubectl apply -f k8s
#
#kubectl set image deployments/api-deployment api=sayonsync/gridcoder-api:latest
#kubectl set image deployments/client-deployment client=sayonsync/gridcoder-client:latest
#kubectl set image deployments/worker-deployment worker=sayonsync/gridcoder-worker:latest

docker build -t sayonsync/gridcoder-api -f ./api/Dockerfile ./api
docker build -t sayonsync/gridcoder-client -f ./client/Dockerfile ./client
docker build -t sayonsync/gridcoder-worker -f ./worker/Dockerfile ./worker

docker push sayonsync/gridcoder-api:latest
docker push sayonsync/gridcoder-client:latest
docker push sayonsync/gridcoder-worker:latest

kubectl apply -f k8s

kubectl set image deployments/api-deployment api=sayonsync/gridcoder-api
kubectl set image deployments/client-deployment client=sayonsync/gridcoder-client
kubectl set image deployments/worker-deployment worker=sayonsync/gridcoder-worker