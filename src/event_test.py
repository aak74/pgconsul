import pytest

from datetime import datetime
from unittest.mock import patch
from .event import Event

class TestEvent:
    def test_initialization(self):
        """Test that Event initializes with correct values"""
        event = Event("test_event")
        assert event.name == "test_event"
        assert isinstance(event.ts_start, float)
        assert event.ts_end is None

    def test_start(self):
        """Test that start() updates ts_start"""
        event = Event("test")
        original_ts = event.ts_start
        event.start()
        assert event.ts_start != original_ts

    def test_stop(self):
        """Test that stop() sets ts_end"""
        event = Event("test")
        event.stop()
        assert event.ts_end is not None

    def test_is_started(self):
        """Test is_started() returns correct status"""
        event = Event("test")
        assert event.is_started() is True
        event.ts_start = None
        assert event.is_started() is False

    def test_is_stopped(self):
        """Test is_stopped() returns correct status"""
        event = Event("test")
        assert event.is_stopped() is False
        event.stop()
        assert event.is_stopped() is True

    def test_to_dict(self):
        """Test dictionary serialization"""
        event = Event("test")
        event.stop()
        result = event.to_dict()
        assert result == {
            "name": "test",
            "ts_start": event.ts_start,
            "ts_end": event.ts_end,
            "duration": event.ts_end-event.ts_start,
        }

    def test_from_dict(self):
        """Test dictionary deserialization"""
        test_data = {
            "name": "from_dict_test",
            "ts_start": 1000.0,
            "ts_end": 2000.0
        }
        
        event = Event.from_dict(test_data)
        
        assert event.name == "from_dict_test"
        assert event.ts_start == 1000.0
        assert event.ts_end == 2000.0

    def test_from_dict_missing_ts_end(self):
        """Test deserialization without ts_end"""
        test_data = {
            "name": "no_ts_end",
            "ts_start": 1000.0
        }
        
        event = Event.from_dict(test_data)
        assert event.ts_end is None
