import pytest
from django.test import RequestFactory

from ..views import script

EXPECTED_JAVASCRIPT = """(function(){var w=window,d=document,
    i=new Image,e=encodeURIComponent;i.src='http://127.0.0.1:8000/a.gif?url='+
    e(d.location.href)+'&ref='+e(d.referrer)+'&t='+e(d.title)+'&wiw='+
    e(w.innerWidth)+'&wih='+e(w.innerHeight);})()""".replace('\n', '').replace('    ', '')


@pytest.fixture
def script_get_request():
    return RequestFactory().get('/a.js', content_type='text/javascript')


def test_script_view_200_status(script_get_request):
    response = script(script_get_request)
    assert response.status_code == 200


def test_script_view_content_type(script_get_request):
    response = script(script_get_request)
    assert response['content-type'] == 'text/javascript'


def test_script_returns_javascript_with_domain():
    response = script(script_get_request)
    assert EXPECTED_JAVASCRIPT in str(response.content)
