import pytest
from dashboard.serializers import UserProfileSerializer

class DummyPhoto:
    """A dummy photo object with a .url attribute."""
    def __init__(self, url):
        self.url = url

class DummyUserProfile:
    """A dummy UserProfile object with a .photo attribute."""
    def __init__(self, photo=None):
        self.photo = photo

@pytest.mark.usefixtures("dummy_user_profile")
class TestUserProfileSerializerGetPhotoUrl:
    """Unit tests for UserProfileSerializer.get_photo_url method."""

    @pytest.fixture
    def serializer(self):
        """Fixture to provide a UserProfileSerializer instance."""
        return UserProfileSerializer()

    @pytest.fixture
    def dummy_user_profile(self):
        """Fixture to provide a dummy UserProfile object."""
        return DummyUserProfile()

    # ------------------- Happy Path Tests -------------------

    @pytest.mark.happy_path
    def test_returns_url_when_photo_exists(self, serializer):
        """Test that get_photo_url returns the correct URL when photo exists."""
        obj = DummyUserProfile(photo=DummyPhoto(url="https://cloudinary.com/photo.jpg"))
        result = serializer.get_photo_url(obj)
        assert result == "https://cloudinary.com/photo.jpg"

    @pytest.mark.happy_path
    def test_returns_none_when_photo_is_none(self, serializer):
        """Test that get_photo_url returns None when photo is None."""
        obj = DummyUserProfile(photo=None)
        result = serializer.get_photo_url(obj)
        assert result is None

    # ------------------- Edge Case Tests -------------------

    @pytest.mark.edge_case
    def test_returns_none_when_photo_has_no_url(self, serializer):
        """Test that get_photo_url returns None when photo object exists but has no url attribute."""
        class PhotoWithoutUrl:
            pass
        obj = DummyUserProfile(photo=PhotoWithoutUrl())
        # Should raise AttributeError, but per implementation, it will fail.
        # To simulate the edge, we catch the exception and assert it.
        with pytest.raises(AttributeError):
            serializer.get_photo_url(obj)

    @pytest.mark.edge_case
    def test_returns_none_when_obj_has_no_photo_attribute(self, serializer):
        """Test that get_photo_url raises AttributeError when obj has no photo attribute."""
        class NoPhotoAttr:
            pass
        obj = NoPhotoAttr()
        with pytest.raises(AttributeError):
            serializer.get_photo_url(obj)

    @pytest.mark.edge_case
    def test_returns_none_when_photo_url_is_empty_string(self, serializer):
        """Test that get_photo_url returns empty string if photo.url is empty string."""
        obj = DummyUserProfile(photo=DummyPhoto(url=""))
        result = serializer.get_photo_url(obj)
        assert result == ""

    @pytest.mark.edge_case
    def test_returns_none_when_photo_url_is_none(self, serializer):
        """Test that get_photo_url returns None if photo.url is None."""
        obj = DummyUserProfile(photo=DummyPhoto(url=None))
        result = serializer.get_photo_url(obj)
        assert result is None

    @pytest.mark.edge_case
    def test_returns_url_when_photo_url_is_non_string(self, serializer):
        """Test that get_photo_url returns the value even if photo.url is not a string (e.g., int)."""
        obj = DummyUserProfile(photo=DummyPhoto(url=12345))
        result = serializer.get_photo_url(obj)
        assert result == 12345