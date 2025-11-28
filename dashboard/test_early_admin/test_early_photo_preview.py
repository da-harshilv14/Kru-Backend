import os
import sys
import django
import pytest
from unittest.mock import Mock
from django.utils.html import format_html

# --------------------------------------------------------------
#  FIX PYTHON PATH SO DJANGO PROJECT CAN BE IMPORTED
# --------------------------------------------------------------
# This is the directory that contains the "back" project folder
sys.path.append("/home/desairudra/krushisetu-new/KrushiSetu")

# --------------------------------------------------------------
#  SETUP DJANGO SETTINGS
# --------------------------------------------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "back.settings")

django.setup()

from dashboard.admin import UserProfileAdmin


@pytest.mark.usefixtures("rf")
class TestUserProfileAdminPhotoPreview:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.admin = UserProfileAdmin(model=Mock(), admin_site=Mock())

    # Happy path
    def test_photo_preview_with_valid_photo(self):
        mock_photo = Mock(url="http://testserver/media/photos/p1.jpg")
        obj = Mock(photo=mock_photo)

        result = self.admin.photo_preview(obj)
        expected = format_html(
            '<img src="{}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 4px;" />',
            mock_photo.url
        )
        assert result == expected

    # Edge cases
    def test_photo_preview_with_no_photo(self):
        obj = Mock(photo=None)
        assert self.admin.photo_preview(obj) == "-"

    def test_photo_preview_with_missing_url(self):
        obj = Mock(photo=Mock())
        del obj.photo.url
        with pytest.raises(AttributeError):
            self.admin.photo_preview(obj)

    def test_photo_preview_with_empty_url(self):
        mock_photo = Mock(url="")
        obj = Mock(photo=mock_photo)

        result = self.admin.photo_preview(obj)
        expected = format_html(
            '<img src="{}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 4px;" />',
            ""
        )
        assert result == expected

    def test_photo_preview_none_obj(self):
        with pytest.raises(AttributeError):
            self.admin.photo_preview(None)
