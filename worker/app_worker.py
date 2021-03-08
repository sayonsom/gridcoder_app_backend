import redis
from google.cloud import storage
from firebase import Firebase
from datetime import datetime
import glob
import datetime
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


def file_download(url, test_file_name):
    try:
        urllib.request.urlretrieve(url, test_file_name)
    except:
        breakpoint()


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
        blob_glm = bucket.blob(name)
        local_name = name.split("/")[-1]
        extension = local_name.split(".")[1]
        local_folder = "temporary"  # "/".join(name.split("/")[:-1])
        local_name = name.split("/")[-1]
        print(f"Creating a local folder: {local_folder}")
        Path(local_folder).mkdir(exist_ok=True)
        os.chdir(local_folder)
        file_url = blob_glm.generate_signed_url(
            expiration=datetime.timedelta(minutes=10),
            version='v4',
            service_account_email='synclabd@appspot.gserviceaccount.com',
            method="GET",
            content_type="application/octet-stream",
            credentials=credentials
        )
        file_download(file_url, local_name)
        if extension.lower() == 'glm':
            glm_files.append(local_name)

    if len(glm_files) > 0:

        data = {'start_time': start_time,
                'stop_time': "NA", 'run_time': "In Progress"}
        # update the start time as soon as the simulation starts
        print("this_task_ID = ", this_task_id)
        print("this data - ", data)
        all_projects = db.child("projects").get()
        print(all_projects)
        db.child("projects").child(this_project_id).child("runs").child(this_task_id).set(data)

        glm_run(this_task_id, this_project_id, glm_files[0])
        stop_time = datetime.datetime.now()

        # Add the stop time, update the status, etc.
        data = {
            'stop_time': stop_time.strftime("%Y-%m-%d %H:%M:%S")}
        db.child("projects").child(this_project_id).child("runs").child(this_task_id).update(data)

        # All the CSV files generated are to be uploaded to the Google Storage
        recorder_files = glob.glob("*.csv")
        print("Recorder Files = ", recorder_files)

        for rf in recorder_files:
            blob = bucket.blob(f"projects/{this_project_id}/results/{this_task_id}/{rf.replace('.csv', '')}")
            blob.upload_from_filename(rf)

        # Upload the file upon which the results were based
        blob = bucket.blob(
            f"projects/{this_project_id}/results/{this_task_id}/{glm_files[0].replace('.glm', '_GRIDLABD_FILE')}")
        blob.upload_from_filename(rf)
    else:
        return "No GLM file found"

    os.chdir(owd)
    return "Simulation Finished"


def glm_run(this_task_id, project_id, filename):
    print(os.getcwd())
    # Start a GridLAB-D simulation
    proc = subprocess.Popen(f'gridlabd {filename} --redirect output:outfile_2.txt', shell=True)
    try:
        outs, errs = proc.communicate(timeout=10000)

        # db_entry = Workspace(task_id=this_task_id,status='FINISHED',Std_err=errs,Std_out=outs)
        # try:
        #     db.session.add(db_entry)
        #     db.session.commit()
        #
        # except:
        #     breakpoint()
    except TimeoutError:
        proc.kill()
        # outs, errs = proc.communicate()
        # db_entry = Workspace(task_id=this_task_id, status='ERROR', Std_err=errs, Std_out=outs)
        # db.session.add(db_entry)
        # db.session.commit()
    return "Done"


def start_simulation(project_id, start_time, task_id):
    """Starts a GridLAB-D simulation and returns a job-id if at least one GLM file exists"""
    owd = os.getcwd()
    run_simulation(project_id, owd, start_time, task_id)
    os.chdir(owd)
    return {'summary': 'New Simulation Job Created'}


if __name__ == "__main__":
    print("joy joy")
    pubsub = redis_conn.pubsub()
    pubsub.subscribe("new-task")
    for message in pubsub.listen():
        print(message)
        print("LOL")
        if message.get("type") == "message":
            project_data = json.loads(message.get("data"))
            project_id = project_data["projectID"]
            start_time = project_data["starttime"]
            task_id = project_data["taskID"]
            start_simulation(project_id, start_time, task_id)

