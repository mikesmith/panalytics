import pytest
from django.http import Http404
from django.test import RequestFactory
from unittest.mock import patch

from ..views import script, collect, PXL

JAVASCRIPT = """(function(){var w=window,d=document,
    i=new Image,e=encodeURIComponent;i.src='http://127.0.0.1:8000/a.gif?
    tid=PA-TESTTRACK&url='+e(d.location.href)+'&ref='+e(d.referrer)+'&t='
    +e(d.title)+'&wiw='+e(w.innerWidth)+'&wih='+e(w.innerHeight);})()"""
EXPECTED_JAVASCRIPT = JAVASCRIPT.replace('\n', '').replace('    ', '')


@pytest.fixture
def script_get_request():
    return RequestFactory().get('/a.js',
                                {'tid': 'PA-TESTTRACK'},
                                content_type='text/javascript')


@pytest.fixture
def script_get_request_no_tid():
    return RequestFactory().get('/a.js', content_type='text/javascript')


@patch('analytics.models.Project.is_valid_tracking_id')
def test_script_view_200_status(mock_is_valid_tracking_id, script_get_request):
    mock_is_valid_tracking_id.return_value = True
    response = script(script_get_request)
    assert response.status_code == 200


@patch('analytics.models.Project.is_valid_tracking_id')
def test_script_view_content_type(
    mock_is_valid_tracking_id, script_get_request
):
    mock_is_valid_tracking_id.return_value = True
    response = script(script_get_request)
    assert response['content-type'] == 'text/javascript'


@patch('analytics.models.Project.is_valid_tracking_id')
def test_script_returns_javascript_with_domain(
    mock_is_valid_tracking_id, script_get_request
):
    mock_is_valid_tracking_id.return_value = True
    response = script(script_get_request)
    assert EXPECTED_JAVASCRIPT in str(response.content)


@patch('analytics.models.Project.is_valid_tracking_id')
def test_script_view_raises_404_status_with_invalid_tid(
    mock_is_valid_tracking_id, script_get_request_no_tid
):
    mock_is_valid_tracking_id.return_value = False
    with pytest.raises(Http404):
        script(script_get_request_no_tid)


@patch('analytics.models.Project.is_valid_tracking_id')
@patch('analytics.models.PageView.create_from_request')
def test_collect_calls_create_from_request_when_dnt_disabled_url_exists(
    mock_create_from_request, mock_is_valid_tracking_id
):
    mock_is_valid_tracking_id.return_value = True
    request = RequestFactory().get('/a.gif',
                                   {'url': 'http://example.com',
                                    'tid': 'PA-TESTTRACK'},
                                   HTTP_DNT='0')
    collect(request)

    assert mock_create_from_request.call_count == 1
    assert mock_create_from_request.call_args[0] == (request,)


@patch('analytics.models.Project.is_valid_tracking_id')
@patch('analytics.models.PageView.create_from_request')
def test_collect_calls_create_from_request_when_dnt_not_given_url_exists(
    mock_create_from_request, mock_is_valid_tracking_id
):
    mock_is_valid_tracking_id.return_value = True
    request = RequestFactory().get('/a.gif',
                                   {'url': 'http://example.com',
                                    'tid': 'PA-TESTTRACK'})
    collect(request)

    assert mock_create_from_request.call_count == 1
    assert mock_create_from_request.call_args[0] == (request,)


@patch('analytics.models.Project.is_valid_tracking_id')
@patch('analytics.models.PageView.create_from_request')
def test_collect_does_not_call_create_from_request_when_dnt_enabled_url_exists(
    mock_create_from_request, mock_is_valid_tracking_id
):
    mock_is_valid_tracking_id.return_value = True
    request = RequestFactory().get('/a.gif',
                                   {'url': 'http://example.com',
                                    'tid': 'PA-TESTTRACK'},
                                   HTTP_DNT='1')
    collect(request)

    assert mock_create_from_request.call_count == 0


@patch('analytics.models.Project.is_valid_tracking_id')
@patch('analytics.models.PageView.create_from_request')
def test_collect_does_not_call_create_from_request_when_url_not_given(
    mock_create_from_request, mock_is_valid_tracking_id
):
    mock_is_valid_tracking_id.return_value = True
    request = RequestFactory().get('/a.gif', {'tid': 'PA-TESTTRACK'})
    collect(request)

    assert mock_create_from_request.call_count == 0


@patch('analytics.models.Project.is_valid_tracking_id')
@patch('analytics.models.PageView.create_from_request')
def test_collect_does_not_call_create_from_request_when_tid_not_given(
    mock_create_from_request, mock_is_valid_tracking_id
):
    mock_is_valid_tracking_id.return_value = False
    request = RequestFactory().get('/a.gif', {'url': 'http://example.com'})
    collect(request)

    assert mock_create_from_request.call_count == 0


@patch('analytics.models.Project.is_valid_tracking_id')
@patch('analytics.models.PageView.create_from_request')
def test_collect_returns_correct_response_with_valid_request(
    mock_create_from_request, mock_is_valid_tracking_id
):
    mock_is_valid_tracking_id.return_value = True
    request = RequestFactory().get('/a.gif',
                                   {'url': 'http://example.com',
                                    'tid': 'PA-TESTTRACK'},
                                   HTTP_DNT='0')
    response = collect(request)

    assert response.status_code == 200
    assert response['content-type'] == 'image/gif'
    assert PXL in response.content
    assert response['cache-control'] == 'private, no-cache'


@patch('analytics.models.Project.is_valid_tracking_id')
@patch('analytics.models.PageView.create_from_request')
def test_collect_returns_correct_response_with_dnt_enabled(
    mock_create_from_request, mock_is_valid_tracking_id
):
    mock_is_valid_tracking_id.return_value = True
    request = RequestFactory().get('/a.gif',
                                   {'url': 'http://example.com',
                                    'tid': 'PA-TESTTRACK'},
                                   HTTP_DNT='1')
    response = collect(request)

    assert response.status_code == 200
    assert response['content-type'] == 'image/gif'
    assert PXL in response.content
    assert response['cache-control'] == 'private, no-cache'


@patch('analytics.models.Project.is_valid_tracking_id')
@patch('analytics.models.PageView.create_from_request')
def test_collect_returns_correct_response_with_missing_url(
    mock_create_from_request, mock_is_valid_tracking_id
):
    mock_is_valid_tracking_id.return_value = True
    request = RequestFactory().get('/a.gif', {'tid': 'PA-TESTTRACK'})
    response = collect(request)

    assert response.status_code == 200
    assert response['content-type'] == 'image/gif'
    assert PXL in response.content
    assert response['cache-control'] == 'private, no-cache'


@patch('analytics.models.Project.is_valid_tracking_id')
@patch('analytics.models.PageView.create_from_request')
def test_collect_returns_correct_response_with_invalid_tid(
    mock_create_from_request, mock_is_valid_tracking_id
):
    mock_is_valid_tracking_id.return_value = False
    request = RequestFactory().get('/a.gif', {'url': 'http://example.com'})
    response = collect(request)

    assert response.status_code == 200
    assert response['content-type'] == 'image/gif'
    assert PXL in response.content
    assert response['cache-control'] == 'private, no-cache'
