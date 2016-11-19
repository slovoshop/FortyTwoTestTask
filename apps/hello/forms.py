# -- coding: utf-8 --
from django.forms import ModelForm
from .models import AboutMe, RequestContent
from django import forms
from widgets import DatePickerWidget
from datetime import date, datetime


class ProfileUpdateForm(ModelForm):
    ''' ModelForm maps AboutMe Model to a Form '''

    class Meta:
        model = AboutMe
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form_widget'}),
            'last_name': forms.TextInput(attrs={'class': 'form_widget'}),
            'email': forms.TextInput(attrs={'class': 'form_widget'}),
            'jabber': forms.TextInput(attrs={'class': 'form_widget'}),
            'skype': forms.TextInput(attrs={'class': 'form_widget'}),
            'contacts': forms.Textarea(attrs={'class': 'form_widget'}),
            'bio': forms.Textarea(attrs={'class': 'form_widget'}),
        }

    birthday = forms.DateField(widget=DatePickerWidget(
        params="dateFormat: 'yy-mm-dd',\
                changeYear: true,\
                yearRange: 'c-115:c'",
        attrs={'class': 'datepicker form_widget'}
        )
      )

    def clean_birthday(self):
        birthday = self.cleaned_data['birthday']

        if birthday < date(1900, 1, 1):
            raise forms.ValidationError("Valid years: 1900-2016.")

        if birthday > datetime.now().date():
            raise forms.ValidationError("Date is older than today.")

        return birthday


class RequestUpdateForm(ModelForm):
    ''' ModelForm maps RequestContent Model to a Form '''

    class Meta:
        model = RequestContent
        widgets = {
            'method': forms.TextInput(attrs={'class': 'form_widget'}),
            'path': forms.TextInput(attrs={'class': 'form_widget'}),
            'date': forms.TextInput(attrs={'class': 'form_widget'}),
            'status_code': forms.TextInput(attrs={'class': 'form_widget'}),
            'priority': forms.TextInput(attrs={'class': 'form_widget'}),
        }
