import subprocess
from typing import Tuple, Optional
import logging

log = logging.getLogger(__name__)

import config


def run_test(solution_path: str, input: str, expected_output: str) -> Tuple[bool, Optional[str]]:
    input = f'{input}\n\n\n\n'.encode()
    process = subprocess.Popen([f'python3.7 {solution_path}'], cwd=config.PROJECT_DIR, shell=True,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,)
    try:
        out, err = process.communicate(input, config.TASK_TIMEOUT)
        if process.returncode != 0:
            stderr = err.decode().strip().split('\n')
            if not stderr:
                return False, 'Runtime error'
            log.error(f'{process.returncode} {stderr}')
            return False, stderr[-1].split(':')[0]
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        print(process.args)
        log.error(f'{process.returncode, process.stderr.read().decode(), process.stdout.read().decode()}')
        return False, 'Time Limit Extended'

    if expected_output != out.decode().strip():
        log.error(f'{expected_output} {out.decode().strip()}')
        return False, 'Wrong Answer'
    return True, None
