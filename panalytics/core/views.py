from django.http import HttpResponse, Http404
from base64 import b64decode
from django.conf import settings

from .models import PageView, Project
from .utils import do_not_track

JAVASCRIPT = """(function(){var w=window,d=document,
    i=new Image,e=encodeURIComponent;i.src='%s/a.gif?tid=%s&url='
    +e(d.location.href)+'&ref='+e(d.referrer)+'&t='+e(d.title)+'&wiw='
    +e(w.innerWidth)+'&wih='+e(w.innerHeight);})()"""

# Transparent 1x1 GIF Pixel
PXL = b64decode('R0lGODlhAQABAIAAANvf7wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==')


def script(request):
    clean_js = JAVASCRIPT.replace('\n', '').replace('    ', '')
    tid = request.GET.get('tid')
    if not Project.is_valid_tracking_id(tid):
        raise Http404
    response = f'{clean_js}' % (settings.ANALYTICS_HOST, tid)
    return HttpResponse(response, content_type="text/javascript")


def collect(request):
    dnt = do_not_track(request)
    tid = Project.is_valid_tracking_id(request.GET.get('tid'))
    url = request.GET.get('url')

    if not dnt and tid and url:
        PageView.create_from_request(request)

    response = HttpResponse(PXL, content_type='image/gif')
    response['Cache-Control'] = 'private, no-cache'
    return response
