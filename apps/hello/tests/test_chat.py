
from django.contrib.auth.models import User
from django.test import TestCase, Client, RequestFactory
from django.core.urlresolvers import reverse
from apps.hello.models import Thread, Message
import json


class SimpleTest(TestCase):
    """ SimpleTest """

    fixtures = ['test_chat.json']

    def setUp(self):
        # Every test needs access to the request factory.
        self.client = Client()
        self.client.login(username='admin', password='admin')

        self.factory = RequestFactory()
        self.user = User.objects.get(username='admin')

    def test_session_storage(self):
        # Issue a GET request.
        resp = self.client.get(reverse('hello:user_chat'))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'dialogs.html')

        print('\n session after chat loading \n')
        print('session[admin_ILMID] = ' + str(self.client.session['admin_ILMID']))


        resp = self.client.post('/send/', {
            'text': 'changeDialog to admin-Jaroslav',
            'sender_id': 1,
            'recipient': 'Jaroslav',
            'mode': 'changeDialog'
        })

        print('\n json response after send: ' + resp.content)
        print('session[admin_ILMID] = ' + str(self.client.session['admin_ILMID']))

        resp = self.client.post('/get_new/', {
            'thread_id': 1,
            'username': 'admin',
            'receiver': 'Jaroslav',
            'lastid_buffer': -1
        })

        print(resp.content)
        print('session[admin_ILMID] = ' + str(self.client.session['admin_ILMID']))

        msg = Message()
        msg.sender_id = 1
        msg.thread_id = 1
        msg.text = 'Text'
        msg.save()

        thread = Thread.objects.get(id=1)
        thread.lastid = msg.id
        thread.save()

        resp = self.client.post('/get_new/', {
            'thread_id': 1,
            'username': 'admin',
            'receiver': 'Jaroslav',
            'lastid_buffer': -1
        })

        print(resp.content)
        print('session[admin_ILMID] = ' + str(self.client.session['admin_ILMID']))

