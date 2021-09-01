import os
import tempfile

from pathlib import Path

i = int(os.environ.get('TEARDOWN_RAN', '0'))
i += 1
os.environ['TEARDOWN_RAN'] = str(i)
