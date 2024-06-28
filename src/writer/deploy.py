import json
import logging
import os
import re
import sys
import tarfile
import tempfile
import time
from datetime import datetime, timedelta
from typing import List, Union

import click
import dateutil.parser
import pytz
import requests
from gitignore_parser import parse_gitignore

WRITER_DEPLOY_URL = os.getenv("WRITER_DEPLOY_URL", "https://api.writer.com/v1/deployment/apps")

@click.group()
def cloud():
    """A group of commands to deploy the app"""
    pass

@cloud.command()
@click.option('--api-key',
    default=lambda: os.environ.get("WRITER_API_KEY", None),
    allow_from_autoenv=True,
    show_envvar=True,
    envvar='WRITER_API_KEY',
    prompt="Enter your API key",
    hide_input=True, help="Writer API key"
)
@click.option('--env', '-e', multiple=True, default=[], help="Environment to deploy the app to")
@click.option('--verbose', '-v', default=False, is_flag=True, help="Enable verbose mode")
@click.argument('path')
def deploy(path, api_key, env, verbose):
    """Deploy the app from PATH folder."""

    abs_path, is_folder = _get_absolute_app_path(path)
    if not is_folder:
        raise click.ClickException("A path to a folder containing a Writer Framework app is required. For example: writer cloud deploy my_app")

    env = _validate_env_vars(env)
    tar = pack_project(abs_path)
    try:
        upload_package(tar, api_key, env, verbose=verbose)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            unauthorized_error()
        else:
            on_error_print_and_raise(e.response, verbose=verbose)
    except Exception as e:
        print(e)
        print("Error deploying app")
        sys.exit(1)
    finally:
        tar.close()

def _validate_env_vars(env: Union[List[str], None]) -> Union[List[str], None]:
    if env is None:
        return None
    for var in env:
        print(var)
        regex = r"^[a-zA-Z_]+[a-zA-Z0-9_]*=.*$"
        if not re.match(regex, var):
            logging.error(f"Invalid environment variable: {var}, please use the format ENV_VAR=value")
            sys.exit(1)
    return env

@cloud.command()
@click.option('--api-key',
    default=lambda: os.environ.get("WRITER_API_KEY", None),
    allow_from_autoenv=True,
    show_envvar=True,
    envvar='WRITER_API_KEY',
    prompt="Enter your API key",
    hide_input=True, help="Writer API key"
)
@click.option('--verbose', '-v', default=False, is_flag=True, help="Enable verbose mode")
def undeploy(api_key, verbose):
    """Stop the app, app would not be available anymore."""
    try:
        print("Undeploying app")
        with requests.delete(WRITER_DEPLOY_URL, headers={"Authorization": f"Bearer {api_key}"}) as resp:
            on_error_print_and_raise(resp, verbose=verbose)
            print("App undeployed")
            sys.exit(0)
    except Exception as e:
        print("Error undeploying app")
        print(e)
        sys.exit(1)

@cloud.command()
@click.option('--api-key',
    default=lambda: os.environ.get("WRITER_API_KEY", None),
    allow_from_autoenv=True,
    show_envvar=True,
    envvar='WRITER_API_KEY',
    prompt="Enter your API key",
    hide_input=True, help="Writer API key"
)
@click.option('--verbose', '-v', default=False, is_flag=True, help="Enable verbose mode")
def logs(api_key, verbose):
    """Fetch logs from the deployed app."""

    try: 
        build_time = datetime.now(pytz.timezone('UTC')) - timedelta(days=4)
        start_time = build_time
        while True:
            prev_start = start_time
            end_time = datetime.now(pytz.timezone('UTC'))
            data = get_logs(api_key, {
                "buildTime": build_time,
                "startTime": start_time,
                "endTime": end_time,
            }, verbose=verbose)
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

def get_logs(token, params, verbose=False):
    with requests.get(WRITER_DEPLOY_URL, params = params, headers={"Authorization": f"Bearer {token}"}) as resp:
        on_error_print_and_raise(resp, verbose=verbose)
        data = resp.json()

        logs = []
        for log in data.get("logs", []):
            meta, msg = log["log"].split(" F ", 1)
            date, _ = meta.split(" ", 1)
            parsed_date = dateutil.parser.parse(date)
            logs.append((parsed_date, msg))
        logs.sort(key=lambda x: x[0])
        return {"status": data["status"], "logs": logs}

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


def upload_package(tar, token, env, verbose=False):
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
        on_error_print_and_raise(resp, verbose=verbose)
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

def on_error_print_and_raise(resp, verbose=False):
    try:
        resp.raise_for_status()
    except Exception as e:
        if verbose:
            print(resp.json())
        raise e

def unauthorized_error():
    print(f"\n{WRITER_DEPLOY_URL}")
    print("Unauthorized. Please check your API key.")
    sys.exit(1)

def _get_absolute_app_path(app_path: str):
    is_path_absolute = os.path.isabs(app_path)
    absolute_app_path = app_path if is_path_absolute else os.path.join(os.getcwd(), app_path)
    is_path_folder = absolute_app_path is not None and os.path.isdir(absolute_app_path)
    return absolute_app_path, is_path_folder
