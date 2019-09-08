from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTests(TestCase):

    def test_wait_for_db_ready(self):
        """Test waiting for db when db is available"""
        # Try retrieving the default db from Django
        # with ConnectionHandler to see if django has a db
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # Make handler's getitem return True
            gi.return_value = True
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 1)

    # Make tests faster by overriding the time.sleep
    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        """Test waiting for db"""
        wait_command = 'django.db.utils.ConnectionHandler.__getitem__'
        with patch(wait_command) as gi:
            # Make ConnectionHandler raise exception
            # for 5 times to simulate
            # that the db is starting up
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
