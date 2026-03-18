"""
Unit tests for TowerScout event system.

Tests event handling, progress tracking, and user cancellation functionality.
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import threading
import time

# Import event system modules (imports handled by conftest.py)
from ts_events import set_event, get_event, clear_events, create_exit_event


class TestEventSystem(unittest.TestCase):
    """Test the event handling system."""

    def setUp(self):
        """Set up test environment."""
        self.test_session_id = 'test_session_12345'
        # Clear any existing events
        clear_events(self.test_session_id)

    def tearDown(self):
        """Clean up after tests."""
        clear_events(self.test_session_id)

    def test_set_and_get_event(self):
        """Test basic event setting and getting."""
        test_event = {
            'progress': 25,
            'message': 'Processing tiles...',
            'status': 'running'
        }
        
        set_event(self.test_session_id, test_event)
        retrieved_event = get_event(self.test_session_id)
        
        self.assertEqual(retrieved_event['progress'], 25)
        self.assertEqual(retrieved_event['message'], 'Processing tiles...')
        self.assertEqual(retrieved_event['status'], 'running')

    def test_get_event_no_session(self):
        """Test getting event for non-existent session."""
        result = get_event('non_existent_session')
        
        # Should return default/empty event structure
        self.assertIn('status', result)
        self.assertEqual(result['status'], 'no_session')

    def test_event_overwrite(self):
        """Test that events are properly overwritten."""
        # Set initial event
        initial_event = {
            'progress': 10,
            'message': 'Starting...',
            'status': 'starting'
        }
        set_event(self.test_session_id, initial_event)
        
        # Set updated event
        updated_event = {
            'progress': 50,
            'message': 'Half complete...',
            'status': 'running'
        }
        set_event(self.test_session_id, updated_event)
        
        # Should get updated event
        result = get_event(self.test_session_id)
        self.assertEqual(result['progress'], 50)
        self.assertEqual(result['message'], 'Half complete...')

    def test_clear_events(self):
        """Test clearing events for a session."""
        # Set test event
        test_event = {
            'progress': 75,
            'message': 'Almost done...',
            'status': 'running'
        }
        set_event(self.test_session_id, test_event)
        
        # Verify event exists
        self.assertEqual(get_event(self.test_session_id)['progress'], 75)
        
        # Clear events
        clear_events(self.test_session_id)
        
        # Should return no session status
        result = get_event(self.test_session_id)
        self.assertEqual(result['status'], 'no_session')

    def test_multiple_sessions(self):
        """Test event isolation between sessions."""
        session1_id = 'session_001'
        session2_id = 'session_002'
        
        # Set different events for each session
        event1 = {'progress': 30, 'status': 'processing', 'message': 'Session 1'}
        event2 = {'progress': 60, 'status': 'analyzing', 'message': 'Session 2'}
        
        set_event(session1_id, event1)
        set_event(session2_id, event2)
        
        # Events should be isolated
        result1 = get_event(session1_id)
        result2 = get_event(session2_id)
        
        self.assertEqual(result1['message'], 'Session 1')
        self.assertEqual(result2['message'], 'Session 2')
        self.assertEqual(result1['progress'], 30)
        self.assertEqual(result2['progress'], 60)
        
        # Clean up
        clear_events(session1_id)
        clear_events(session2_id)

    def test_create_exit_event(self):
        """Test exit event creation for cancellation."""
        exit_event = create_exit_event()
        
        # Should be a threading event
        self.assertIsInstance(exit_event, threading.Event)
        
        # Should start as not set
        self.assertFalse(exit_event.is_set())
        
        # Should be settable
        exit_event.set()
        self.assertTrue(exit_event.is_set())


class TestProgressTracking(unittest.TestCase):
    """Test progress tracking functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_session_id = 'progress_test_session'
        clear_events(self.test_session_id)

    def tearDown(self):
        """Clean up after tests."""
        clear_events(self.test_session_id)

    def test_progress_sequence(self):
        """Test a sequence of progress updates."""
        progress_sequence = [
            {'progress': 0, 'message': 'Starting detection...', 'status': 'starting'},
            {'progress': 25, 'message': 'Processing tiles...', 'status': 'processing'},
            {'progress': 50, 'message': 'Running detection...', 'status': 'detecting'},
            {'progress': 75, 'message': 'Analyzing results...', 'status': 'analyzing'},
            {'progress': 100, 'message': 'Complete!', 'status': 'complete'}
        ]
        
        for event in progress_sequence:
            set_event(self.test_session_id, event)
            result = get_event(self.test_session_id)
            
            self.assertEqual(result['progress'], event['progress'])
            self.assertEqual(result['status'], event['status'])

    def test_progress_validation(self):
        """Test progress value validation."""
        # Valid progress values
        valid_progress = [0, 25, 50, 75, 100]
        
        for progress in valid_progress:
            event = {
                'progress': progress,
                'message': f'Progress: {progress}%',
                'status': 'running'
            }
            set_event(self.test_session_id, event)
            result = get_event(self.test_session_id)
            self.assertEqual(result['progress'], progress)

    def test_error_event_handling(self):
        """Test handling of error events."""
        error_event = {
            'progress': 0,
            'message': 'Detection failed: Network error',
            'status': 'error',
            'error': 'NetworkError: Unable to connect to map provider'
        }
        
        set_event(self.test_session_id, error_event)
        result = get_event(self.test_session_id)
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)
        self.assertIn('Network error', result['message'])

    def test_cancellation_event(self):
        """Test cancellation event handling."""
        cancellation_event = {
            'progress': 0,
            'message': 'Detection cancelled by user',
            'status': 'cancelled'
        }
        
        set_event(self.test_session_id, cancellation_event)
        result = get_event(self.test_session_id)
        
        self.assertEqual(result['status'], 'cancelled')
        self.assertIn('cancelled', result['message'])


class TestThreadSafety(unittest.TestCase):
    """Test thread safety of event system."""

    def setUp(self):
        """Set up test environment."""
        self.test_session_id = 'thread_test_session'
        clear_events(self.test_session_id)

    def tearDown(self):
        """Clean up after tests."""
        clear_events(self.test_session_id)

    def test_concurrent_event_setting(self):
        """Test concurrent event setting from multiple threads."""
        num_threads = 10
        events_per_thread = 5
        results = []
        
        def set_events(thread_id):
            """Function to set events from a thread."""
            for i in range(events_per_thread):
                event = {
                    'progress': i * 20,
                    'message': f'Thread {thread_id}, Event {i}',
                    'status': 'running',
                    'thread_id': thread_id
                }
                set_event(self.test_session_id, event)
                time.sleep(0.001)  # Small delay to allow interleaving
        
        # Create and start threads
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=set_events, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Get final event - should be valid regardless of thread interleaving
        final_event = get_event(self.test_session_id)
        self.assertIn('progress', final_event)
        self.assertIn('status', final_event)

    def test_concurrent_read_write(self):
        """Test concurrent reading and writing of events."""
        write_results = []
        read_results = []
        
        def writer():
            """Function to continuously write events."""
            for i in range(20):
                event = {
                    'progress': i * 5,
                    'message': f'Write iteration {i}',
                    'status': 'running',
                    'iteration': i
                }
                set_event(self.test_session_id, event)
                write_results.append(i)
                time.sleep(0.001)
        
        def reader():
            """Function to continuously read events."""
            for i in range(20):
                event = get_event(self.test_session_id)
                read_results.append(event)
                time.sleep(0.001)
        
        # Start writer and reader threads
        writer_thread = threading.Thread(target=writer)
        reader_thread = threading.Thread(target=reader)
        
        writer_thread.start()
        reader_thread.start()
        
        writer_thread.join()
        reader_thread.join()
        
        # Verify operations completed
        self.assertEqual(len(write_results), 20)
        self.assertEqual(len(read_results), 20)
        
        # All read results should be valid events
        for event in read_results:
            self.assertIn('status', event)


class TestEventSystemPerformance(unittest.TestCase):
    """Test performance characteristics of event system."""

    def test_event_setting_performance(self):
        """Test performance of event setting operations."""
        session_id = 'performance_test'
        num_operations = 1000
        
        start_time = time.time()
        
        for i in range(num_operations):
            event = {
                'progress': i % 101,
                'message': f'Operation {i}',
                'status': 'running'
            }
            set_event(session_id, event)
        
        elapsed_time = time.time() - start_time
        
        # Should be fast (less than 1 second for 1000 operations)
        self.assertLess(elapsed_time, 1.0)
        
        # Clean up
        clear_events(session_id)

    def test_event_getting_performance(self):
        """Test performance of event getting operations."""
        session_id = 'get_performance_test'
        
        # Set initial event
        initial_event = {
            'progress': 50,
            'message': 'Test message',
            'status': 'running'
        }
        set_event(session_id, initial_event)
        
        num_operations = 1000
        start_time = time.time()
        
        for i in range(num_operations):
            event = get_event(session_id)
            # Basic validation to ensure event is retrieved
            self.assertIn('status', event)
        
        elapsed_time = time.time() - start_time
        
        # Should be very fast (less than 0.5 seconds for 1000 operations)
        self.assertLess(elapsed_time, 0.5)
        
        # Clean up
        clear_events(session_id)

    def test_memory_usage_with_many_sessions(self):
        """Test memory behavior with many concurrent sessions."""
        num_sessions = 100
        session_ids = [f'memory_test_session_{i}' for i in range(num_sessions)]
        
        # Set events for many sessions
        for session_id in session_ids:
            event = {
                'progress': 50,
                'message': 'Memory test event',
                'status': 'running'
            }
            set_event(session_id, event)
        
        # Verify all events are retrievable
        for session_id in session_ids:
            event = get_event(session_id)
            self.assertEqual(event['message'], 'Memory test event')
        
        # Clean up all sessions
        for session_id in session_ids:
            clear_events(session_id)


if __name__ == '__main__':
    unittest.main()