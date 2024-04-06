import os.path


def fixture(fixture_name) -> str:
    """
    Returns the path of one of the fixture folders based on its name

    >>> fixture_path = fixture('app_dir_simple')
    """
    fixture_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), fixture_name))
    if not os.path.isdir(fixture_dir):
        raise FileNotFoundError(f'the fixture is missing : {fixture_dir}')

    return fixture_dir