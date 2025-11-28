# test_serializers.py

import pytest
from unittest.mock import Mock

from dashboard.serializers import UserProfileSerializer

@pytest.mark.usefixtures("mock_user_profile")
class TestUserProfileSerializerGetLandProofUrl:
    """
    Unit tests for UserProfileSerializer.get_land_proof_url method.
    """

    @pytest.fixture
    def serializer(self):
        """Fixture to instantiate the serializer."""
        return UserProfileSerializer()

    @pytest.fixture
    def mock_user_profile(self):
        """Fixture to provide a mock UserProfile object."""
        return Mock()

    # ------------------- Happy Path Tests -------------------

    @pytest.mark.happy
    def test_returns_url_when_land_proof_present(self, serializer, mock_user_profile):
        """
        Test that get_land_proof_url returns the correct URL when land_proof is present.
        """
        mock_land_proof = Mock()
        mock_land_proof.url = "https://cloudinary.com/land_proof.jpg"
        mock_user_profile.land_proof = mock_land_proof

        result = serializer.get_land_proof_url(mock_user_profile)
        assert result == "https://cloudinary.com/land_proof.jpg"

    @pytest.mark.happy
    def test_returns_url_when_land_proof_url_is_empty_string(self, serializer, mock_user_profile):
        """
        Test that get_land_proof_url returns an empty string if land_proof.url is an empty string.
        """
        mock_land_proof = Mock()
        mock_land_proof.url = ""
        mock_user_profile.land_proof = mock_land_proof

        result = serializer.get_land_proof_url(mock_user_profile)
        assert result == ""

    # ------------------- Edge Case Tests -------------------

    @pytest.mark.edge
    def test_returns_none_when_land_proof_is_none(self, serializer, mock_user_profile):
        """
        Test that get_land_proof_url returns None when land_proof is None.
        """
        mock_user_profile.land_proof = None

        result = serializer.get_land_proof_url(mock_user_profile)
        assert result is None

    @pytest.mark.edge
    def test_returns_none_when_land_proof_attribute_missing(self, serializer):
        """
        Since the actual serializer directly accesses obj.land_proof,
        a missing attribute will raise AttributeError.
        """
        obj = Mock(spec=[])  # has no land_proof attribute

        with pytest.raises(AttributeError):
            serializer.get_land_proof_url(obj)


    @pytest.mark.edge
    def test_raises_attribute_error_when_land_proof_has_no_url(self, serializer, mock_user_profile):
        """
        Test that get_land_proof_url raises AttributeError if land_proof exists but has no 'url' attribute.
        """
        class LandProofNoUrl:
            pass

        mock_user_profile.land_proof = LandProofNoUrl()

        with pytest.raises(AttributeError):
            # This will raise because LandProofNoUrl has no 'url'
            _ = serializer.get_land_proof_url(mock_user_profile)

    @pytest.mark.edge
    def test_returns_none_when_land_proof_is_falsey_but_not_none(self, serializer, mock_user_profile):
        """
        Test that get_land_proof_url returns None when land_proof is a falsey value (e.g., False, 0, '').
        """
        for falsey in [False, 0, ""]:
            mock_user_profile.land_proof = falsey
            result = serializer.get_land_proof_url(mock_user_profile)
            assert result is None

    @pytest.mark.edge
    def test_returns_url_when_land_proof_is_property(self, serializer, mock_user_profile):
        """
        Test that get_land_proof_url works if land_proof is a property returning a mock with a url.
        """
        class LandProof:
            @property
            def url(self):
                return "https://cloudinary.com/land_proof_property.jpg"

        mock_user_profile.land_proof = LandProof()
        result = serializer.get_land_proof_url(mock_user_profile)
        assert result == "https://cloudinary.com/land_proof_property.jpg"