import pytest
from django.test import RequestFactory
from unittest.mock import patch

from ..views import script, collect, PXL

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


@patch('analytics.models.PageView.create_from_request')
def test_collect_calls_create_from_request_when_dnt_disabled_url_exists(
    mock_create_from_request
):
    request = RequestFactory().get('/a.gif',
                                   {'url': 'http://example.com'},
                                   HTTP_DNT='0')
    collect(request)
    assert mock_create_from_request.call_count == 1
    assert mock_create_from_request.call_args[0] == (request,)


@patch('analytics.models.PageView.create_from_request')
def test_collect_calls_create_from_request_when_dnt_not_given_url_exists(
    mock_create_from_request
):
    request = RequestFactory().get('/a.gif', {'url': 'http://example.com'})
    collect(request)
    assert mock_create_from_request.call_count == 1
    assert mock_create_from_request.call_args[0] == (request,)


@patch('analytics.models.PageView.create_from_request')
def test_collect_does_not_call_create_from_request_when_dnt_enabled_url_exists(
    mock_create_from_request
):
    request = RequestFactory().get('/a.gif',
                                   {'url': 'http://example.com'},
                                   HTTP_DNT='1')
    collect(request)
    assert mock_create_from_request.call_count == 0


@patch('analytics.models.PageView.create_from_request')
def test_collect_does_not_call_create_from_request_when_url_not_given(
    mock_create_from_request
):
    request = RequestFactory().get('/a.gif')
    collect(request)
    assert mock_create_from_request.call_count == 0


@patch('analytics.models.PageView.create_from_request')
def test_collect_returns_correct_response_with_valid_request(
    mock_create_from_request
):
    request = RequestFactory().get('/a.gif',
                                   {'url': 'http://example.com'},
                                   HTTP_DNT='0')
    response = collect(request)
    assert response.status_code == 200
    assert response['content-type'] == 'image/gif'
    assert PXL in response.content
    assert response['cache-control'] == 'private, no-cache'


@patch('analytics.models.PageView.create_from_request')
def test_collect_returns_correct_response_with_dnt_enabled(
    mock_create_from_request
):
    request = RequestFactory().get('/a.gif',
                                   {'url': 'http://example.com'},
                                   HTTP_DNT='1')
    response = collect(request)
    assert response.status_code == 200
    assert response['content-type'] == 'image/gif'
    assert PXL in response.content
    assert response['cache-control'] == 'private, no-cache'


@patch('analytics.models.PageView.create_from_request')
def test_collect_returns_correct_response_with_missing_url_in_query(
    mock_create_from_request
):
    request = RequestFactory().get('/a.gif')
    response = collect(request)
    assert response.status_code == 200
    assert response['content-type'] == 'image/gif'
    assert PXL in response.content
    assert response['cache-control'] == 'private, no-cache'
