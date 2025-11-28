"""
Test suite for UserProfileView.perform_update in dashboard/views.py

Covers:
- Happy paths: normal update scenarios
- Edge cases: unusual or boundary conditions

Assumptions:
- UserProfileSerializer is a DRF serializer with a .save() method accepting user kwarg.
- self.request.user is always set (due to IsAuthenticated).
- serializer.save may raise exceptions.
- The tests are located as a sibling file to dashboard/views.py.
"""

import pytest
from unittest.mock import MagicMock, patch
from dashboard.views import UserProfileView

@pytest.fixture
def mock_request():
    """Fixture to provide a mock request with a user attribute."""
    mock = MagicMock()
    mock.user = MagicMock()
    return mock

@pytest.fixture
def view_instance(mock_request):
    """Fixture to provide a UserProfileView instance with a mock request."""
    view = UserProfileView()
    view.request = mock_request
    return view

@pytest.mark.happy_path
class TestUserProfileViewPerformUpdate:
    # Happy Path Tests

    def test_perform_update_saves_with_user(self, view_instance):
        """
        Test that perform_update calls serializer.save with the correct user.
        """
        serializer = MagicMock()
        view_instance.perform_update(serializer)
        serializer.save.assert_called_once_with(user=view_instance.request.user)

    def test_perform_update_with_different_user_object(self, view_instance):
        """
        Test perform_update with a different user object to ensure correct user is passed.
        """
        another_user = MagicMock()
        view_instance.request.user = another_user
        serializer = MagicMock()
        view_instance.perform_update(serializer)
        serializer.save.assert_called_once_with(user=another_user)

    def test_perform_update_with_serializer_having_other_kwargs(self, view_instance):
        """
        Test perform_update when serializer.save accepts additional kwargs.
        """
        serializer = MagicMock()
        # Simulate serializer.save accepting extra kwargs
        def save_side_effect(**kwargs):
            assert 'user' in kwargs
            return 'saved'
        serializer.save.side_effect = save_side_effect
        result = view_instance.perform_update(serializer)
        serializer.save.assert_called_once_with(user=view_instance.request.user)
        assert result is None  # perform_update does not return anything

@pytest.mark.edge_case
class TestUserProfileViewPerformUpdateEdgeCases:
    # Edge Case Tests

    def test_perform_update_with_none_user(self, view_instance):
        """
        Test perform_update when request.user is None.
        """
        view_instance.request.user = None
        serializer = MagicMock()
        view_instance.perform_update(serializer)
        serializer.save.assert_called_once_with(user=None)

    def test_perform_update_serializer_raises_exception(self, view_instance):
        """
        Test perform_update when serializer.save raises an exception.
        """
        serializer = MagicMock()
        serializer.save.side_effect = ValueError("Save failed")
        with pytest.raises(ValueError, match="Save failed"):
            view_instance.perform_update(serializer)

    def test_perform_update_with_nonstandard_user_object(self, view_instance):
        """
        Test perform_update when request.user is a non-standard object (e.g., a string).
        """
        view_instance.request.user = "not_a_user_object"
        serializer = MagicMock()
        view_instance.perform_update(serializer)
        serializer.save.assert_called_once_with(user="not_a_user_object")

    def test_perform_update_with_missing_user_attribute(self, view_instance):
        """
        Test perform_update when request has no user attribute.
        """
        delattr(view_instance.request, 'user')
        serializer = MagicMock()
        # Should raise AttributeError
        with pytest.raises(AttributeError):
            view_instance.perform_update(serializer)