"""
    :codeauthor: Jayesh Kariya <jayeshk@saltstack.com>
"""


import salt.modules.logrotate as logrotate
from salt.exceptions import SaltInvocationError
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.mock import MagicMock, patch
from tests.support.unit import TestCase

PARSE_CONF = {
    "include files": {"rsyslog": ["/var/log/syslog"]},
    "rotate": 1,
    "/var/log/wtmp": {"rotate": 1},
}


class LogrotateTestCase(TestCase, LoaderModuleMockMixin):
    """
    Test cases for salt.modules.logrotate
    """

    def setup_loader_modules(self):
        return {logrotate: {}}

    # 'show_conf' function tests: 1

    def test_show_conf(self):
        """
        Test if it show parsed configuration
        """
        with patch("salt.modules.logrotate._parse_conf", MagicMock(return_value=True)):
            self.assertTrue(logrotate.show_conf())

    # 'set_' function tests: 4

    def test_set(self):
        """
        Test if it set a new value for a specific configuration line
        """
        with patch(
            "salt.modules.logrotate._parse_conf", MagicMock(return_value=PARSE_CONF)
        ), patch.dict(
            logrotate.__salt__, {"file.replace": MagicMock(return_value=True)}
        ):
            self.assertTrue(logrotate.set_("rotate", "2"))

    def test_set_failed(self):
        """
        Test if it fails to set a new value for a specific configuration line
        """
        with patch(
            "salt.modules.logrotate._parse_conf", MagicMock(return_value=PARSE_CONF)
        ):
            kwargs = {"key": "/var/log/wtmp", "value": 2}
            self.assertRaises(SaltInvocationError, logrotate.set_, **kwargs)

    def test_set_setting(self):
        """
        Test if it set a new value for a specific configuration line
        """
        with patch.dict(
            logrotate.__salt__, {"file.replace": MagicMock(return_value=True)}
        ), patch(
            "salt.modules.logrotate._parse_conf", MagicMock(return_value=PARSE_CONF)
        ):
            self.assertTrue(logrotate.set_("/var/log/wtmp", "rotate", "2"))

    def test_set_setting_failed(self):
        """
        Test if it fails to set a new value for a specific configuration line
        """
        with patch(
            "salt.modules.logrotate._parse_conf", MagicMock(return_value=PARSE_CONF)
        ):
            kwargs = {"key": "rotate", "value": "/var/log/wtmp", "setting": "2"}
            self.assertRaises(SaltInvocationError, logrotate.set_, **kwargs)

    def test_get(self):
        """
        Test if get a value for a specific configuration line
        """
        with patch(
            "salt.modules.logrotate._parse_conf", MagicMock(return_value=PARSE_CONF)
        ):
            # A single key returns the right value
            self.assertEqual(logrotate.get("rotate"), 1)

            # A single key returns the wrong value
            self.assertNotEqual(logrotate.get("rotate"), 2)

            # A single key returns the right stanza value
            self.assertEqual(logrotate.get("/var/log/wtmp", "rotate"), 1)

            # A single key returns the wrong stanza value
            self.assertNotEqual(logrotate.get("/var/log/wtmp", "rotate"), 2)

            # Ensure we're logging the message as debug not warn
            with patch.object(logrotate, "_LOG") as log_mock:
                res = logrotate.get("/var/log/utmp", "rotate")
                self.assertTrue(log_mock.debug.called)
                self.assertFalse(log_mock.warn.called)
