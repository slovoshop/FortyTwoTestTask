from django.shortcuts import render


def home(request):
    bio = {
        'first_name': 'Oleksiy',
        'last_name': 'Strutynskyy',
        'birthday': 'May 7, 1979',
        'photo': '',
        'email': 'k6_alexstr@ukr.net',
        'jabber': 'alexleon@42cc.co',
        'skype': 'oleksiy.strutynskyy',
        'contacts': 'facebook.com\n\
                     linkedin.com\n\
                     gmail.com',
        'bio': 'I want to be Django Developer.\n\
                Django junior is my first aim.'
    }

    return render(request, 'home.html', {'bio': bio})
