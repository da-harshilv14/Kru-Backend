"""
Unit tests for the `get` method of `UserPhotoView` in dashboard/views.py.
"""

import pytest
from unittest.mock import MagicMock, patch
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory

from dashboard.views import UserPhotoView


# ----------------- FIXTURES -----------------

@pytest.fixture
def api_rf():
    return APIRequestFactory()


@pytest.fixture
def user_mock():
    """Mock user WITH cloud_profile (default)."""
    user = MagicMock()
    return user


@pytest.fixture
def user_no_profile():
    """Mock user WITHOUT cloud_profile."""
    user = MagicMock()
    user.cloud_profile = None
    return user


@pytest.fixture
def view_instance():
    return UserPhotoView()


# ----------------- TEST CLASS -----------------

@pytest.mark.usefixtures("api_rf", "user_mock", "view_instance")
class TestUserPhotoViewGet:

    # ---------------- HAPPY PATH ----------------

    @pytest.mark.happy_path
    def test_returns_serialized_photo_data(self, api_rf, user_mock, view_instance):
        """User has cloud_profile → serializer returns expected data"""
        profile_mock = MagicMock()
        user_mock.cloud_profile = profile_mock

        expected_data = {"photo_url": "http://example.com/photo.jpg"}

        with patch("dashboard.views.UserPhotoSerializer") as serializer_cls:
            serializer_cls.return_value.data = expected_data

            request = api_rf.get("/fake-url/")
            request.user = user_mock

            response = view_instance.get(request)

        assert isinstance(response, Response)
        assert response.data == expected_data

    @pytest.mark.happy_path
    def test_returns_other_photo_url(self, api_rf, user_mock, view_instance):
        """Different photo url"""
        profile_mock = MagicMock()
        user_mock.cloud_profile = profile_mock

        expected_data = {"photo_url": "https://cdn.site.com/another_photo.png"}

        with patch("dashboard.views.UserPhotoSerializer") as serializer_cls:
            serializer_cls.return_value.data = expected_data

            request = api_rf.get("/fake-url/")
            request.user = user_mock

            response = view_instance.get(request)

        assert response.data == expected_data

    # ---------------- EDGE CASES ----------------

    @pytest.mark.edge_case
    def test_returns_empty_dict_if_cloud_profile_missing(self, api_rf, view_instance, user_no_profile):
        """User has NO cloud_profile → backend returns {}"""
        request = api_rf.get("/fake-url/")
        request.user = user_no_profile

        response = view_instance.get(request)

        assert response.status_code == 200
        assert response.data == {}     # matches backend

    @pytest.mark.edge_case
    def test_returns_none_when_serializer_raises_exception(self, api_rf, user_mock, view_instance):
        """Serializer crashes → {"photo_url": None}"""
        user_mock.cloud_profile = MagicMock()

        with patch("dashboard.views.UserPhotoSerializer", side_effect=Exception("err")):
            request = api_rf.get("/fake-url/")
            request.user = user_mock

            response = view_instance.get(request)

        assert response.data == {"photo_url": None}

    @pytest.mark.edge_case
    def test_returns_none_when_user_is_none(self, api_rf, view_instance):
        """request.user = None → {"photo_url": None}"""
        request = api_rf.get("/fake-url/")
        request.user = None

        response = view_instance.get(request)

        assert response.data == {"photo_url": None}
