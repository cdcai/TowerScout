"""Focused proxy tests; mocked responses do not qualify provider availability."""
import json
import sys
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'webapp'))
import towerscout


class LocationSuggestionTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.cache = self.stack.enter_context(tempfile.TemporaryDirectory())
        self.stack.enter_context(patch.object(towerscout, 'MAP_CACHE_DIR', self.cache))
        self.stack.enter_context(patch.object(towerscout, 'azure_api_key', 'synthetic-key'))
        self.allowed = self.stack.enter_context(patch.object(towerscout.rate_limiter, 'is_allowed', return_value=True))
        self.provider = self.stack.enter_context(patch.object(towerscout, 'provider_get', return_value=Mock(
            status_code=200, content=json.dumps({'results': []}).encode('utf-8')
        )))
        self.client = towerscout.app.test_client()

    def request(self, service='suggest', **params):
        return self.client.get(f'/api/maps/azure/{service}', query_string={
            'query': 'Example address', 'limit': 5, **params
        })

    def test_suggestions_use_typeahead_and_do_not_cache_partial_queries(self):
        for _ in range(2):
            response = self.request(limit=20, lat='40', lon='-74')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, 'application/json')
            self.assertTrue(response.cache_control.no_store)
            self.assertEqual(response.json, {'results': []})
        self.assertEqual(self.provider.call_count, 2)
        params = self.provider.call_args.kwargs['params']
        self.assertEqual(params['typeahead'], 'true')
        self.assertEqual(params['limit'], 5)
        self.assertEqual(params['lat'], 40)
        self.assertEqual(params['lon'], -74)
        self.assertEqual(list(Path(self.cache).iterdir()), [])
        self.allowed.assert_called_with('map-azure-suggest:127.0.0.1', max_requests=60, window_seconds=60)

    def test_existing_address_search_keeps_its_cache_and_parameters(self):
        self.assertEqual(self.request('search').status_code, 200)
        self.assertEqual(self.request('search').status_code, 200)
        self.provider.assert_called_once()
        self.assertNotIn('typeahead', self.provider.call_args.kwargs['params'])

    def test_suggestion_rate_limit_fails_before_provider_request(self):
        self.allowed.return_value = False
        self.assertEqual(self.request().status_code, 429)
        self.provider.assert_not_called()

    def test_invalid_queries_and_unapproved_parameters_are_rejected(self):
        for params in ({'query': 'a'}, {'query': '<>\"'}, {'query': 'a' * 1001}, {'typeahead': 'false'}):
            self.assertEqual(self.request(**params).status_code, 400)
        self.provider.assert_not_called()

    def test_suggestion_limit_is_at_least_one(self):
        self.assertEqual(self.request(limit=-5).status_code, 200)
        self.assertEqual(self.provider.call_args.kwargs['params']['limit'], 1)


if __name__ == '__main__':
    unittest.main()
