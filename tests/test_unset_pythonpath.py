import subprocess
import os


def test_unset_pythonpath_script_runs_and_imports_psycopg2():
    script = os.path.join(os.path.dirname(__file__), 'scripts', 'check_unset_pythonpath.sh')
    env = os.environ.copy()
    # Ensure we run with PYTHONPATH set in the caller environment to simulate user's issue
    env['PYTHONPATH'] = '/Users/sundar/Library/Python/3.9/lib/python/site-packages'

    proc = subprocess.run(['bash', script], capture_output=True, text=True, env=env)
    print(proc.stdout)
    print(proc.stderr)
    assert proc.returncode == 0, f"Script failed with exit {proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    assert 'PYTHONPATH is set' in proc.stdout
    assert 'OK: psycopg2 import succeeded' in proc.stdout
    assert 'Integration check passed.' in proc.stdout
