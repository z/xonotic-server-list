import sys
import os

app_dir = os.path.join(os.environ['HOME'], 'xsl')

INTERP = os.path.join(app_dir, 'venv', 'bin', 'python')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.insert(0, app_dir)
sys.path.append(app_dir)
from bin.api import api as application