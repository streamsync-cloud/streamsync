import logging
import os
import shutil
import sys
from typing import Optional

import click

import writer.serve
from writer.deploy import cloud

CONTEXT_SETTINGS = {'help_option_names': ['-h', '--help']}
@click.group(
    context_settings=CONTEXT_SETTINGS,
    help="Writer Framework CLI",
)
@click.version_option(None, '--version', '-v')
def main():
    pass

@main.command()
@click.option('--host', default="127.0.0.1", help="Host to run the app on")
@click.option('--port', default=5000, help="Port to run the app on")
@click.argument('path')
def run(path, host, port):
    """Run the app from PATH folder in run mode."""

    abs_path, is_folder = _get_absolute_app_path(path)
    if not is_folder:
        raise click.ClickException("A path to a folder containing a Writer Framework app is required. For example: writer run my_app")

    writer.serve.serve(
        abs_path, mode="run", port=port, host=host, enable_server_setup=True)

@main.command()
@click.option('--host', default="127.0.0.1", help="Host to run the app on")
@click.option('--port', default=5000, help="Port to run the app on")
@click.option('--enable-remote-edit', help="Set this flag to allow non-local requests in edit mode.", is_flag=True)
@click.option('--enable-server-setup', help="Set this flag to enable server setup hook in edit mode.", is_flag=True)
@click.argument('path')
def edit(path, port, host, enable_remote_edit, enable_server_setup):
    """Run the app from PATH folder in edit mode."""

    abs_path, is_folder = _get_absolute_app_path(path)
    if not is_folder:
        raise click.ClickException("A path to a folder containing a Writer Framework app is required. For example: writer edit my_app")

    writer.serve.serve(
        abs_path, mode="edit", port=port, host=host,
        enable_remote_edit=enable_remote_edit, enable_server_setup=enable_server_setup)

@main.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True))
@click.option('--template', help="The template to use when creating a new app.")
def create(path, template):
    """Create a new app in PATH folder."""

    abs_path, _ = _get_absolute_app_path(path)
    if abs_path is None:
        raise click.ClickException("A target folder is required to create a Writer Framework app. For example: writer create my_app")

    create_app(abs_path, template_name=template)

@main.command()
@click.option('--host', default="127.0.0.1", help="Host to run the app on")
@click.option('--port', default=5000, help="Port to run the app on")
@click.option('--enable-remote-edit', help="Set this flag to allow non-local requests in edit mode.", is_flag=True)
def hello(port, host, enable_remote_edit):
    """Create and run a onboarding 'Hello' app."""
    create_app("hello", template_name="hello", overwrite=True)
    writer.serve.serve("hello", mode="edit",
       port=port, host=host, enable_remote_edit=enable_remote_edit,
       enable_server_setup=False)

main.add_command(cloud)

def create_app(app_path: str, template_name: Optional[str], overwrite=False):
    if template_name is None:
        template_name = "default"

    is_folder_created = os.path.exists(app_path)
    is_folder_empty = True if not is_folder_created else len(os.listdir(app_path)) == 0

    if not overwrite and not is_folder_empty:
        logging.error("The target folder must be empty or not already exist.")
        sys.exit(1)

    server_path = os.path.dirname(__file__)
    template_path = os.path.join(server_path, "app_templates", template_name)

    if not os.path.exists(template_path):
        logging.error(f"Template { template_name } couldn't be found.")
        sys.exit(1)

    shutil.copytree(template_path, app_path, dirs_exist_ok=True)

def _get_absolute_app_path(app_path: str):
    is_path_absolute = os.path.isabs(app_path)
    absolute_app_path = app_path if is_path_absolute else os.path.join(os.getcwd(), app_path)
    is_path_folder = absolute_app_path is not None and os.path.isdir(absolute_app_path)
    return absolute_app_path, is_path_folder

if __name__ == "__main__":
    main()
