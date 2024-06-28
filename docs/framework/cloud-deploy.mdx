# Cloud Deployment Using CLI

## Table of Contents

2. [Basic Usage](#basic-usage)
3. [Common Options](#common-options)
4. [Commands](#commands)
   - [Deploy](#writer-cloud-deploy)
   - [Undeploy](#writer-cloud-undeploy)
   - [Logs](#writer-cloud-logs)
5. [Environment Variables](#environment-variables)
6. [API Key](#api-key)
7. [Deployment Process](#deployment-process)
8. [Example Workflow](#example-workflow)

## Basic Usage

The `writer cloud` command group includes the following commands:
- `deploy`
- `undeploy`
- `logs`

## Common Options

These options are common across multiple commands:
- `--api-key`: The Writer API key used for authentication. If not provided, you will be prompted to enter it.
- `--verbose, -v`: Enable verbose output.

## Commands

### `writer cloud deploy`

Deploys an app from the specified path to the Writer cloud.

**Usage:**
```
writer cloud deploy [OPTIONS] PATH
```

**Arguments:**
- `PATH`: The path to the folder containing the app to deploy.

**Options:**
- `--api-key`: Writer API key for authentication. If not provided, you will be prompted to enter it.
- `--env, -e`: Environment variables to set in the deployed app. Use the format `VAR=value`. Multiple environment variables can be specified by repeating the `--env` option.
- `--verbose, -v`: Enable verbose output.

**Example:**
```
writer cloud deploy hello --env VAR1=value1 --env VAR2=value2
```

**Description:**
- Deploys the app located in the `PATH` folder.
- Creates a deployment package, ignoring `.git` directories, Dockerfiles, and reserved filenames like `service_entrypoint.py`.
- Uploads the package to the deployment server.
- The deployed app will have access to specified environment variables.
- By default, the `WRITER_API_KEY` environment variable will be added to enable AI features.

**Output Example**

```
Creating deployment package from path: /path/to/your/app
[WARNING] Dockerfile found in project root. This will be ignored in the deployment package.
Packing file: pyproject.toml
Packing file: README.md
...
Uploading package to deployment server
Package uploaded. Building...
...
Deployment successful
URL: https://your_app_url
```

### `writer cloud undeploy`

Stops the deployed app and makes it unavailable.

**Usage:**
```
writer cloud undeploy [OPTIONS]
```

**Options:**
- `--api-key`: Writer API key for authentication. If not provided, you will be prompted to enter it.
- `--verbose, -v`: Enable verbose output.

**Example:**
```
writer cloud undeploy
```

**Description:**
- Stops and removes the deployed app from the Writer cloud.

### `writer cloud logs`

Fetches logs from the deployed app.

**Usage:**
```
writer cloud logs [OPTIONS]
```

**Options:**
- `--api-key`: Writer API key for authentication. If not provided, you will be prompted to enter it.
- `--verbose, -v`: Enable verbose output.

**Example:**
```
writer cloud logs
```

**Description:**
- Continuously fetches and displays logs from the deployed app.
- Logs are ordered by date and time.

**Output Example**

```
2024-06-11 09:27:02.190646+00:00 [INFO] Starting container entrypoint...
2024-06-11 09:27:03.798148+00:00 [INFO] BuildService - Downloading build files...
...
```

## Environment Variables

When deploying an app, you can specify environment variables that will be available to the app during runtime. Use the `--env` option to pass these variables.

**Example:**
```
writer cloud deploy hello --env DB_HOST=db.example.com --env DB_PORT=5432
```

In this example, `DB_HOST` and `DB_PORT` will be available to the app as environment variables.

## API Key

The `WRITER_API_KEY` is crucial for deploying and managing apps. It is used for authenticating requests to the Writer cloud. If not provided as an option, the CLI will prompt you to enter it. The `WRITER_API_KEY` will also be added to the deployed app's environment to enable AI features of the Writer framework.

## Deployment Process

1. **Package Creation:** The CLI packages the app, excluding certain files (e.g., Dockerfile, `service_entrypoint.py`).
2. **Upload Package:** The package is uploaded to the Writer deployment server.
3. **Build and Deploy:** The server builds and deploys the app, making it accessible via a URL.
4. **Environment Variables:** Specified environment variables are set, and `WRITER_API_KEY` is added by default.

## Example Workflow

1. **Deploying an App:**
   ```
   writer cloud deploy /path/to/app --env DB_HOST=db.example.com --env DB_PORT=5432
   ```

2. **Fetching Logs:**
   ```
   writer cloud logs
   ```

3. **Undeploying an App:**
   ```
   writer cloud undeploy
   ```

By following this documentation, you should be able to effectively deploy and manage your Writer apps using the Writer Framework CLI.
