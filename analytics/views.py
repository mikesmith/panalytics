from django.http import HttpResponse, Http404
from urllib.parse import urlparse
from base64 import b64decode
from django.conf import settings
import re

JAVASCRIPT = """(function(){var w=window,d=document,
    i=new Image,e=encodeURIComponent;i.src='%s/a.gif?url='+e(d.location.href)+
    '&ref='+e(d.referrer)+'&t='+e(d.title)+'&wiw='+e(w.innerWidth)+'&wih='
    +e(w.innerHeight);})()""".replace('\n', '')

# Transparent 1x1 GIF Pixel
PIXEL = b64decode('R0lGODlhAQABAIAAANvf7wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==')


def script(request):
    response = f'{JAVASCRIPT}' % settings.ANALYTICS_HOST
    return HttpResponse(response, content_type="text/javascript")


def collect(request):

    try:
        # Do not collect and return a 404 if Do Not Track is enabled
        dnt = request.headers['dnt']
        if dnt == '1':
            raise Http404
    except KeyError:
        dnt = None

    if not request.GET.get('url'):
        raise Http404

    parsed_url = urlparse(request.GET.get('url'))
    protocol = parsed_url.scheme
    domain = parsed_url.netloc
    path = parsed_url.path
    url = request.GET.get('url')
    ref = request.GET.get('ref')
    title = request.GET.get('t')
    window_width = request.GET.get('wiw')
    window_height = request.GET.get('wih')

    # A unique visit is when referrer domain is not the current domain.
    # which means the user is coming from outside the site's domain
    unique_visit = urlparse(ref).netloc != domain

    # Set referrer to source (email, etc.) if found in site url query
    source = re.search(r'(?<=ref=)\S*', parsed_url.query)
    if source:
        source = source.group(0)
    referer = ref or source

    print(f'Do Not Track = {dnt}')
    print(f'protocol = {protocol}')
    print(f'domain = {domain}')
    print(f'path = {path}')
    print(f'url = {url}')
    print(f'title = {title}')
    print(f'wiw = {window_width}')
    print(f'wih = {window_height}')
    print(f'ref = {ref}')
    print(f'source = {source}')
    print(f'referer = {referer}')
    print(f'Unique Visit = {unique_visit}')

    response = HttpResponse(PIXEL, content_type='image/gif')
    response['Cache-Control'] = 'private, no-cache'
    return response
