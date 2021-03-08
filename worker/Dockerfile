# base image
FROM gridlabd/slac-develop
WORKDIR "/app"

# install python
RUN yum update -y
RUN yum install -y python3

# Set up the working directory
COPY ./app_worker.py ./
COPY ./synclabd-firebase-adminsdk-ytj92-85babe429d.json ./
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --use-feature=2020-resolver

CMD ["python3", "app_worker.py"]