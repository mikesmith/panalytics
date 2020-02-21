
def do_not_track(request):
    try:
        dnt = request.headers['dnt']
    except KeyError:
        dnt = None

    return dnt == '1'
