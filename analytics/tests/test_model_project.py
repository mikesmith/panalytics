from unittest.mock import patch

from ..models import Project


@patch('django.db.models.Model.save')
@patch('analytics.models.get_tracking_id')
def test_project_save_skips_new_tid_if_given(
    mock_get_tracking_id, mock_model_save
):
    project = Project(name='test', tid='testtid')
    project.save()

    assert mock_get_tracking_id.call_count == 0
    assert mock_model_save.call_count == 1


@patch('django.db.models.Model.save')
@patch('analytics.models.Project.objects')
@patch('analytics.models.get_tracking_id')
def test_project_save_gets_tid_if_not_given(
    mock_get_tracking_id, mock_objects, mock_model_save
):
    mock_get_tracking_id.return_value = 'newtrackid'
    mock_objects.filter.return_value.exists.return_value = False

    project = Project(name='test')
    project.save()

    assert mock_get_tracking_id.call_count == 1
    assert mock_model_save.call_count == 1
    assert project.tid == 'newtrackid'


@patch('django.db.models.Model.save')
@patch('analytics.models.Project.objects')
@patch('analytics.models.get_tracking_id')
def test_project_save_get_new_tid_if_duplicate_exists(
    mock_get_tracking_id, mock_objects, mock_model_save
):
    mock_get_tracking_id.side_effect = ['newtrackid', 'newertrackid']
    mock_objects.filter.return_value.exists.side_effect = [True, False]

    project = Project(name='test')
    project.save()

    assert mock_get_tracking_id.call_count == 2
    assert mock_model_save.call_count == 1
    assert project.tid == 'newertrackid'
