from django.http import HttpResponse
from base64 import b64decode
from django.conf import settings

from .models import PageView
from .utils import do_not_track

JAVASCRIPT = """(function(){var w=window,d=document,
    i=new Image,e=encodeURIComponent;i.src='%s/a.gif?url='+e(d.location.href)+
    '&ref='+e(d.referrer)+'&t='+e(d.title)+'&wiw='+e(w.innerWidth)+'&wih='
    +e(w.innerHeight);})()""".replace('\n', '').replace('    ', '')

# Transparent 1x1 GIF Pixel
PXL = b64decode('R0lGODlhAQABAIAAANvf7wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==')


def script(request):
    response = f'{JAVASCRIPT}' % settings.ANALYTICS_HOST
    return HttpResponse(response, content_type="text/javascript")


def collect(request):
    if not do_not_track(request) and request.GET.get('url'):
        PageView.create_from_request(request)

    response = HttpResponse(PXL, content_type='image/gif')
    response['Cache-Control'] = 'private, no-cache'
    return response
