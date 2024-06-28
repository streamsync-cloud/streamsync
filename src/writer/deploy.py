import hashlib
import json
import logging
import os
import sys
import tarfile
import tempfile
import time
import uuid
from datetime import datetime, timedelta
from typing import List

import dateutil.parser
import pytz
import requests
from gitignore_parser import parse_gitignore
from platformdirs import user_data_dir

appname = "WriterDeploy"
appauthor = "Writer"
data_dir = user_data_dir(appname, appauthor)


WRITER_DEPLOY_URL = os.getenv("WRITER_DEPLOY_URL", "https://api.writer.com/v1/deployment/apps")

def deploy(path, token, env):
    app_id = check_app(path, token)
    tar = pack_project(path)
    store_app(app_id, token)
    upload_package(tar, token, env)

def undeploy(token):
    try:
        print("Undeploying app")
        with requests.delete(WRITER_DEPLOY_URL, headers={"Authorization": f"Bearer {token}"}) as resp:
            resp.raise_for_status()
            print("App undeployed")
            sys.exit(0)
    except Exception as e:
        print("Error undeploying app")
        print(e)
        sys.exit(1)

def runtime_logs(token):
    try: 
        build_time = datetime.now(pytz.timezone('UTC')) - timedelta(days=4)
        start_time = build_time
        while True:
            prev_start = start_time
            end_time = datetime.now(pytz.timezone('UTC'))
            data = get_logs(token, {
                "buildTime": build_time,
                "startTime": start_time,
                "endTime": end_time,
            })
            # order logs by date and print
            logs = data['logs']
            for log in logs:
                start_time = start_time if start_time > log[0] else log[0]
            if start_time == prev_start:
                start_time = datetime.now(pytz.timezone('UTC'))
                time.sleep(5)
                continue
            for log in logs:
                print(log[0], log[1])
            print(start_time)
            time.sleep(1)
    except Exception as e:
        print(e)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)

def check_app(path, token):
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    stored_app_id = None
    app_id = get_app_id(path)
    try:
        with open(os.path.join(data_dir, f"{token_hash}"), "r") as f:
            stored_app_id = f.read()
    except FileNotFoundError:
        pass
    if stored_app_id is None:
        return app_id
    if stored_app_id != app_id:
        print("[WARNING] This token was already used to deploy a different app")
        url = get_app_url(token)
        print(f"[WARNING] URL: {url}")
        if input("[WARNING] Are you sure you want to continue? (y/N)").lower() != "y":
            sys.exit(1)
    return app_id
    
def get_app_id(path):
    parsed_file = None
    try:
        with open(os.path.join(path, "ui.json"), "r") as f:
            parsed_file = json.load(f)
            if not isinstance(parsed_file, dict):
                raise ValueError("No dictionary found in components file.")
            file_payload = parsed_file
            app_id = file_payload.get("metadata", {}).get("app_id")
    except FileNotFoundError:
        logging.error(
            "Couldn't find ui.json in the path provided: %s.", path)
        sys.exit(1)
    if not app_id:
        app_id = uuid.uuid4().hex
        parsed_file["metadata"]["app_id"] = app_id
        with open(os.path.join(path, "ui.json"), "w") as f:
            json.dump(parsed_file, f)
    return app_id

def store_app(app_id, token):
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, f"{token_hash}"), "w") as f:
        f.write(app_id)

def pack_project(path):
    print(f"Creating deployment package from path: {path}")

    files = []
    def match(file_path) -> bool: return False
    if os.path.exists(os.path.join(path, ".gitignore")):
        match = parse_gitignore(os.path.join(path, ".gitignore"))
    for root, dirs, filenames in os.walk(path):
        for filename in filenames:
            if ".git" in root.split(os.path.sep):
                continue
            if root == path and filename == "Dockerfile":
                print("[WARNING] Dockerfile found in project root. This will be ignored in the deployment package.")
                continue
            if root == path and filename == "service_entrypoint.py":
                print("[WARNING] service_entrypoint.py is a reserved file name. This will be ignored in the deployment package.")
                continue
            if not match(os.path.join(root, filename)):
                files.append(os.path.relpath(os.path.join(root, filename), path))

    f = tempfile.TemporaryFile(suffix='.tar')

    with tarfile.open(fileobj=f, mode="w") as tar:
        for file in files:
            print("Packing file:", file)
            tar.add(os.path.join(path, file), file)
    f.flush()

    return f

def get_logs(token, params):
    with requests.get(WRITER_DEPLOY_URL, params = params, headers={"Authorization": f"Bearer {token}"}) as resp:
        try:
            resp.raise_for_status()
        except Exception as e:
            print(resp.json())
            raise e
        data = resp.json()

        logs = []
        for log in data.get("logs", []):
            meta, msg = log["log"].split(" F ", 1)
            date, _ = meta.split(" ", 1)
            parsed_date = dateutil.parser.parse(date)
            logs.append((parsed_date, msg))
        logs.sort(key=lambda x: x[0])
        return {"status": data["status"], "logs": logs}

def get_app_url(token):
    params = {
        "buildId": "",
        "buildTime": datetime.now(pytz.timezone('UTC')),
        "startTime": datetime.now(pytz.timezone('UTC')),
        "endTime": datetime.now(pytz.timezone('UTC')),
    }
    with requests.get(WRITER_DEPLOY_URL, params = params, headers={"Authorization": f"Bearer {token}"}) as resp:
        try:
            resp.raise_for_status()
        except Exception as e:
            print(resp.json())
            raise e
        data = resp.json()
    return data['status']['url']


def check_service_status(token, build_id, build_time, start_time, end_time, last_status):
    data = get_logs(token, {
        "buildId": build_id,
        "buildTime": build_time,
        "startTime": start_time,
        "endTime": end_time
    })
    if data["status"]["status"] == "DEPLOYING" and data["status"]["status"] != last_status:
        print("Build completed. Deploying app...")
    status = data["status"]["status"]
    url = data["status"]["url"]
    for log in data.get("logs", []):
        print(log[0], log[1])
    return status, url

def dictFromEnv(env: List[str]) -> dict:
    env_dict = {}
    if env is None:
        return env_dict
    for e in env:
        key, value = e.split("=", 1)
        env_dict[key] = value
        print('Environment variable:', key)

    return env_dict

def upload_package(tar, token, env):
    try: 
        print("Uploading package to deployment server")
        tar.seek(0)
        files = {'file': tar}
        start_time = datetime.now(pytz.timezone('UTC'))
        build_time = start_time
        with requests.post(
            url = WRITER_DEPLOY_URL, 
            headers = {
                "Authorization": f"Bearer {token}",
            },
            files=files,
            data={"envs": json.dumps(dictFromEnv(env))}
        ) as resp:
            try:
                resp.raise_for_status()
            except Exception as e:
                print(resp.json())
                raise e
            data = resp.json()
            build_id = data["buildId"]
        
        print("Package uploaded. Building...")
        status = "WAITING"
        url = ""
        while status not in ["COMPLETED", "FAILED"] and datetime.now(pytz.timezone('UTC')) < build_time + timedelta(minutes=5):
            end_time = datetime.now(pytz.timezone('UTC'))
            status, url = check_service_status(token, build_id, build_time, start_time, end_time, status)
            time.sleep(5)
            start_time = end_time

        if status == "COMPLETED":
            print("Deployment successful")
            print(f"URL: {url}")
            sys.exit(0)
        else:
            time.sleep(5)
            check_service_status(token, build_id, build_time, start_time, datetime.now(pytz.timezone('UTC')), status)
            print("Deployment failed")
            sys.exit(1)

    except Exception as e:
        print("Error uploading package")
        print(e)
        sys.exit(1)
    finally:
        tar.close()


