from django.core.management import call_command
from optparse import make_option
from django.conf import settings
import os
from south.models import MigrationHistory
from apps.hello.models import RequestContent


def FixBarista(command):

    result = 'no command'
    linebreaks = ''

    try:

        if command == 'rc_fields':

            rc = RequestContent.objects.first()
            result = rc._meta.get_all_field_names()
            linebreaks = True

        if command == 'history':

            result = MigrationHistory.objects.all()
            linebreaks = True

        if command == 'sh':

            ''' run post_deploy.sh and redirect stderr to stdout
                and stdout to file and print it to stdout '''
            result = os.system('sh post_deploy.sh 2>&1 | tee -a sh.txt')

        if command == 'path_base':

            result = os.listdir(settings.BASE_DIR)
            linebreaks = True

        if command == 'path_prebase':

            result = os.listdir(os.path.dirname(settings.BASE_DIR))
            linebreaks = True

        if command == 'path_app':

            folder = os.path.join(settings.BASE_DIR, 'apps', 'hello')
            result = os.listdir(folder)
            linebreaks = True

        if command == 'path_mig':

            folder = os.path.join(settings.BASE_DIR,
                                  'apps',
                                  'hello',
                                  'migrations')
            result = os.listdir(folder)
            linebreaks = True

        if command == 'list':

            make_option('--list',
                        action='store_true',
                        dest='mlist',
                        default=False,
                        help="Tells South to show \
                              all migrations.")
            result = call_command("migrate",
                                  "apps.hello",
                                  mlist=True,)

        if command == 'delete_ghost_migrations':

            make_option('--delete-ghost-migrations',
                        action='store_true',
                        dest='delete_ghosts',
                        default=False,
                        help="Tells South to delete any 'ghost' \
                              migrations (ones in the database \
                              but not on disk).")
            make_option('--ignore-ghost-migrations',
                        action='store_true',
                        dest='ignore_ghosts',
                        default=False,
                        help="Tells South to ignore any 'ghost' \
                              migrations (ones in the database \
                              but not on disk).")
            result = call_command("migrate",
                                  "apps.hello",
                                  delete_ghosts=True,
                                  ignore_ghosts=True,)

        if command == '0002_fake':

            result = call_command("migrate",
                                  "apps.hello",
                                  "0002",
                                  fake=True,)

        if command == 'app_db':

            result = settings.DATABASES

        if command == 'goto_0002':

            result = call_command("migrate",
                                  "apps.hello",
                                  "0002",)

        if command == 'set_app_db':

            settings.DATABASES['default']['NAME'] = 'test8db.sqlite3'
            result = settings.DATABASES

    except Exception as e:
        result = e

    return result, linebreaks
