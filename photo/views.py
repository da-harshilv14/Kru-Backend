from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentSerializer
import cloudinary.uploader
import logging

logger = logging.getLogger(__name__)

def index(request):
    return HttpResponse("Photo app")

@api_view(['GET'])
@permission_classes([AllowAny])
def debug_cookies(request):
    return Response({'cookies': list(request.COOKIES.keys())})

@api_view(['GET'])
@permission_classes([AllowAny])
def test_set_cookie(request):
    r = Response({'ok': True})
    r.set_cookie('test_cookie', '1', httponly=True, samesite='Lax')
    return r

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def debug_document(request, pk):
    try:
        d = Document.objects.get(pk=pk, user=request.user)
        return Response({'id': d.id, 'type': d.document_type, 'title': d.title, 'file': str(d.file)})
    except Document.DoesNotExist:
        return Response({'error': 'not found'}, status=404)

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user).order_by('-uploaded_at')

    def _determine_resource_type(self, file_name):
        """Helper to determine resource type from file name"""
        file_name_lower = file_name.lower()
        if file_name_lower.endswith('.pdf'):
            return 'raw'
        elif file_name_lower.endswith(('.doc', '.docx', '.xls', '.xlsx', '.txt')):
            return 'raw'
        else:
            return 'image'

    def create(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        document_type = request.data.get('document_type')
        document_number = request.data.get('document_number')
        title = request.data.get('title')
        
        # If no title provided, get the label from DOCUMENT_TYPES
        if not title:
            choices_dict = dict(Document.DOCUMENT_TYPES)
            title = choices_dict.get(document_type, 'Document')

        if not file:
            return Response({'error': 'file is required'}, status=400)
        if not document_type:
            return Response({'error': 'document_type is required'}, status=400)
        if not document_number:
            return Response({'error': 'document_number is required'}, status=400)

        try:
            # Determine resource_type based on file extension
            resource_type = self._determine_resource_type(file.name)
            
            logger.info(f"Uploading {file.name} as resource_type={resource_type}")
            
            # Upload to Cloudinary
            up = cloudinary.uploader.upload(
                file, 
                resource_type=resource_type,
                folder='documents',
                type='upload',
                access_mode='public'
            )
            
            logger.info(f"Upload success: {up['public_id']}, URL: {up.get('secure_url')}")
            
            doc = Document.objects.create(
                user=request.user,
                title=title,
                document_type=document_type,
                document_number=document_number,
                file=up['public_id'],
                resource_type=resource_type,
            )
            
            return Response(self.get_serializer(doc).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception("Upload failed")
            return Response({'error': str(e)}, status=500)

    def update(self, request, *args, **kwargs):
        """Handle document updates"""
        instance = self.get_object()
        file = request.FILES.get('file')
        document_type = request.data.get('document_type')
        document_number = request.data.get('document_number')
        title = request.data.get('title')
        
        logger.info(f"=== UPDATE REQUEST ===")
        logger.info(f"Document ID: {instance.id}")
        logger.info(f"Current title: {instance.title}")
        logger.info(f"Received title: {title}")
        logger.info(f"Received document_type: {document_type}")
        logger.info(f"Has new file: {file is not None}")

        try:
            # If a new file is uploaded, handle the upload
            if file:
                # Delete old file from Cloudinary
                old_public_id = str(instance.file)
                try:
                    cloudinary.uploader.destroy(old_public_id, resource_type=instance.resource_type)
                    logger.info(f"Deleted old file: {old_public_id}")
                except Exception as e:
                    logger.warning(f"Could not delete old file: {e}")
                
                # Determine resource_type for new file
                resource_type = self._determine_resource_type(file.name)
                
                logger.info(f"Uploading new file {file.name} as resource_type={resource_type}")
                
                # Upload new file
                up = cloudinary.uploader.upload(
                    file,
                    resource_type=resource_type,
                    folder='documents',
                    type='upload',
                    access_mode='public'
                )
                
                logger.info(f"Upload success: {up['public_id']}")
                
                # Update file and resource_type
                instance.file = up['public_id']
                instance.resource_type = resource_type
            
            # Update document_type
            if document_type and document_type != instance.document_type:
                instance.document_type = document_type
                # Derive new title from document_type if title not explicitly provided
                if not title or title == 'Document':
                    choices_dict = dict(Document.DOCUMENT_TYPES)
                    instance.title = choices_dict.get(document_type, 'Document')
                    logger.info(f"Derived title from document_type: {instance.title}")
            
            # Update title only if explicitly provided and not "Document"
            if title and title != 'Document':
                instance.title = title
                logger.info(f"Using provided title: {title}")
            
            # Update document_number
            if document_number:
                instance.document_number = document_number
            
            instance.save()
            logger.info(f"Saved - Final title: {instance.title}")
            
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            logger.exception("Update failed")
            return Response({'error': str(e)}, status=500)

    def partial_update(self, request, *args, **kwargs):
        """Handle partial updates (PATCH)"""
        return self.update(request, *args, **kwargs)