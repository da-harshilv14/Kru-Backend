import pytest
from django.contrib.auth import get_user_model
from dashboard.models import UserProfile


@pytest.mark.django_db
class TestUserProfileStr:

    def make_user(self, full_name):
        User = get_user_model()

        email_address = f"{abs(hash(full_name)) % 100000}@test.com"
        mobile_number = "99999" + str(abs(hash(full_name)) % 10000)

        return User.objects.create_user(
            full_name,
            email_address,
            mobile_number,
            "testpass"
        )

    # ---------------- HAPPY PATH --------------------

    @pytest.mark.happy_path
    def test_str_returns_full_name_profile(self):
        user = self.make_user("Test User")
        profile = UserProfile.objects.get(user=user)
        assert str(profile) == "Test User's Profile"

    @pytest.mark.happy_path
    def test_str_with_special_characters(self):
        name = "Élise O'Connor-王"
        user = self.make_user(name)
        profile = UserProfile.objects.get(user=user)
        assert str(profile) == f"{name}'s Profile"

    @pytest.mark.happy_path
    def test_str_with_spaces(self):
        name = "  John   Doe  "
        user = self.make_user(name)
        profile = UserProfile.objects.get(user=user)
        assert str(profile) == f"{name}'s Profile"

    # ---------------- EDGE CASES ---------------------

    @pytest.mark.edge_case
    def test_str_with_empty_full_name(self):
        """Use unsaved profile so DB does not override."""
        user = self.make_user("TEMP")
        user.full_name = ""   # override in memory
        profile = UserProfile(user=user)  # unsaved instance
        assert str(profile) == "'s Profile"

    @pytest.mark.edge_case
    def test_str_with_none_full_name(self):
        """Avoid NOT NULL DB constraint by using unsaved profile."""
        user = self.make_user("TEMP")
        user.full_name = None
        profile = UserProfile(user=user)
        assert str(profile) == "None's Profile"

    @pytest.mark.edge_case
    def test_str_missing_full_name_attribute(self):
        """
        Ensure __str__ raises AttributeError when user has no full_name.
        Use pure Python mock objects to bypass OneToOne validation.
        """
        class DummyUser:
            pass

        class DummyProfile:
            def __init__(self, user):
                self.user = user

            def __str__(self):
                return UserProfile.__str__(self)

        dummy_user = DummyUser()
        profile = DummyProfile(dummy_user)

        with pytest.raises(AttributeError):
            str(profile)

    @pytest.mark.edge_case
    def test_str_full_name_not_string(self):
        user = self.make_user("TEMP")
        user.full_name = 12345  # do NOT save to DB
        profile = UserProfile(user=user)
        assert str(profile) == "12345's Profile"

    @pytest.mark.edge_case
    def test_str_full_name_callable(self):
        user = self.make_user("TEMP")
        user.full_name = lambda: "Callable Name"
        profile = UserProfile(user=user)

        result = str(profile)
        assert result.startswith("<function") and result.endswith("'s Profile")
