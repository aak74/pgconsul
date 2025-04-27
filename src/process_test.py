import pytest
from datetime import datetime

from .process import Process, Event


@pytest.fixture
def process():
    return Process(name='test_process', stages=['A', 'B', 'C'])


class TestProcess:
    def test_init(self, process: Process):
        assert process.name == 'test_process'
        assert isinstance(process.ts_start, float)
        assert process.ts_end is None
        assert process._stage_ordered == ['A', 'B', 'C']
        assert process._stages == {'A': None, 'B': None, 'C': None}
        assert process._current_stage_idx == -1
        assert process._current_stage is None

    def test_start_stop_process(self, process: Process):
        original_ts_start = process.ts_start
        process.start()
        assert process.ts_start != original_ts_start
        assert process.is_started()
        process.stop()
        assert process.is_stopped() is not None

    def test_stage_valid_stage_name(self, process: Process):
        event = process.start_stage('A')
        assert isinstance(event, Event)
        assert event.name == 'A'
        assert process.stage('A').is_started()
        event = process.stop_stage('A')
        assert process.stage('A').is_stopped()

    def test_stage_invalid_stage_name(self, process: Process):
        with pytest.raises(ValueError) as e:
            process.stage('invalid_stage')
        assert str(e.value) == 'Invalid stage name: invalid_stage'

        with pytest.raises(ValueError) as e:
            process.start_stage('invalid_stage')
        assert str(e.value) == 'Invalid stage name: invalid_stage'

        with pytest.raises(ValueError) as e:
            process.stop_stage('invalid_stage')
        assert str(e.value) == 'Invalid stage name: invalid_stage'

    def test_start_stage_current_stage_cannot_be_restarted(self, process: Process):
        process.start_stage('A')
        with pytest.raises(ValueError) as e:
            process.start_stage('A')
        assert str(e.value) == 'Current stage can not be restarted'

    def test_is_started(self, process: Process):
        assert process.is_started()
        process.ts_start = None
        assert not process.is_started()

    def test_is_stopped(self, process: Process):
        assert not process.is_stopped()
        process.ts_end = datetime.now().timestamp()
        assert process.is_stopped()

    def test_is_stage_stopped(self, process: Process):
        process.start_stage('A')
        process.stop_stage('A')
        assert process.stage('A').is_stopped()

    def test_stage_sequence_ok(self, process: Process):
        process.start_stage('A')
        process.start_stage('B')
        process.start_stage('C')
        process.stop_stage('C')

    def test_stage_sequence_wrong_order(self, process: Process):
        with pytest.raises(ValueError) as e:
            process.start_stage('B')
        assert str(e.value) == 'Previous stage is not stopped'

        process.start_stage('A')

        with pytest.raises(ValueError) as e:
            process.start_stage('C')
        assert str(e.value) == 'Previous stage is not stopped'

    def test_create_from_json(self):
        data = '{"name": "test_process", "time": {"ts_start": 1740000000, "ts_end": 1740000010}, "stages": {"A": {"name": "A", "ts_start": 1740000000, "ts_end": 1740000010}, "B": null, "C": null}}'
        process = Process.from_json(data)
        assert process.name == 'test_process'
        assert process.stage('A').ts_start == 1740000000
        assert process.stage('A').ts_end == 1740000010
        assert process.stage('B') is None
        assert process.stage('C') is None

