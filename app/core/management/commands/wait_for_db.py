import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to pause execution until database is available"""
    def handle(self, *args, **options):
        # Write to stdout/console
        self.stdout.write('Waiting for db to start...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('Database unavailable waiting for 1 sec...')
                # To give a reasonable amount of time for the db to start
                time.sleep(1)
        # Format success message
        self.stdout.write(self.style.SUCCESS('Database is now available'))
