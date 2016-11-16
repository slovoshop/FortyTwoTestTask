from django.shortcuts import render
from .models import AboutMe, RequestContent
from django.views.generic import ListView, UpdateView
from .forms import ProfileUpdateForm
from django.http import HttpResponse, HttpResponseBadRequest
import json
import utils
from django.core.urlresolvers import reverse
import logging
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import os


logger = logging.getLogger(__name__)


def home(request):
    bio = None
    photo_exists = False

    # check if there are entries in the db
    try:
        bio = AboutMe.objects.first()

    except IndexError:
        pass

    if bio:
        host, name = utils.check_no_image_in_db(bio)
        file_path = host + name

        if file_path:
            photo_exists = utils.check_no_image_in_filesystem(file_path)

    return render(request,
                  'home.html',
                  {'bio': bio, 'photo_exists': photo_exists})


def fix_migrations_on_barista(request):
    ''' Solve problem with migrations on barista '''

    command = request.GET.get('act', '')

    result, linebreaks = utils.FixBarista(command)

    return render(request,
                  'south.html',
                  {'result': result,
                   'linebreaks': linebreaks})


class RequestsView(ListView):
    model = RequestContent
    queryset = RequestContent.objects.order_by('-date')[:10]
    template_name = 'request.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RequestsView, self).dispatch(*args, **kwargs)

    def get(self, request, **kwargs):
        if request.is_ajax():

            jsonDict = {
                "dbcount": len(RequestContent.objects.all()),
                "reqlogs": list(self.get_queryset().values())
            }

            return HttpResponse(json.dumps(jsonDict, default=lambda x: str(x)),
                                content_type="application/json")

        return super(RequestsView, self).get(request, **kwargs)


class ProfileUpdateView(UpdateView):
    model = AboutMe
    form_class = ProfileUpdateForm
    template_name = 'edit.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProfileUpdateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('hello:edit', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super(ProfileUpdateView, self).get_context_data(**kwargs)

        photo_exists = os.path.isfile(self.object.photo.path) \
            if self.object.photo else False

        if not photo_exists:
            message = "File doesn't exist: {}".format(self.object.photo.url) \
                if self.object.photo else "User has no photo"
            logger.exception(message)

        context['photo_exists'] = photo_exists
        return context

    def form_valid(self, form):
        """
        If the request is ajax, save the form and return a json response.
        Otherwise return super as expected.
        """

        if self.request.is_ajax():
            form.save()
            profile_to_json = {'status': "success"}
            return HttpResponse(json.dumps(profile_to_json),
                                content_type="application/json")

        return super(ProfileUpdateView, self).form_valid(form)

    def form_invalid(self, form):
        """
        If the request is ajax, save the form and return a json response.
        Otherwise return super as expected.
        """

        if self.request.is_ajax():
            errors_dict = {}
            if form.errors:
                for error in form.errors:
                    errors_dict[error] = form.errors[error]
            return HttpResponseBadRequest(json.dumps(errors_dict))

        return super(ProfileUpdateView, self).form_invalid(form)

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            try:
                return super(ProfileUpdateView,
                             self).post(request, *args, **kwargs)
            except IOError:
                message = "File doesn't exist:  " + self.object.photo.url
                logger.exception(message)
                return HttpResponseBadRequest(
                          json.dumps({'Image': message}),
                          content_type="application/json")

        return super(ProfileUpdateView, self).post(request, *args, **kwargs)
