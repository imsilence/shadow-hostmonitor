#encoding: utf-8

import time

from django.core.management.base import BaseCommand

from filemonitor.models import Config, ActualFile

class Command(BaseCommand):
    help = 'Check Actual File Status'

    TIME_SLEEP = 30

    def handle(self, *args, **kwargs):
        curr_time = 0
        last_time = 0

        while True:
            curr_time = time.time()
            configs = Config.get_config('filemonitor', '')
            interval = int(configs.get('interval'))
            paths = configs.get('paths')
            if curr_time >= last_time + interval:
                last_time = curr_time
                ActualFile.build(paths)
            else:
                time.sleep(self.TIME_SLEEP)
