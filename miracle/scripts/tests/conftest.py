import shutil
import tempfile

import pytest


@pytest.yield_fixture(scope='function')
def tmp_path():
    try:
        path = tempfile.mkdtemp()
        yield path
    finally:
        shutil.rmtree(path)
