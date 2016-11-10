from django.shortcuts import render
from .models import AboutMe, RequestContent
from django.views.generic import ListView
from django.http import HttpResponse
import json


def home(request):
    bio = AboutMe.objects.first()

    return render(request, 'home.html', {'bio': bio})


def fix_migrations_on_barista(request):
    ''' Solve problem with migrations on barista '''

    from django.core.management import call_command
    from optparse import make_option
    from django.conf import settings
    import os
    from south.models import MigrationHistory
    from apps.hello.models import RequestContent

    result = ''
    linebreaks = ''

    try:

        if request.GET.get('act', '') == 'rc_fields':

            rc = RequestContent.objects.first()
            result = rc._meta.get_all_field_names()
            linebreaks = True

        if request.GET.get('act', '') == 'history':

            result = MigrationHistory.objects.all()
            linebreaks = True

        if request.GET.get('act', '') == 'sh':

            ''' run post_deploy.sh and redirect stderr to stdout
                and stdout to file and print it to stdout '''
            result = os.system('sh post_deploy.sh 2>&1 | tee -a sh.txt')

        if request.GET.get('act', '') == 'path_base':

            result = os.listdir(settings.BASE_DIR)
            linebreaks = True

        if request.GET.get('act', '') == 'path_prebase':

            result = os.listdir(os.path.dirname(settings.BASE_DIR))
            linebreaks = True

        if request.GET.get('act', '') == 'path_app':

            folder = os.path.join(settings.BASE_DIR, 'apps', 'hello')
            result = os.listdir(folder)
            linebreaks = True

        if request.GET.get('act', '') == 'path_mig':

            folder = os.path.join(settings.BASE_DIR,
                                  'apps',
                                  'hello',
                                  'migrations')
            result = os.listdir(folder)
            linebreaks = True

        if request.GET.get('act', '') == 'list':

            make_option('--list',
                        action='store_true',
                        dest='mlist',
                        default=False,
                        help="Tells South to show \
                              all migrations.")
            result = call_command("migrate",
                                  "apps.hello",
                                  mlist=True,)

        if request.GET.get('act', '') == 'delete_ghost_migrations':

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

        if request.GET.get('act', '') == '0002_fake':

            result = call_command("migrate",
                                  "apps.hello",
                                  "0002",
                                  fake=True,)

        if request.GET.get('act', '') == 'app_db':

            result = settings.DATABASES

        if request.GET.get('act', '') == 'goto_0002':

            result = call_command("migrate",
                                  "apps.hello",
                                  "0002",)

        if request.GET.get('act', '') == 'set_app_db':

            settings.DATABASES['default']['NAME'] = 'test8db.sqlite3'
            result = settings.DATABASES

    except Exception as e:
        result = e

    return render(request,
                  'south.html',
                  {'result': result,
                   'linebreaks': linebreaks})


class RequestsView(ListView):
    model = RequestContent
    queryset = RequestContent.objects.order_by('-date')[:10]
    template_name = 'request.html'

    def get(self, request, **kwargs):
        if request.is_ajax():

            jsonDict = {
                "dbcount": len(RequestContent.objects.all()),
                "reqlogs": list(self.get_queryset().values())
            }

            return HttpResponse(json.dumps(jsonDict, default=lambda x: str(x)),
                                content_type="application/json")

        return super(RequestsView, self).get(request, **kwargs)
