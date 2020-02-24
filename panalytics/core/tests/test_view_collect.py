from django.test import RequestFactory
from unittest.mock import patch

from ..views import collect, PXL


@patch('panalytics.core.models.Project.is_valid_tracking_id')
@patch('panalytics.core.models.PageView.create_from_request')
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


@patch('panalytics.core.models.Project.is_valid_tracking_id')
@patch('panalytics.core.models.PageView.create_from_request')
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


@patch('panalytics.core.models.Project.is_valid_tracking_id')
@patch('panalytics.core.models.PageView.create_from_request')
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


@patch('panalytics.core.models.Project.is_valid_tracking_id')
@patch('panalytics.core.models.PageView.create_from_request')
def test_collect_does_not_call_create_from_request_when_url_not_given(
    mock_create_from_request, mock_is_valid_tracking_id
):
    mock_is_valid_tracking_id.return_value = True
    request = RequestFactory().get('/a.gif', {'tid': 'PA-TESTTRACK'})
    collect(request)

    assert mock_create_from_request.call_count == 0


@patch('panalytics.core.models.Project.is_valid_tracking_id')
@patch('panalytics.core.models.PageView.create_from_request')
def test_collect_does_not_call_create_from_request_when_tid_not_given(
    mock_create_from_request, mock_is_valid_tracking_id
):
    mock_is_valid_tracking_id.return_value = False
    request = RequestFactory().get('/a.gif', {'url': 'http://example.com'})
    collect(request)

    assert mock_create_from_request.call_count == 0


@patch('panalytics.core.models.Project.is_valid_tracking_id')
@patch('panalytics.core.models.PageView.create_from_request')
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


@patch('panalytics.core.models.Project.is_valid_tracking_id')
@patch('panalytics.core.models.PageView.create_from_request')
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


@patch('panalytics.core.models.Project.is_valid_tracking_id')
@patch('panalytics.core.models.PageView.create_from_request')
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


@patch('panalytics.core.models.Project.is_valid_tracking_id')
@patch('panalytics.core.models.PageView.create_from_request')
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
