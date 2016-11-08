from django.shortcuts import render
from .models import AboutMe, RequestContent
from django.views.generic import ListView
from django.core import serializers
from django.http import HttpResponse


def home(request):
    bio = AboutMe.objects.first()

    return render(request, 'home.html', {'bio': bio})


def fix_migrations_on_barista(request):
    ''' Solve problem with migrations on barista '''

    from django.core.management import call_command
    from optparse import make_option

    result = ''

    if request.GET.get('act', '') == 'run':
        try:
            make_option('--delete-ghost-migrations',
                        action='store_true',
                        dest='delete_ghosts',
                        help="Tells South to delete any 'ghost' \
                              migrations (ones in the database \
                              but not on disk).")
            result = call_command("migrate",
                                  "apps.hello",
                                  delete_ghosts=True,)

        except Exception as e:
            result = e

    return render(request,
                  'south.html',
                  {'result': result})


class RequestsView(ListView):
    model = RequestContent
    queryset = RequestContent.objects.order_by('-date')[:10]
    template_name = 'request.html'

    def get(self, request, **kwargs):
        if request.is_ajax():
            self.object_list = self.get_queryset()
            data = serializers.serialize("json", self.get_queryset())
            return HttpResponse(data, content_type='application/json')

        return super(RequestsView, self).get(request, **kwargs)
