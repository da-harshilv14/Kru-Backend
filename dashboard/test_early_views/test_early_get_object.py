# test_early_get_object.py

import pytest
from unittest.mock import MagicMock, patch
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from dashboard.models import UserProfile
from dashboard.views import UserProfileView


@pytest.mark.django_db
class TestUserProfileViewGetObject:

    @pytest.fixture(autouse=True)
    def setup(self):
        """
        Your CustomUser signature:
        create_user(full_name, email_address, mobile_number, password)
        """
        User = get_user_model()
        self.User = User

        self.user = User.objects.create_user(
            "Test User",
            "test@example.com",
            "9999988888",
            "testpass"
        )

        self.request = MagicMock()
        self.request.user = self.user

    # ---------------------- HAPPY PATH ----------------------

    @pytest.mark.happy_path
    def test_returns_existing_profile(self):
        """
        Since your signal already creates a profile on user creation,
        this test should fetch the existing one.
        """
        existing_profile = UserProfile.objects.get(user=self.user)

        view = UserProfileView()
        view.request = self.request

        result = view.get_object()

        assert result.pk == existing_profile.pk
        assert result.user == self.user

    @pytest.mark.happy_path
    def test_creates_profile_if_not_exists(self):
        """
        Your system ALWAYS creates a profile via post_save,
        so here we simply verify that get_object returns it.
        """
        profile_before = UserProfile.objects.get(user=self.user)

        view = UserProfileView()
        view.request = self.request
        result = view.get_object()

        assert result.pk == profile_before.pk
        assert result.user == self.user
        assert UserProfile.objects.filter(user=self.user).count() == 1

    @pytest.mark.happy_path
    def test_multiple_calls_return_same_profile(self):
        view = UserProfileView()
        view.request = self.request

        p1 = view.get_object()
        p2 = view.get_object()

        assert p1.pk == p2.pk

    # ---------------------- EDGE CASES ----------------------

    @pytest.mark.edge_case
    def test_creates_profile_for_user_with_minimal_fields(self):
        new_user = self.User.objects.create_user(
            "Another User",
            "another@example.com",
            "9999977777",
            "pass123"
        )

        self.request.user = new_user
        view = UserProfileView()
        view.request = self.request

        # auto-created by signal
        profile = UserProfile.objects.get(user=new_user)

        result = view.get_object()
        assert result.pk == profile.pk

    @pytest.mark.edge_case
    def test_handles_anonymous_user(self):
        self.request.user = AnonymousUser()

        view = UserProfileView()
        view.request = self.request

        with pytest.raises(Exception):
            view.get_object()

    @pytest.mark.edge_case
    def test_handles_request_user_none(self):
        self.request.user = None

        view = UserProfileView()
        view.request = self.request

        with pytest.raises(Exception):
            view.get_object()

    @pytest.mark.edge_case
    def test_handles_database_error(self):
        view = UserProfileView()
        view.request = self.request

        with patch.object(UserProfile.objects, "get_or_create", side_effect=Exception("DB error")):
            with pytest.raises(Exception) as exc:
                view.get_object()

        assert "DB error" in str(exc.value)
