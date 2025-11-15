# test_serializers_validate.py

import pytest
from unittest.mock import MagicMock, patch

from subsidy.serializers import SubsidyApplicationSerializer
from rest_framework import serializers

@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = 1
    return user

@pytest.fixture
def mock_request(mock_user):
    request = MagicMock()
    request.user = mock_user
    return request

@pytest.fixture
def serializer_context(mock_request):
    return {'request': mock_request}

@pytest.fixture
def valid_attrs():
    return {
        'subsidy': 42,
        'full_name': 'John Doe',
        'mobile': '1234567890',
        'email': 'john@example.com',
        'aadhaar': '123412341234',
        'address': '123 Main St',
        'state': 'State',
        'district': 'District',
        'taluka': 'Taluka',
        'village': 'Village',
        'land_area': 1.5,
        'land_unit': 'acre',
        'soil_type': 'loamy',
        'ownership': 'self',
        'bank_name': 'Bank',
        'account_number': '123456789',
        'ifsc': 'IFSC0001',
        'document_ids': [1, 2, 3]
    }

@pytest.mark.usefixtures("serializer_context")
class TestSubsidyApplicationSerializerValidate:
    @pytest.mark.happy
    def test_validate_allows_new_application(self, serializer_context, valid_attrs, mock_user):
        """
        Test that validate allows a new application if user has not applied for the subsidy.
        """
        with patch('subsidy.serializers.SubsidyApplication.objects') as mock_manager:
            # Simulate no existing application
            mock_manager.filter.return_value.exists.return_value = False

            serializer = SubsidyApplicationSerializer(context=serializer_context)
            result = serializer.validate(valid_attrs.copy())
            assert result == valid_attrs

            mock_manager.filter.assert_called_once_with(user=mock_user, subsidy=valid_attrs['subsidy'])
            mock_manager.filter.return_value.exists.assert_called_once()

    @pytest.mark.happy
    def test_validate_allows_application_with_minimal_fields(self, serializer_context, mock_user):
        """
        Test that validate works with minimal required fields (no document_ids).
        """
        attrs = {
            'subsidy': 99,
            'full_name': 'Jane Doe',
            'mobile': '9876543210',
            'email': 'jane@example.com',
            'aadhaar': '432143214321',
            'address': '456 Main St',
            'state': 'State2',
            'district': 'District2',
            'taluka': 'Taluka2',
            'village': 'Village2',
            'land_area': 2.0,
            'land_unit': 'hectare',
            'soil_type': 'clay',
            'ownership': 'rented',
            'bank_name': 'Bank2',
            'account_number': '987654321',
            'ifsc': 'IFSC0002',
        }
        with patch('subsidy.serializers.SubsidyApplication.objects') as mock_manager:
            mock_manager.filter.return_value.exists.return_value = False

            serializer = SubsidyApplicationSerializer(context=serializer_context)
            result = serializer.validate(attrs.copy())
            assert result == attrs

    @pytest.mark.happy
    def test_validate_allows_application_with_empty_document_ids(self, serializer_context, valid_attrs, mock_user):
        """
        Test that validate works when document_ids is an empty list.
        """
        attrs = valid_attrs.copy()
        attrs['document_ids'] = []
        with patch('subsidy.serializers.SubsidyApplication.objects') as mock_manager:
            mock_manager.filter.return_value.exists.return_value = False

            serializer = SubsidyApplicationSerializer(context=serializer_context)
            result = serializer.validate(attrs.copy())
            assert result == attrs

    @pytest.mark.edge
    def test_validate_raises_if_already_applied(self, serializer_context, valid_attrs, mock_user):
        """
        Test that validate raises ValidationError if user has already applied for the subsidy.
        """
        with patch('subsidy.serializers.SubsidyApplication.objects') as mock_manager:
            mock_manager.filter.return_value.exists.return_value = True

            serializer = SubsidyApplicationSerializer(context=serializer_context)
            with pytest.raises(serializers.ValidationError) as excinfo:
                serializer.validate(valid_attrs.copy())
            assert "already applied" in str(excinfo.value)

    @pytest.mark.edge
    def test_validate_handles_missing_subsidy_key(self, serializer_context, valid_attrs, mock_user):
        """
        Test that validate works gracefully if 'subsidy' key is missing (should pass None to filter).
        """
        attrs = valid_attrs.copy()
        attrs.pop('subsidy')
        with patch('subsidy.serializers.SubsidyApplication.objects') as mock_manager:
            mock_manager.filter.return_value.exists.return_value = False

            serializer = SubsidyApplicationSerializer(context=serializer_context)
            result = serializer.validate(attrs.copy())
            assert result == attrs
            mock_manager.filter.assert_called_once_with(user=mock_user, subsidy=None)

    @pytest.mark.edge
    def test_validate_handles_missing_user_in_context(self, valid_attrs, serializer_context):
        """
        Test that validate raises KeyError if 'user' is missing from request in context.
        """
        context = {'request': MagicMock()}
        del context['request'].user  # Remove user attribute

        serializer = SubsidyApplicationSerializer(context=context)
        with patch('subsidy.serializers.SubsidyApplication.objects'):
            with pytest.raises(AttributeError):
                serializer.validate(valid_attrs.copy())

    @pytest.mark.edge
    def test_validate_handles_missing_request_in_context(self, valid_attrs):
        """
        Test that validate raises KeyError if 'request' is missing from context.
        """
        serializer = SubsidyApplicationSerializer(context={})
        with patch('subsidy.serializers.SubsidyApplication.objects'):
            with pytest.raises(KeyError):
                serializer.validate(valid_attrs.copy())