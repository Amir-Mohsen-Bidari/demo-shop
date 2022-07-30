from django.contrib.sessions.models import Session

def session_check(request):
    if request.session.session_key == None:
        request.session.create()
    return {}