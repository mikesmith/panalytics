from django.test import RequestFactory
import re

from ..utils import do_not_track, get_tracking_id


def test_do_not_track_as_enabled():
    request = RequestFactory().get('/a.gif', HTTP_DNT='1')
    assert do_not_track(request)


def test_do_not_track_as_disabled():
    request = RequestFactory().get('/a.gif', HTTP_DNT='0')
    assert not do_not_track(request)


def test_do_not_track_as_not_specified():
    request = RequestFactory().get('/a.gif')
    assert not do_not_track(request)


def test_get_tracking_id_include_nine_random_character_string():
    result = get_tracking_id()
    assert re.match(r'PA-[A-Z0-9]{9}$', result)


def test_get_tracking_id_returns_twelve_character_string():
    result = get_tracking_id()
    assert len(result) == 12
