"""
Unit tests for the `get_aadhaar_card_url` method in `UserProfileSerializer` (dashboard/serializers.py).

Covers:
- Happy paths: normal and expected object configurations.
- Edge cases: missing fields, None values, and unusual object states.

Test class: TestUserProfileSerializerGetAadhaarCardUrl
"""

import pytest
from unittest.mock import Mock
from dashboard.serializers import UserProfileSerializer

@pytest.mark.usefixtures("mock_user_profile")
class TestUserProfileSerializerGetAadhaarCardUrl:
    @pytest.fixture
    def serializer(self):
        """Fixture to instantiate the serializer."""
        return UserProfileSerializer()

    @pytest.fixture
    def mock_user_profile(self):
        """Fixture to create a mock UserProfile object."""
        return Mock()

    # -------------------- Happy Path Tests --------------------

    @pytest.mark.happy_path
    def test_returns_url_when_aadhaar_card_present(self, serializer, mock_user_profile):
        """
        Test that the method returns the correct URL when `aadhaar_card` is present and has a `url` attribute.
        """
        mock_aadhaar_card = Mock()
        mock_aadhaar_card.url = "https://cloudinary.com/aadhaar_card.jpg"
        mock_user_profile.aadhaar_card = mock_aadhaar_card

        result = serializer.get_aadhaar_card_url(mock_user_profile)
        assert result == "https://cloudinary.com/aadhaar_card.jpg"

    @pytest.mark.happy_path
    def test_returns_url_when_aadhaar_card_url_is_empty_string(self, serializer, mock_user_profile):
        """
        Test that the method returns an empty string if `aadhaar_card.url` is an empty string (still present).
        """
        mock_aadhaar_card = Mock()
        mock_aadhaar_card.url = ""
        mock_user_profile.aadhaar_card = mock_aadhaar_card

        result = serializer.get_aadhaar_card_url(mock_user_profile)
        assert result == ""

    # -------------------- Edge Case Tests --------------------

    @pytest.mark.edge_case
    def test_returns_none_when_aadhaar_card_is_none(self, serializer, mock_user_profile):
        """
        Test that the method returns None when `aadhaar_card` is None.
        """
        mock_user_profile.aadhaar_card = None

        result = serializer.get_aadhaar_card_url(mock_user_profile)
        assert result is None

    @pytest.mark.edge_case
    def test_returns_none_when_aadhaar_card_attribute_missing(self, serializer):
        """
        Since the real serializer directly accesses `obj.aadhaar_card`,
        a missing attribute will raise AttributeError.
        """
        class DummyObj:
            pass

        dummy = DummyObj()

        with pytest.raises(AttributeError):
            serializer.get_aadhaar_card_url(dummy)


    @pytest.mark.edge_case
    def test_raises_attribute_error_if_aadhaar_card_has_no_url(self, serializer, mock_user_profile):
        """
        Test that the method raises AttributeError if `aadhaar_card` is present but has no `url` attribute.
        """
        class AadhaarCardNoUrl:
            pass

        mock_user_profile.aadhaar_card = AadhaarCardNoUrl()
        with pytest.raises(AttributeError):
            # This will raise because the code tries to access .url on an object that doesn't have it
            _ = serializer.get_aadhaar_card_url(mock_user_profile)

    @pytest.mark.edge_case
    def test_returns_none_if_aadhaar_card_is_falsy_but_not_none(self, serializer, mock_user_profile):
        """
        Test that the method returns None if `aadhaar_card` is a falsy value (e.g., False, 0, '').
        """
        for falsy_value in [False, 0, "", [], {}, ()]:
            mock_user_profile.aadhaar_card = falsy_value
            result = serializer.get_aadhaar_card_url(mock_user_profile)
            assert result is None

    @pytest.mark.edge_case
    def test_returns_url_when_aadhaar_card_is_property(self, serializer, mock_user_profile):
        """
        Test that the method works if `aadhaar_card` is a property returning an object with a `url`.
        """
        class AadhaarCard:
            @property
            def url(self):
                return "https://cloudinary.com/aadhaar_card_property.jpg"

        mock_user_profile.aadhaar_card = AadhaarCard()
        result = serializer.get_aadhaar_card_url(mock_user_profile)
        assert result == "https://cloudinary.com/aadhaar_card_property.jpg"