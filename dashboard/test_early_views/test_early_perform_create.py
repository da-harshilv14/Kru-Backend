# test_views.py

import pytest
from unittest.mock import MagicMock, patch
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from dashboard.views import UserProfileView

User = get_user_model()

@pytest.fixture
def mock_user():
    """Fixture to provide a mock user instance."""
    user = MagicMock(spec=User)
    user.is_authenticated = True
    user.pk = 1
    return user

@pytest.fixture
def mock_request(mock_user):
    """Fixture to provide a mock request with a user."""
    factory = APIRequestFactory()
    request = factory.post('/fake-url/')
    request.user = mock_user
    return request

@pytest.fixture
def mock_serializer():
    """Fixture to provide a mock serializer."""
    serializer = MagicMock()
    return serializer

class TestUserProfileViewPerformCreate:
    """Unit tests for UserProfileView.perform_create method."""

    @pytest.mark.happy_path
    def test_perform_create_saves_with_user(self, mock_request, mock_serializer):
        """
        Test that perform_create calls serializer.save with the correct user.
        """
        view = UserProfileView()
        view.request = mock_request

        view.perform_create(mock_serializer)

        mock_serializer.save.assert_called_once_with(user=mock_request.user)

    @pytest.mark.happy_path
    def test_perform_create_with_different_user(self, mock_serializer):
        """
        Test perform_create with a different user instance.
        """
        user = MagicMock(spec=User)
        user.pk = 42
        user.is_authenticated = True

        factory = APIRequestFactory()
        request = factory.post('/fake-url/')
        request.user = user

        view = UserProfileView()
        view.request = request

        view.perform_create(mock_serializer)

        mock_serializer.save.assert_called_once_with(user=user)

    @pytest.mark.edge_case
    def test_perform_create_with_anonymous_user(self, mock_serializer):
        """
        Test perform_create when request.user is AnonymousUser (should still pass user to save).
        """
        from django.contrib.auth.models import AnonymousUser

        factory = APIRequestFactory()
        request = factory.post('/fake-url/')
        request.user = AnonymousUser()

        view = UserProfileView()
        view.request = request

        view.perform_create(mock_serializer)

        mock_serializer.save.assert_called_once_with(user=request.user)

    @pytest.mark.edge_case
    def test_perform_create_with_none_user(self, mock_serializer):
        """
        Test perform_create when request.user is None (should pass None to save).
        """
        factory = APIRequestFactory()
        request = factory.post('/fake-url/')
        request.user = None

        view = UserProfileView()
        view.request = request

        view.perform_create(mock_serializer)

        mock_serializer.save.assert_called_once_with(user=None)

    @pytest.mark.edge_case
    def test_perform_create_serializer_save_raises_exception(self, mock_request, mock_serializer):
        """
        Test perform_create when serializer.save raises an exception.
        """
        mock_serializer.save.side_effect = ValueError("Save failed")

        view = UserProfileView()
        view.request = mock_request

        with pytest.raises(ValueError, match="Save failed"):
            view.perform_create(mock_serializer)

    @pytest.mark.edge_case
    def test_perform_create_without_request_attribute(self, mock_serializer):
        """
        Test perform_create when view.request is not set (should raise AttributeError).
        """
        view = UserProfileView()
        # view.request is not set

        with pytest.raises(AttributeError):
            view.perform_create(mock_serializer)