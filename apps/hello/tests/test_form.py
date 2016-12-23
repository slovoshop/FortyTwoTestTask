# -*- coding: utf-8 -*-
from django.test import TestCase
from apps.hello.forms import ProfileUpdateForm, MessageForm
from apps.hello.models import AboutMe, Message
from datetime import date
from apps.hello.utils import GetTestImage


NORMAL = {"id": 1,
          "first_name": "Alex",
          "last_name": "Testenko",
          "birthday": date(1999, 9, 19),
          "email": "mail@alex.com",
          "jabber": "j",
          "skype": "s",
          "bio": "some text",
          "contacts": "Allo ullu olla"}


class ProfileUpdateFormTests(TestCase):

    def test_form_and_db_data_equal(self):
        """
        Check that form saves correct data
        """
        instance = AboutMe.objects.first()

        form = ProfileUpdateForm(NORMAL,
                                 {'photo': GetTestImage('test.png')},
                                 instance=instance)

        self.assertTrue(form.is_valid())
        form.save()

        # check database and form data equals
        profile = AboutMe.objects.first()

        for field in profile._meta.get_all_field_names():
            value = getattr(profile, field)
            if field != "photo":
                self.assertEqual(value, form.data[field])

    def test_blank_and_invalid_data(self):
        """
        Send empty data and invalid date and check form
        for required fields and valid date
        """
        form = ProfileUpdateForm({'birthday': '1999-0919'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
                         {'first_name': [u'This field is required.'],
                          'last_name': [u'This field is required.'],
                          'birthday': [u'Enter a valid date.'],
                          'skype': [u'This field is required.'],
                          'jabber': [u'This field is required.'],
                          'email': [u'This field is required.']
                          })

    def test_form_save_and_resize_image(self):
        """
        Check that form saves and resizes image to 200x200
        """
        instance = AboutMe.objects.first()

        image = GetTestImage('test.png', 'PIL')
        self.assertGreater(image.height, 200)
        self.assertGreater(image.width, 200)

        form = ProfileUpdateForm(NORMAL,
                                 {'photo': GetTestImage('test.png')},
                                 instance=instance)

        self.assertTrue(form.is_valid())
        form.save()

        # check image resize
        profile = AboutMe.objects.first()
        image_resized = GetTestImage(profile.photo, 'PIL')
        self.assertLessEqual(image_resized.height, 200)
        self.assertLessEqual(image_resized.width, 200)


class MessageFormTests(TestCase):
    """ Test MessageForm """

    def test_form_and_db_data_equal(self):
        """
        Check that form saves correct data
        """

        form = MessageForm({'text': u'Привет'})
        self.assertTrue(form.is_valid())

        message = Message.objects.first()
        message.text = u'Привет'
        message.save()

        self.assertEqual(message.text, form.data['text'])

    def test_blank_and_too_long_data(self):
        """
        Send empty data and too long data and check form
        for required field and max_length
        """
        form = MessageForm({'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
                         {'text': [u'This field is required.']})

        long_text = ''
        for i in range(513):
            long_text += '!'

        form = MessageForm({'text': long_text})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
                         {'text': [u'Ensure this value has at most ' +
                                   u'512 characters (it has 513).']})
