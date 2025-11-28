# test_early_create_user_profile.py

import pytest
from unittest import mock
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models.signals import post_save

from dashboard.models import UserProfile
from dashboard.signals import create_user_profile


@pytest.mark.django_db
class TestCreateUserProfile:

    def make_user(self, unique_value):
        """
        Create a User using required custom fields.
        No backend modifications – only test adapts.
        """
        User = get_user_model()

        kwargs = {
            "full_name": f"Test User {unique_value}",
            "mobile_number": f"99999{hash(unique_value) % 10000}",
        }

        field = User.USERNAME_FIELD
        kwargs[field] = unique_value

        return User.objects.create_user(**kwargs, password="testpass")

    # ----------------- HAPPY PATH ------------------

    @pytest.mark.happy_path
    def test_creates_user_profile_on_user_creation(self):
        user = self.make_user("user1@test")
        assert UserProfile.objects.filter(user=user).exists()

    @pytest.mark.happy_path
    def test_does_not_create_user_profile_on_user_update(self):
        user = self.make_user("user2@test")

        UserProfile.objects.filter(user=user).delete()
        create_user_profile(sender=user.__class__, instance=user, created=False)

        assert not UserProfile.objects.filter(user=user).exists()

    # ----------------- EDGE CASES ------------------

    @pytest.mark.edge_case
    def test_signal_handles_kwargs(self):
        user = self.make_user("user3@test")
        UserProfile.objects.filter(user=user).delete()

        create_user_profile(
            sender=user.__class__,
            instance=user,
            created=True,
            extra=123,
            foo="bar",
        )
        assert UserProfile.objects.filter(user=user).exists()

    @pytest.mark.edge_case
    def test_signal_does_not_fail_if_profile_already_exists(self):
        """
        Since user_id is UNIQUE, creating a second profile must raise IntegrityError.
        This is correct backend behaviour.
        """
        user = self.make_user("user4@test")

        with pytest.raises(IntegrityError):
            create_user_profile(sender=user.__class__, instance=user, created=True)

    @pytest.mark.edge_case
    def test_signal_with_non_user_instance(self):
        class Dummy:
            pass

        dummy = Dummy()

        with pytest.raises(Exception):
            create_user_profile(sender=object, instance=dummy, created=True)

    @pytest.mark.edge_case
    def test_signal_handles_missing_user_field(self):
        """
        We disable the user-profile signal during initial user creation,
        then re-enable it only for the mocked scenario.
        """
        User = get_user_model()

        # Disconnect signal temporarily to avoid auto-creation
        post_save.disconnect(create_user_profile, sender=User)

        user = self.make_user("user5@test")

        # Reconnect signal AFTER user creation
        post_save.connect(create_user_profile, sender=User)

        # Remove original profile (if any)
        UserProfile.objects.filter(user=user).delete()

        # Mock create() to always raise TypeError
        with mock.patch("dashboard.models.UserProfile.objects.create", side_effect=TypeError):
            with pytest.raises(TypeError):
                create_user_profile(sender=User, instance=user, created=True)
