#encoding: utf-8


from django.core.management.base import BaseCommand

from filemonitor.models import Config, BaseLineFile

class Command(BaseCommand):
    help = 'Init File BaseLine Info'

    def handle(self, *args, **kwargs):
        configs = Config.get_config('filemonitor', '')
        paths = configs.get('paths')
        BaseLineFile.build(paths)
