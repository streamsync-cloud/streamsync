import contextlib
import os
import shutil
import tempfile
from typing import List

import alfred


@alfred.command("ci", help="continuous integration pipeline")
@alfred.option('--front', '-f', help="run for frontend only", is_flag=True, default=False)
@alfred.option('--back', '-b', help="run for backend only", is_flag=True, default=False)
@alfred.option('--e2e', '-e', help="run for end-to-end only", default=None)
def ci(front, back, e2e):
    if back or (not front and not back and not e2e):
        alfred.invoke_command("ci.mypy")
        alfred.invoke_command("ci.pytest")
    if front or (not front and not back and not e2e):
        alfred.invoke_command("npm.lint")
        alfred.invoke_command("npm.test")
        alfred.invoke_command("npm.build")
        alfred.invoke_command("ci.codegen.ui.binding")
    if e2e:
        alfred.invoke_command("npm.e2e", browser=e2e)

@alfred.command("ci.mypy", help="typing checking with mypy on ./src/streamsync")
def ci_mypy():
    alfred.run("mypy ./src/streamsync --exclude app_templates/*")


@alfred.command("ci.pytest", help="run pytest on ./tests")
def ci_test():
    os.chdir("tests")
    alfred.run("pytest")


@alfred.command("ci.codegen.ui.binding", help="check if ui binding is up to date")
def ci_codegen_ui_binding():
    with _preserve_files(["src/streamsync/ui.py", "src/ui/components.json"]):
        _, original_diff, stderr = alfred.run("git diff  src/streamsync/ui.py", exit_on_error=False, stream_stdout=False)
        alfred.invoke_command("npm.codegen.binding.ui")
        _, final_diff, stderr = alfred.run("git diff  src/streamsync/ui.py", exit_on_error=False, stream_stdout=False)
        if original_diff != final_diff:
            print("UI binding is incomplete and has to be regenerated with `alfred npm.codegen.binding.ui`")
            exit(1)


@contextlib.contextmanager
def _preserve_files(path: List[str]):
    """
    Preserve files in a temporary directory and restore them after the context

    :param path: list of files to preserve
    """
    tmpdir = tempfile.mkdtemp()
    try:
        for p in path:
            os.makedirs(os.path.dirname(os.path.join(tmpdir, p)), exist_ok=True)
            shutil.copy(p, os.path.join(tmpdir, p))

        yield
    finally:
        for p in path:
            shutil.copy(os.path.join(tmpdir, p), p)

        shutil.rmtree(tmpdir)


