# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404, redirect
from .models import AboutMe, RequestContent, Thread, Message
from django.views.generic import ListView, UpdateView
from .forms import ProfileUpdateForm, RequestUpdateForm, MessageForm
from django.http import HttpResponse, HttpResponseBadRequest, Http404
import json
import utils
from django.core.urlresolvers import reverse
import logging
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import os
from django.contrib.auth.models import User
from django.conf import settings
import time
import pdb
from django.views.decorators.cache import cache_control, never_cache
import datetime


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


@csrf_exempt
def fix_migrations_on_barista(request):
    ''' Solve problem with migrations on barista '''

    command = request.GET.get('act', '')

    if command == 'read_txt':

        fileContent = ''
        text_file = os.path.join(settings.BASE_DIR, 'setup.txt')
        file = open(text_file)

        for line in file:
            fileContent += line

        json_data = {'fileContent': fileContent}
        return HttpResponse(json.dumps(json_data),
                            content_type="application/json")

    result, linebreaks = utils.FixBarista(command)

    return render(request,
                  'south.html',
                  {'result': result,
                   'linebreaks': linebreaks})


class RequestsView(ListView):
    model = RequestContent
    template_name = 'request.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RequestsView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        if 'priority' in self.request.GET:
            priority = self.request.GET.get('priority', '')

            if priority == '1':
                queryset = RequestContent.objects.order_by('-priority')[:10]
            else:
                queryset = RequestContent.objects.order_by('priority')[:10]

        elif 'date' in self.request.GET:
            date = self.request.GET.get('date', '')

            if date == '1':
                queryset = RequestContent.objects.order_by('-date')[:10]
            else:
                queryset = RequestContent.objects.order_by('date')[:10]

        else:
            queryset = RequestContent.objects.order_by('-date')[:10]

        return queryset

    def get(self, request, **kwargs):
        if request.is_ajax():

            jsonDict = {
                "dbcount": len(RequestContent.objects.all()),
                "reqlogs": list(self.get_queryset().values())
            }

            return HttpResponse(json.dumps(jsonDict, default=lambda x: str(x)),
                                content_type="application/json")

        return super(RequestsView, self).get(request, **kwargs)

    def post(self, request, *args, **kwargs):
        data = request.POST

        ''' get RequestContent object for given request '''
        request_content = RequestContent.objects.get(pk=data['pk'])
        request_content.priority = data['priority']
        request_content.save()

        ''' return JSON '''
        json_data = {	'link_id': '#priority_' + str(request_content.id),
                      'priority': request_content.priority}

        return HttpResponse(json.dumps(json_data),
                            content_type="application/json")


@login_required
def request_edit(request, req_id):
    """
    Returns page with form to edit request on GET.
    Validates form and redirects to /request/ on POST."""

    req = get_object_or_404(RequestContent, pk=req_id)

    if request.method == 'GET':
        form = RequestUpdateForm(instance=req)
        return render(request, 'request_edit.html',
                      {'form': form, 'req_id': req_id})

    elif request.method == 'POST':
        form = RequestUpdateForm(request.POST, instance=req)

        if form.is_valid():
            form.save()
            if request.is_ajax():
                profile_to_json = {'status': "success"}
                return HttpResponse(json.dumps(profile_to_json),
                                    content_type="application/json")
            else:
                return redirect(reverse('hello:request'))

        if form.is_invalid():
            return render(request,
                          'hello/request_edit.html',
                          {'form': form, 'req_id': req_id})
    raise Http404


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


@login_required
def userchat(request):
    threads = Thread.objects.filter(
        participants=request.user
    ).order_by("-lastid")

    # print(request.session.__dict__)

    initLMID = request.user.username + '_ILMID'
    if initLMID not in request.session:
        request.session[initLMID] = {}
    request.session.modified = True
    request.session.save()

    if not request.COOKIES.get(initLMID):
        request.COOKIES[initLMID] = '{}'

    if not threads:
        return render(request,
                      'dialogs.html',
                      {'users': User.objects.exclude(username=request.user)})

    ILMID_dict = utils._scan_threads(threads, request.user.id, init=True)

    for key in ILMID_dict:
        if key not in request.session[initLMID]:
            request.session[initLMID][key] = ILMID_dict[key]
    request.session.modified = True

    """temp = json.loads(request.COOKIES[initLMID])
    for key in ILMID_dict:
        if key not in temp:
            temp[key] = ILMID_dict[key]
    request.COOKIES[initLMID] = json.dumps(temp)

    print(request.COOKIES)"""

    for thread in threads:
        partner = thread.participants.exclude(id=request.user.id)
        thread.partner = partner[0].username

    resp = render(request,
                  'dialogs.html',
                  {
                    'threads': threads,
                    'users': User.objects.exclude(username=request.user),
                    'initLMID': json.dumps(ILMID_dict)
                  })
    #resp.set_cookie('admin_temp', {'temp': 1})
    #resp.set_cookie(initLMID, temp)
    return resp


@csrf_exempt
@require_POST
@never_cache
def send(request):
    """
    This view is called when the client wants to send a message.
    If the message is saved successfully,
    200 OK with a body containing 'OK' is returned.
    If it fails, json is returned with a body describing the fault.
    """
    # Parse and validate text.
    form = MessageForm(request.POST)

    """admin_temp = json.loads(request.COOKIES['admin_temp'])
    admin_temp['temp'] += 1
    request.COOKIES['admin_temp'] = json.dumps(admin_temp)
    print('>> SEND >> request.COOKIES[admin_temp] = ' + request.COOKIES['admin_temp'])"""

    if not form.is_valid():
        return HttpResponse(json.dumps(form.errors),
                            content_type="application/json")

    sender_id = int(request.POST['sender_id'])
    mode = request.POST['mode']

    # Define dialog members
    sender = User.objects.get(id=sender_id)
    recipient = User.objects.get(username=request.POST['recipient'])

    """if sender.username == 'admin':
        print('sender-' + sender.username + ' >> send started >> session[admin_ILMID] = ' + str(request.session['admin_ILMID']))"""

    initLMID = sender.username + '_ILMID'
    #print(request.COOKIES)
    request.COOKIES[initLMID] = utils._check_initLMID(request.session, sender.username, request.COOKIES)

    if sender.username == 'admin':
        initLMID = sender.username + '_ILMID'
        nowtime = datetime.datetime.now().strftime('%H:%M:%S')
        print('\n' + nowtime + ' admin >> view send >>> after _check_initLMID >> request.session[admin_ILMID] = ' + str(request.session['admin_ILMID']))

    # Get the thread corresponding to the dialog members
    thread_queryset = Thread.objects.filter(participants=recipient).\
        filter(participants=sender)

    if thread_queryset.exists():
        thread = thread_queryset[0]
    else:
        thread = Thread.objects.create()
        thread.participants.add(sender, recipient)

    service_text = 'changeDialog to ' +\
        sender.username + '-' + recipient.username

    """ When the user selects another thread in the left-hand list
        then ajax-post contains service text
        that doesn't need to save in the Message
    """
    if not request.POST['text'] == service_text:
        # Save new message in the backend.
        msg = Message()
        msg.sender_id = sender_id
        msg.thread_id = thread.id
        msg.text = form.cleaned_data['text']
        msg.save()

        # Remember last message ID in the thread
        thread.lastid = msg.id
        thread.save()

    # If user don`t change dialog and just sends a message to the current one
    if mode == 'currentDialog':
        return HttpResponse('OK', content_type='text/plain; charset=UTF-8')

    # update QuerySet of threads with current user
    threads = Thread.objects.\
        filter(participants=sender).\
        order_by("-lastid")

    # prepare data to switch to another dialog
    result = utils._scan_threads(threads, sender_id)

    return HttpResponse(json.dumps(result),
                        content_type="application/json")


@csrf_exempt
@require_POST
def get_new(request):
    """
    This method is called from the client when it wants to check if there are
    any new messages since the last message "id".

    The backend is checked every second for SLEEP_SECONDS. If there are no new
    messages in this interval, "OK" is returned and the client may initiate a
    new request.

    The result of this method, when new messages are available is json similar
    to below:

    {
        messages: [{...}, {...}, ...],
        lastid: 100
    }

    "message" contains HTML that can be injected into a textarea.
     "lastid" is the highest(latest) message ID in the thread.
    """

    SLEEP_SECONDS = 20

    thread_id = int(request.POST['thread_id'])
    username = request.POST['username']
    receiver = request.POST['receiver']
    lastid_buffer = int(request.POST['lastid_buffer'])

    initLMID = username + '_ILMID'
    session_initLMID = request.session.get(initLMID)

    request.COOKIES[initLMID] = utils._check_initLMID(request.session, username, request.COOKIES)

    """if username == 'admin':
        nowtime = datetime.datetime.now().strftime('%H:%M:%S')
        print(nowtime + ' admin-' + receiver + ' >> get_new started >> session[admin_ILMID] = ' + str(request.session._session_cache[initLMID]))
        #pdb.set_trace()"""

    last_id = session_initLMID[receiver] if\
    lastid_buffer in [-1, 0] else lastid_buffer

    # Start long polling cycle
    for _ in range(SLEEP_SECONDS):
        # Get the thread corresponding to the dialog members
        thread = Thread.objects.get(id=thread_id)

        # If no new messages was found, sleep and try again.
        if thread.lastid == last_id:
            # Initial request after dialog changing
            if lastid_buffer == -1:
                response = HttpResponse('No new messages',
                                        content_type='text/plain')
                response['debugtext'] = username + '-' + receiver + ': No new messages'
                return response
            time.sleep(1)
            continue

        """ If new messages was found,
            query the backend for messages since 'lastid' in session
        """
        messages = Message.objects.\
            filter(thread=thread_id, pk__gt=last_id).order_by('pk')

        message_count = messages.count()

        # Never return more than 100 messages at once.
        if message_count > 100:
            messages = messages[message_count - 100:]


        session_initLMID[receiver] = thread.lastid
        #request.session.pop('admin_lastid') try this also
        request.session[initLMID] = session_initLMID
        # Update LMID in the session
        #request.session[initLMID][receiver] = thread.lastid
        #request.COOKIES[initLMID] = request.session[initLMID]
        #temp = request.session[initLMID]
        #request.session.update(temp)
        request.session.save()
        request.session.modified = True

        if username == 'admin':
            nowtime = datetime.datetime.now().strftime('%H:%M:%S')
            print(nowtime + ' admin >> get_new NEW MESSAGES: ' + initLMID + '[' + receiver + '] = ' + str(request.session[initLMID][receiver]))

        # Convert the QuerySet to a dictlist and return result
        result = utils._prepear_new_messages(messages, thread.lastid)
        response = HttpResponse(json.dumps(result),
                                content_type="application/json")
        response['debugtext'] = username + '-' + receiver + ': New messages in JSON'
        return response

    # if the SLEEP_SECONDS interval is ended without new messages
    """if username == 'admin':
        nowtime = datetime.datetime.now().strftime('%H:%M:%S')
        print(nowtime + ' get_new NO NEW: admin_ILMID = ' + str(request.session[initLMID]))"""

    response = HttpResponse('Long polling cycle is ended',
                            content_type='text/plain')
    response['debugtext'] = username + '-' + receiver + ': Long polling cycle is ended'
    return response


@csrf_exempt
@require_POST
@never_cache
def scan_threads(request):

    # long polling interval(LPI) for threads scanning
    # to convert in seconds you have to multiply THREADS_LPI х 5    
    THREADS_LPI = 4

    user_id = int(request.POST['user_id'])
    thread_id = int(request.POST['thread_id'])
    unread_dict = json.loads(request.POST['unread_dict'])

    logged_user = User.objects.get(id=user_id)
    initLMID = logged_user.username + '_ILMID'
    request.COOKIES[initLMID] = utils._check_initLMID(request.session, logged_user.username, request.COOKIES)

    """# This block is for testing
    current_thread = Thread.objects.get(id=thread_id)
    current_partner = current_thread.participants.exclude(id=user_id)[0]
    if logged_user.username == 'admin':
        nowtime = datetime.datetime.now().strftime('%H:%M:%S')
        print(nowtime + ' ' + logged_user.username + '-' + current_partner.username + ' >> scan_threads started')
        for key in request.session[initLMID]:
            if key not in unread_dict:
                unread_dict[key] = 0

        andrey_thread = Thread.objects.get(id=4) # thread admin-Andrey has ID=4
        print(nowtime + ' unread_dict[Andrey] = ' + str(unread_dict['Andrey']))
        print(nowtime + ' andrey_thread.lastid = ' + str(andrey_thread.lastid))
        print(nowtime + ' request.session[admin_ILMID] = ' + str(request.session[initLMID]))
    # End tetsing block"""

    for _ in range(THREADS_LPI):
        # Query the backend for threads with current user.
        threads = Thread.objects.filter(participants=user_id).\
                         order_by("-lastid")

        """ If the user changes current thread or
            new thread appears, then collect information
        """
        if request.POST['changeDialog'] == 'true' or\
        threads.count() > len(request.session[initLMID]):

            result = utils._scan_threads(threads, user_id)
            new_unread = utils._get_unread(threads, request.session[initLMID], user_id)

            """if logged_user.username == 'admin':
                nowtime = datetime.datetime.now().strftime('%H:%M:%S')
                print(nowtime + ' ' + logged_user.username + '-' + current_partner.username + ' >> scan_threads >> new_unread')
                for key in new_unread:
                    if key == 'Andrey':
                        print(nowtime + ' ' + key + ': ' + str(new_unread[key]))"""

            for dialog in result['threads']:
                dialog['unread'] = new_unread[dialog['partner']]

            return HttpResponse(json.dumps(result),
                                content_type="application/json")

        # if any of the threads have new messages, than collect information
        for thread in threads:
            if thread.id == thread_id:
                continue

            partner = thread.participants.exclude(id=user_id)[0]

            """if logged_user.username == 'admin':
                print(logged_user.username + '-' + current_partner.username + ' >>>> THREADS_LPI')
                print('thread.lastid: ' + str(thread.lastid) + '  ' + initLMID + '[' + partner.username + '] = ' + str(request.session[initLMID][partner.username]))"""

            if thread.lastid != request.session[initLMID][partner.username]:
                new_unread = utils._get_unread(threads, request.session[initLMID], user_id)

                if new_unread[partner.username] > unread_dict[partner.username]:
                    result = utils._scan_threads(threads, user_id)

                    """if logged_user.username == 'admin':
                        nowtime = datetime.datetime.now().strftime('%H:%M:%S')
                        print(nowtime + ' ' + logged_user.username + '-' + current_partner.username + ' >>>> THREADS_LPI: new_unread for ' + partner.username + ' >unread')"""

                    for dialog in result['threads']:
                        dialog['unread'] = new_unread[dialog['partner']]
                        """if logged_user.username == 'admin':
                            nowtime = datetime.datetime.now().strftime('%H:%M:%S')
                            print(nowtime + ' new_unread[' + dialog['partner'] + '] = ' + str(new_unread[dialog['partner']]))"""

                    return HttpResponse(json.dumps(result),
                                        content_type="application/json")

        # If no messages was found, sleep and try again.
        time.sleep(5)
        continue

    # If there are no new messages during THREADS_LPI, "OK" is returned
    return HttpResponse('OK', content_type='text/plain')
