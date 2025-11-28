"""
Unit tests for UserProfileSerializer.get_pan_card_url in dashboard/serializers.py

Covers:
- Happy paths: pan_card present with url, pan_card present with empty url, pan_card present with None url
- Edge cases: pan_card is None, pan_card attribute missing, pan_card object without url attribute, obj is None
"""

import pytest
from types import SimpleNamespace
from dashboard.serializers import UserProfileSerializer

@pytest.mark.usefixtures("dummy_serializer")
class TestUserProfileSerializerGetPanCardUrl:
    @pytest.fixture(autouse=True)
    def dummy_serializer(self):
        # Create a serializer instance for method calls
        self.serializer = UserProfileSerializer()

    # ------------------- HAPPY PATHS -------------------
    @pytest.mark.happy_path
    def test_pan_card_present_with_valid_url(self):
        """Test get_pan_card_url returns correct url when pan_card is present and has a valid url."""
        obj = SimpleNamespace(pan_card=SimpleNamespace(url="https://cloudinary.com/pan_card.jpg"))
        result = self.serializer.get_pan_card_url(obj)
        assert result == "https://cloudinary.com/pan_card.jpg"

    @pytest.mark.happy_path
    def test_pan_card_present_with_empty_url(self):
        """Test get_pan_card_url returns empty string when pan_card is present and url is empty string."""
        obj = SimpleNamespace(pan_card=SimpleNamespace(url=""))
        result = self.serializer.get_pan_card_url(obj)
        assert result == ""

    @pytest.mark.happy_path
    def test_pan_card_present_with_none_url(self):
        """Test get_pan_card_url returns None when pan_card is present but url is None."""
        obj = SimpleNamespace(pan_card=SimpleNamespace(url=None))
        result = self.serializer.get_pan_card_url(obj)
        assert result is None

    # ------------------- EDGE CASES -------------------
    @pytest.mark.edge_case
    def test_pan_card_is_none(self):
        """Test get_pan_card_url returns None when pan_card is None."""
        obj = SimpleNamespace(pan_card=None)
        result = self.serializer.get_pan_card_url(obj)
        assert result is None

    @pytest.mark.edge_case
    def test_obj_missing_pan_card_attribute(self):
        """
        REAL serializer directly reads obj.pan_card.
        Missing attribute must raise AttributeError.
        """
        obj = SimpleNamespace()  # no pan_card attribute

        with pytest.raises(AttributeError):
            self.serializer.get_pan_card_url(obj)

    @pytest.mark.edge_case
    def test_pan_card_object_missing_url_attribute(self):
        """Test get_pan_card_url raises AttributeError when pan_card object has no url attribute."""
        obj = SimpleNamespace(pan_card=SimpleNamespace())
        with pytest.raises(AttributeError):
            self.serializer.get_pan_card_url(obj)

    @pytest.mark.edge_case
    def test_obj_is_none(self):
        """Test get_pan_card_url raises AttributeError when obj is None."""
        with pytest.raises(AttributeError):
            self.serializer.get_pan_card_url(None)
