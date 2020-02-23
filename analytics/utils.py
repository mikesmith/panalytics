from django.utils.crypto import get_random_string


def do_not_track(request):
    try:
        dnt = request.headers['dnt']
    except KeyError:
        dnt = None

    return dnt == '1'


def get_tracking_id():
    return f'PA-{get_random_string(9).upper()}'
