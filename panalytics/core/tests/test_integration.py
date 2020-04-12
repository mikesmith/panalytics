import pytest

from ..models import Project
from ..views import PXL

JAVASCRIPT = """(function(){var w=window,d=document,
    i=new Image,e=encodeURIComponent;i.src='%s/a.gif?tid=%s&url='
    +e(d.location.href)+'&ref='+e(d.referrer)+'&t='+e(d.title)+'&wiw='
    +e(w.innerWidth)+'&wih='+e(w.innerHeight);})()"""
CLEAN_JAVASCRIPT = JAVASCRIPT.replace('\n', '').replace('    ', '')


def test_script_view_no_tracking_id_404_response(client):
    response = client.get('/a.js')

    assert response.status_code == 404


@pytest.mark.django_db
def test_script_view_invalid_tracking_id_404_response(client):
    Project.objects.create(name='Test Project')

    response = client.get('/a.js?tid=TESTING')

    assert response.status_code == 404


@pytest.mark.django_db
def test_script_view_valid_tracking_id_javascript_in_200_response(client):
    project = Project.objects.create(name='Test Project')
    clean_js = f'{CLEAN_JAVASCRIPT}' % ('http://127.0.0.1:8000', project.tid)

    response = client.get(f'/a.js?tid={project.tid}')

    assert response.status_code == 200
    assert clean_js in str(response.content)


@pytest.mark.django_db
def test_collect_view_returns_gif_response(client):
    project = Project.objects.create(name='Test Project')
    query = {'tid': project.tid,
             'url': 'http://example.com/about',
             't': 'Test Title',
             'wiw': '1272',
             'wih': '675'}

    response = client.get('/a.gif', query)

    assert response.status_code == 200
    assert response['content-type'] == 'image/gif'
    assert PXL in response.content


@pytest.mark.django_db
def test_collect_view_returns_gif_response_even_when_invalid(client):
    Project.objects.create(name='Test Project')
    query = {'tid': 'INVALID',
             'url': 'http://example.com/about',
             't': 'Test Title',
             'wiw': '1272',
             'wih': '675'}

    response = client.get('/a.gif', query)

    assert response.status_code == 200
    assert response['content-type'] == 'image/gif'
    assert PXL in response.content


@pytest.mark.django_db
def test_collect_view_persists_page_view(client):
    project = Project.objects.create(name='Test Project')
    query = {'tid': project.tid,
             'url': 'http://example.com/about',
             't': 'Test Title',
             'wiw': '1272',
             'wih': '675'}

    response = client.get('/a.gif', query)

    assert project.pageviews.count() == 1
    assert response.status_code == 200


@pytest.mark.django_db
def test_collect_view_persists_page_view_with_valid_data(client):
    project = Project.objects.create(name='Test Project')
    query = {'tid': project.tid,
             'url': 'http://example.com/about',
             't': 'Test Title',
             'wiw': '1272',
             'wih': '675'}

    client.get('/a.gif', query)

    pageview = project.pageviews.first()
    assert pageview.url == query['url']
    assert pageview.title == query['t']
    assert pageview.window_width == int(query['wiw'])
    assert pageview.window_height == int(query['wih'])


@pytest.mark.django_db
def test_collect_view_invalid_tid(client):
    project = Project.objects.create(name='Test Project')
    query = {'tid': 'INVALIDTID',
             'url': 'http://example.com/about',
             't': 'Test Title',
             'wiw': '1272',
             'wih': '675'}

    response = client.get('/a.gif', query)

    assert project.pageviews.count() == 0
    assert response.status_code == 200


@pytest.mark.django_db
def test_collect_view_no_url(client):
    project = Project.objects.create(name='Test Project')
    query = {'tid': project.tid,
             't': 'Test Title',
             'wiw': '1272',
             'wih': '675'}

    response = client.get('/a.gif', query)

    assert project.pageviews.count() == 0
    assert response.status_code == 200
