import redis
from google.cloud import storage
from firebase import Firebase
from datetime import datetime
import glob
import datetime
import time
import urllib.request
from pathlib import Path
import os
import subprocess
import json
from google.oauth2 import service_account

redis_conn = redis.Redis(host=os.environ['REDIS_HOST'],
                         port=os.environ['REDIS_PORT'],
                         charset='utf-8',
                         decode_responses=True)

# Firebase Configuration
config = {
    'apiKey': "AIzaSyAOvaCbz_NpuusIdZAi0BQ4w0OR5r-JIr0",
    'authDomain': "synclabd.firebaseapp.com",
    'databaseURL': "https://synclabd.firebaseio.com",
    'projectId': "synclabd",
    'storageBucket': "synclabd.appspot.com",
    'messagingSenderId': "441483248251",
    'appId': "1:441483248251:web:3f01905a7d95222feb18de",
    'measurementId': "G-FS918METY1"
}

firebase = Firebase(config)
storage_client = storage.Client()
storage_fb = firebase.storage()
db = firebase.database()
credentials = service_account.Credentials.from_service_account_file(
    'synclabd-firebase-adminsdk-ytj92-85babe429d.json')


def file_download(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""

    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Blob {} downloaded to {}.".format(
            source_blob_name, destination_file_name
        )
    )


def files_in_a_project(project_id):
    bucket = storage_client.get_bucket("synclabd.appspot.com")
    files = bucket.list_blobs(prefix=f"projects/{project_id}/", delimiter="/")
    file_names = []

    for f in files:
        file_names.append(f.name)

    return file_names


def run_simulation(this_project_id, owd, start_time, task_id):
    this_task_id = task_id
    # db.child("projects").child(this_project_id).child("runs").child(this_task_id)
    bucket = storage_client.get_bucket("synclabd.appspot.com")
    files = bucket.list_blobs(prefix=f"projects/{this_project_id}/", delimiter="/")
    glm_files = []

    for f in files:
        name = f.name
        local_name = name.split("/")[-1]
        extension = local_name.split(".")[1]
        local_folder = "temporary"  # "/".join(name.split("/")[:-1])
        local_name = name.split("/")[-1]
        print(f"Creating a local folder: {local_folder}")
        Path(local_folder).mkdir(exist_ok=True)
        os.chdir(local_folder)
        f.download_to_filename(local_name)

        if extension.lower() == 'glm':
            glm_files.append(local_name)

    if len(glm_files) > 0:

        data = {'start_time': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(start_time)),
                'stop_time': "NA", 'run_time': "In Progress"}
        # update the start time as soon as the simulation starts
        print("this_task_ID = ", this_task_id)
        print("this data - ", data)
        all_projects = db.child("projects").get()
        print(all_projects)
        db.child("projects").child(this_project_id).child("runs").child(this_task_id).set(data)

        run_time_result = glm_run(this_task_id, this_project_id, glm_files[0])
        stop_time = time.time()
        compute_duration = stop_time - start_time
        # Add the stop time, update the status, etc.
        data = {
            'run_time': run_time_result,
            'compute_duration': compute_duration,
            'stop_time': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(stop_time))}
        db.child("projects").child(this_project_id).child("runs").child(this_task_id).update(data)

        # Upload all the files to the Project results

        files = glob.glob("*.*")

        for f in files:
            blob = bucket.blob(f"projects/{this_project_id}/results/{this_task_id}/{f}")
            blob.upload_from_filename(f)

        # All the CSV files generated are to be uploaded to the Google Storage
        # recorder_files = glob.glob("*.csv")
        # print("Recorder Files = ", recorder_files)
        #
        # for rf in recorder_files:
        #     blob = bucket.blob(f"projects/{this_project_id}/results/{this_task_id}/{rf}")
        #     blob.upload_from_filename(rf)
        #
        # # Upload the file upon which the results were based
        # blob = bucket.blob(
        #     f"projects/{this_project_id}/results/{this_task_id}/{glm_files[0]}")
        # blob.upload_from_filename(rf)
    else:
        return "No GLM file found"

    os.chdir(owd)
    return "Simulation Finished"


def glm_run(this_task_id, project_id, filename):
    print(os.getcwd())
    # Start a GridLAB-D simulation
    try:
        proc = subprocess.check_output(
            f'gridlabd {filename} --redirect output:outfile.txt --redirect warning:warnings.txt --redirect error:errors.txt',
            shell=True, stderr=subprocess.STDOUT, timeout=10000)
        try:
            if os.path.getsize('./errors.txt') > 0:
                return "Failed"
            elif os.path.getsize('./warnings.txt') > 0:
                return "Completed (Review Warnings)"
            else:
                return "Completed"
        except OSError:
            return f"Output File Read Error. Email: support@gridcoder.com. Mention Project ID= {project_id}, Task ID={this_task_id}"
    except TimeoutError:
        proc.kill()
        return "Failed"


def start_simulation(project_id, start_time, task_id):
    """Starts a GridLAB-D simulation and returns a job-id if at least one GLM file exists"""
    owd = os.getcwd()
    run_simulation(project_id, owd, start_time, task_id)
    os.chdir(owd)
    return {'summary': 'New Simulation Job Created'}


if __name__ == "__main__":
    pubsub = redis_conn.pubsub()
    pubsub.subscribe("new-task")
    for message in pubsub.listen():
        if message.get("type") == "message":
            project_data = json.loads(message.get("data"))
            project_id = project_data["projectID"]
            start_time = project_data["starttime"]
            task_id = project_data["taskID"]
            start_simulation(project_id, start_time, task_id)

    # project_id = "4f0d5097-d66f-46ba-8eb6-dfb129a05c1c"
    # start_time = 1615898254
    # task_id = "test-1-tuesday-march-16-2021"
    # start_simulation(project_id, start_time, task_id)
