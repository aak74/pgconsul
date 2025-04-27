import json
import logging
from .process import Process
from .zk import Zookeeper


class ProcessStorage:
    PROCESS_ROOT = 'process'
    PROCESS_SWITCHOVER = f'{PROCESS_ROOT}/switchover'
    PROCESS_FAILOVER = f'{PROCESS_ROOT}/failover'

    def __init__(self, zk: Zookeeper):
        self.zk = zk
        
    def write_process_info(self, process: Process) -> None:
        try:
            path = f'{self.PROCESS_ROOT}/{process.name}'
            self.zk.ensure_path(path)
            self.zk.write(path, process.__repr__())
        except Exception as e:
            logging.error(f'Failed to write process {process.name}: {str(e)}')
            raise

    def get_process_info(self, name) -> Process:
        try:
            data = self.zk.get(f'{self.PROCESS_ROOT}/{name}')
            if not data:
                raise ValueError(f'Process {name} not found')
            return json.loads(data)
        except Exception as e:
            logging.error(f'Failed to get process {name}: {str(e)}')
            raise
