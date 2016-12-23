# -*- coding: utf-8 -*-

from django.db import models
from PIL import Image
from django.contrib.auth.models import User


class AboutMe(models.Model):
    """ Profile Model """

    class Meta(object):
        verbose_name = u"Bio"
        verbose_name_plural = u"Biography"

    first_name = models.CharField(
        max_length=256,
        blank=False,
        verbose_name=u"First name")

    last_name = models.CharField(
        max_length=256,
        blank=False,
        verbose_name=u"Last name")

    birthday = models.DateField(
        blank=False,
        verbose_name=u"Birthday",
        null=True)

    email = models.EmailField()

    jabber = models.CharField(
        max_length=256,
        blank=False,
        verbose_name=u"Jabber")

    skype = models.CharField(
        max_length=256,
        blank=False,
        verbose_name=u"Skype")

    bio = models.TextField(
        blank=True,
        verbose_name=u"About me")

    contacts = models.TextField(
        blank=True,
        verbose_name=u"Additional contacts")

    photo = models.ImageField(
        upload_to='photo',
        null=False,
        blank=True,
        verbose_name=u"Photo")

    def __unicode__(self):
        return u"%s %s" % (self.first_name, self.last_name)

    def save(self, *args, **kwargs):
        ''' resize profile image to (200, 200) '''

        size = 200, 200
        super(AboutMe, self).save(*args, **kwargs)
        if self.photo:
            filename = self.photo.path
            image = Image.open(filename)
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(filename)


class RequestContent(models.Model):
    ''' RequestContent Model	'''

    method = models.CharField(max_length=7)
    path = models.TextField('Path', max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    status_code = models.IntegerField('Status code', max_length=3)
    priority = models.IntegerField(max_length=2, default=0)

    def __unicode__(self):
        return u"%s %s" % (self.path, self.date)


class ModelsChange(models.Model):
    ''' Model with entries about creation/updating/deletion
    in models '''

    model = models.CharField(max_length=10)
    datetime = models.DateTimeField(auto_now=True, auto_now_add=True)
    action = models.CharField(max_length=10)


class Thread(models.Model):
    ''' Thread Model	'''

    participants = models.ManyToManyField(User)
    lastid = models.IntegerField(default=1, blank=True, null=True)
    stop = models.BooleanField(default=False)

    def get_participants(self):
        pk = str(self.pk) + " "
        members = " ".join([u.username for u in self.participants.all()])
        lastid = " (last message ID: " + str(self.lastid) + ")"
        admin_display = pk + members + lastid
        return admin_display


class Message(models.Model):
    ''' Message Model	'''

    text = models.TextField(max_length=512)
    sender = models.ForeignKey(User)
    thread = models.ForeignKey(Thread)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%d %s %s" % (self.pk, self.sender, self.text)
