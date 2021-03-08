docker build -t sayonsync/gridcoder-api:latest -t sayonsync/gridcoder-api:$SHA -f ./api/Dockerfile ./api
docker build -t sayonsync/gridcoder-devdocs:latest -t sayonsync/gridcoder-devdocs:$SHA -f ./client/Dockerfile ./client
docker build -t sayonsync/gridcoder-worker:latest -t sayonsync/gridcoder-worker:$SHA -f ./worker/Dockerfile ./worker

docker push sayonsync/gridcoder-api:latest
docker push sayonsync/gridcoder-devdocs:latest
docker push sayonsync/gridcoder-worker:latest

docker push sayonsync/gridcoder-api:$SHA
docker push sayonsync/gridcoder-devdocs:$SHA
docker push sayonsync/gridcoder-worker:$SHA

kubectl apply -f k8s

kubectl set image deployments/api-deployment api=sayonsync/gridcoder-api:$SHA
kubectl set image sayonsync/gridcoder-devdocs client=sayonsync/gridcoder-devdocs:$SHA
kubectl set image deployments/worker-deployment worker=sayonsync/gridcoder-worker:$SHA