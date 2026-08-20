from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import FileField


class Command(BaseCommand):
    help = 'Report media files referenced by the database but missing from MEDIA_ROOT'

    def add_arguments(self, parser):
        parser.add_argument('--list', type=int, default=5, help='Missing paths to print per model')

    def handle(self, *args, **options):
        self.stdout.write(f'MEDIA_ROOT: {settings.MEDIA_ROOT}')
        self.stdout.write(f'MEDIA_URL:  {settings.MEDIA_URL}\n')

        total, missing_total = 0, 0
        for model in apps.get_models():
            fields = [f for f in model._meta.get_fields() if isinstance(f, FileField)]
            if not fields:
                continue

            names = [f.name for f in fields]
            missing = []
            checked = 0
            for row in model.objects.only('pk', *names).iterator():
                for name in names:
                    value = getattr(row, name, None)
                    if not value:
                        continue
                    checked += 1
                    if not value.storage.exists(value.name):
                        missing.append(f'{model.__name__}(pk={row.pk}).{name} → {value.name}')

            if not checked:
                continue

            total += checked
            missing_total += len(missing)
            label = f'{model._meta.label}: {checked} file(s)'
            if missing:
                self.stdout.write(self.style.ERROR(f'{label} — {len(missing)} missing'))
                for line in missing[:options['list']]:
                    self.stdout.write(f'    {line}')
                if len(missing) > options['list']:
                    self.stdout.write(f'    … and {len(missing) - options["list"]} more')
            else:
                self.stdout.write(self.style.SUCCESS(f'{label} — all present'))

        self.stdout.write('')
        if missing_total:
            self.stdout.write(self.style.ERROR(
                f'{missing_total} of {total} referenced files are missing from MEDIA_ROOT. '
                'The database and the media volume are out of sync — restore the volume or re-upload.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(f'All {total} referenced media files exist.'))
