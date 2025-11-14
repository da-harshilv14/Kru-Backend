# subsidy/views.py
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import DocumentSerializer, SubsidyApplicationSerializer
from .models import Document

# Upload single document (multipart/form-data)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])  # OK to keep; parsers ignored for GET
def upload_document(request):
    if request.method == 'GET':
        # return documents for the current user (or change to all() if you want)
        qs = Document.objects.filter(owner=request.user).order_by('-uploaded_at')
        serializer = DocumentSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST -> create a new Document (multipart/form-data expected)
    serializer = DocumentSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        doc = serializer.save(owner=request.user)  # pass owner if serializer doesn't set it
        return Response(DocumentSerializer(doc, context={'request': request}).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Submit application (expects JSON, application is created with request.user)
@api_view(['POST','GET'])
@permission_classes([IsAuthenticated])
def apply_subsidy(request):
    """
    Expects JSON like:
    {
      "subsidy_id": 1,
      "document_ids": [1,2],
      "full_name": "...",
      "mobile": "...",
      ...
    }
    """
    serializer = SubsidyApplicationSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        app = serializer.save()
        return Response({'message': 'Application submitted successfully', 'id': app.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
