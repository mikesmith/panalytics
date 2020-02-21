from django.test import RequestFactory

from ..utils import do_not_track


def test_do_not_track_as_enabled():
    request = RequestFactory().get('/a.gif', HTTP_DNT='1')
    assert do_not_track(request)


def test_do_not_track_as_disabled():
    request = RequestFactory().get('/a.gif', HTTP_DNT='0')
    assert not do_not_track(request)


def test_do_not_track_as_not_specified():
    request = RequestFactory().get('/a.gif')
    assert not do_not_track(request)
