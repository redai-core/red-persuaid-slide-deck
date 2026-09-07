import os
import unittest
from unittest.mock import patch
from engine.credentials import (
    resolve_otterly_key,
    has_otterly_key,
    store_token,
    get_stored_token,
)


class TestOtterlyCredentials(unittest.TestCase):
    def test_resolve_otterly_key_override(self):
        with patch("engine.credentials.store_token") as mock_store:
            key = resolve_otterly_key(override="test_key_123")
            self.assertEqual(key, "test_key_123")
            mock_store.assert_called_once_with("test_key_123", key="otterly_api_key")

    def test_resolve_otterly_key_env_var(self):
        with patch.dict(os.environ, {"OTTERLY_API_KEY": "env_key_456"}, clear=False):
            key = resolve_otterly_key(override=None)
            self.assertEqual(key, "env_key_456")

    def test_resolve_otterly_key_stored_fallback(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("engine.credentials.get_stored_token", return_value="stored_key_789") as mock_get:
                key = resolve_otterly_key(override=None)
                self.assertEqual(key, "stored_key_789")
                mock_get.assert_called_once_with("otterly_api_key")

    def test_has_otterly_key_false_when_empty(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("engine.credentials.get_stored_token", return_value=None):
                self.assertFalse(has_otterly_key())


if __name__ == "__main__":
    unittest.main()
