# -*- coding: utf-8 -*-
from django.test import TestCase
from apps.hello.models import AboutMe, RequestContent
from django.utils.encoding import smart_unicode

NORMAL = {
    "method": "GET",
    "path": "/request/",
    "status_code": "200",
    "date": "November 08, 2016, 08:23"
}


class AboutMeModelTest(TestCase):
    """Test AboutMe model"""

    def test_unicode(self):
        """ test that __unicode__ returns
        <first_name last_name> """

        bio = AboutMe(first_name=u'Розробник', last_name=u'Джанго')
        self.assertEqual(smart_unicode(bio), u'Розробник Джанго')


class RequestContentModelTest(TestCase):
    """Test RequestContent model"""

    def setUp(self):
        self.normal_info = NORMAL
        self.new_info = RequestContent.objects.create(**self.normal_info)

    def test_fields(self):
        """ check model fields """
        for key in self.normal_info.keys():
            if key != 'date':
                self.assertEquals(unicode(self.normal_info[key]),
                                  getattr(self.new_info, key))

    def test_unicode_label(self):
        """ test __unicode__ """

        info = RequestContent(path=u'шлях_запиту',
                              date='July 18, 2016, 09:30 a.m.')
        self.assertEqual(smart_unicode(info),
                         u'шлях_запиту July 18, 2016, 09:30 a.m.')


class ThreadModelTest(TestCase):
    """Test Thread model"""

    def test_get_participants(self):
        """ test admin display for threads """
        user1 = User.objects.create_user(username='alex')
        user2 = User.objects.create_user(username='leon')

        thread = Thread()
        thread.save()
        thread.participants.add(user1, user2)
        thread.lastid = 10
        thread.save()
        print(thread.participants.all())

        admin_display = '1 alex leon (last message ID: 10)'
        self.assertEqual(thread.get_participants(), admin_display)
