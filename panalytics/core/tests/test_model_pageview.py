import pytest
from django.test import RequestFactory
from unittest.mock import patch

from ..models import PageView


@pytest.fixture
def get_request_url():
    query = {'url': 'http://example.com'}
    return RequestFactory().get('/a.gif', query)


@pytest.fixture
def get_request_url_referer():
    query = {'url': 'http://example.com', 'ref': 'http://refer.com'}
    return RequestFactory().get('/a.gif', query)


@pytest.fixture
def get_request_url_title():
    query = {'url': 'http://example.com/about',
             't': 'Test Title'}
    return RequestFactory().get('/a.gif', query)


@pytest.fixture
def get_request_url_title_dimensions():
    query = {'url': 'http://example.com/about',
             't': 'Test Title',
             'wiw': '1272',
             'wih': '675'}
    return RequestFactory().get('/a.gif', query)


@patch('panalytics.core.models.get_object_or_404')
@patch('panalytics.core.models.PageView.objects.create')
def test_create_from_request_passes_url_to_obj_create(
    mock_pageview_objects_create, mock_project_objects_get, get_request_url
):
    PageView.create_from_request(get_request_url)
    args, kwargs = mock_pageview_objects_create.call_args
    assert mock_pageview_objects_create.call_count == 1
    assert kwargs['protocol'] == 'http'
    assert kwargs['domain'] == 'example.com'
    assert kwargs['path'] == ''
    assert kwargs['url'] == 'http://example.com'


@patch('panalytics.core.models.get_object_or_404')
@patch('panalytics.core.models.PageView.objects.create')
def test_create_from_request_passes_default_referer_to_obj_create(
    mock_pageview_objects_create, mock_project_objects_get, get_request_url
):
    PageView.create_from_request(get_request_url)
    args, kwargs = mock_pageview_objects_create.call_args
    assert mock_pageview_objects_create.call_count == 1
    assert kwargs['referer'] == ''


@patch('panalytics.core.models.get_object_or_404')
@patch('panalytics.core.models.PageView.objects.create')
def test_create_from_request_passes_referer_to_obj_create(
    mock_pageview_objects_create,
    mock_project_objects_get,
    get_request_url_referer
):
    PageView.create_from_request(get_request_url_referer)
    args, kwargs = mock_pageview_objects_create.call_args
    assert mock_pageview_objects_create.call_count == 1
    assert kwargs['referer'] == 'http://refer.com'


@patch('panalytics.core.models.get_object_or_404')
@patch('panalytics.core.models.PageView.objects.create')
def test_create_from_request_passes_source_as_referer_to_obj_create(
    mock_pageview_objects_create, mock_project_objects_get
):
    query = {'url': 'http://example.com/?ref=email'}
    request = RequestFactory().get('/a.gif', query)
    PageView.create_from_request(request)
    args, kwargs = mock_pageview_objects_create.call_args
    assert mock_pageview_objects_create.call_count == 1
    assert kwargs['referer'] == 'email'


@patch('panalytics.core.models.get_object_or_404')
@patch('panalytics.core.models.PageView.objects.create')
def test_create_from_request_passes_referer_instead_or_source_to_obj_create(
    mock_pageview_objects_create, mock_project_objects_get
):
    query = {'url': 'http://example.com/?ref=email', 'ref': 'http://refer.com'}
    request = RequestFactory().get('/a.gif', query)
    PageView.create_from_request(request)
    args, kwargs = mock_pageview_objects_create.call_args
    assert mock_pageview_objects_create.call_count == 1
    assert kwargs['referer'] == 'http://refer.com'


@patch('panalytics.core.models.get_object_or_404')
@patch('panalytics.core.models.PageView.objects.create')
def test_create_from_request_passes_url_with_path_to_obj_create(
    mock_pageview_objects_create,
    mock_project_objects_get,
    get_request_url_title
):
    PageView.create_from_request(get_request_url_title)
    args, kwargs = mock_pageview_objects_create.call_args
    assert mock_pageview_objects_create.call_count == 1
    assert kwargs['protocol'] == 'http'
    assert kwargs['domain'] == 'example.com'
    assert kwargs['path'] == '/about'
    assert kwargs['url'] == 'http://example.com/about'


@patch('panalytics.core.models.get_object_or_404')
@patch('panalytics.core.models.PageView.objects.create')
def test_create_from_request_passes_correct_title_to_obj_create(
    mock_pageview_objects_create,
    mock_project_objects_get,
    get_request_url_title
):
    PageView.create_from_request(get_request_url_title)
    args, kwargs = mock_pageview_objects_create.call_args
    assert mock_pageview_objects_create.call_count == 1
    assert kwargs['title'] == 'Test Title'


@patch('panalytics.core.models.get_object_or_404')
@patch('panalytics.core.models.PageView.objects.create')
def test_create_from_request_passes_default_title_to_obj_create(
    mock_pageview_objects_create, mock_project_objects_get, get_request_url
):
    PageView.create_from_request(get_request_url)
    args, kwargs = mock_pageview_objects_create.call_args
    assert mock_pageview_objects_create.call_count == 1
    assert kwargs['title'] == ''


@patch('panalytics.core.models.get_object_or_404')
@patch('panalytics.core.models.PageView.objects.create')
def test_create_from_request_passes_correct_window_dimensions_to_obj_create(
    mock_pageview_objects_create,
    mock_project_objects_get,
    get_request_url_title_dimensions
):
    PageView.create_from_request(get_request_url_title_dimensions)
    args, kwargs = mock_pageview_objects_create.call_args
    assert mock_pageview_objects_create.call_count == 1
    assert kwargs['window_width'] == '1272'
    assert kwargs['window_height'] == '675'


@patch('panalytics.core.models.get_object_or_404')
@patch('panalytics.core.models.PageView.objects.create')
def test_create_from_request_passes_default_window_dimensions_when_empty(
    mock_pageview_objects_create,
    mock_project_objects_get,
    get_request_url_title
):
    PageView.create_from_request(get_request_url_title)
    args, kwargs = mock_pageview_objects_create.call_args
    assert mock_pageview_objects_create.call_count == 1
    assert kwargs['window_width'] == '0'
    assert kwargs['window_height'] == '0'


@patch('panalytics.core.models.get_object_or_404')
@patch('panalytics.core.models.PageView.objects.create')
def test_create_from_request_passes_unique_visit_to_obj_create(
    mock_pageview_objects_create,
    mock_project_objects_get,
    get_request_url_referer
):
    PageView.create_from_request(get_request_url_referer)
    args, kwargs = mock_pageview_objects_create.call_args
    assert mock_pageview_objects_create.call_count == 1
    assert kwargs['unique_visit']


@patch('panalytics.core.models.get_object_or_404')
@patch('panalytics.core.models.PageView.objects.create')
def test_create_from_request_not_unique_visit_if_url_referer_domain_the_same(
    mock_pageview_objects_create, mock_project_objects_get
):
    query = {'url': 'http://example.com/about', 'ref': 'http://example.com'}
    request = RequestFactory().get('/a.gif', query)
    PageView.create_from_request(request)
    args, kwargs = mock_pageview_objects_create.call_args
    assert mock_pageview_objects_create.call_count == 1
    assert not kwargs['unique_visit']
