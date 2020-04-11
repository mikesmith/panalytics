import pytest

from ..models import Project

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
