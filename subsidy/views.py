from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import SubsidyApplicationSerializer, DocumentSerializer, OfficerReviewSerializer, OfficerSubsidyApplicationSerializer
from .models import SubsidyApplication, Document
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction

User = get_user_model()
from .models import SubsidyApplication
from .serializers import SubsidyApplicationSerializer

class SubsidyApplicationViewSet(viewsets.ModelViewSet):
    """
    CRUD viewset for SubsidyApplication.
    Adds a custom action `mark_payment_done` to transition Approved -> Payment done.
    """
    queryset = SubsidyApplication.objects.all().select_related("subsidy", "user")
    serializer_class = SubsidyApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally filter so providers only see their subsidy applications.
        Adjust logic if providers are staff or another model.
        """
        qs = super().get_queryset()
        user = self.request.user

        # If provider users should only see applications for subsidies they own,
        # uncomment following lines and adjust attribute name as needed:
        # owned_subsidy_pk_list = []
        # for s in Subsidy.objects.filter(provider=user).values_list('pk', flat=True):
        #     owned_subsidy_pk_list.append(s)
        # qs = qs.filter(subsidy__in=owned_subsidy_pk_list)

        return qs

    @action(detail=True, methods=["post"], url_path="mark_payment_done")
    def mark_payment_done(self, request, pk=None):
        """
        POST /api/applications/<pk>/mark_payment_done/
        Only the subsidy provider (owner) may perform this. Allowed transition: Approved -> Payment done
        """
        app = self.get_object()

        # Determine subsidy owner/provider by trying common attribute names
        subsidy = getattr(app, "subsidy", None)
        provider_user = None
        if subsidy is not None:
            provider_user = getattr(subsidy, "provider", None) \
                            or getattr(subsidy, "owner", None) \
                            or getattr(subsidy, "created_by", None) \
                            or getattr(subsidy, "user", None)

        # Check provider authorization
        if provider_user is None:
            return Response({"detail": "Subsidy owner not configured on backend."}, status=status.HTTP_400_BAD_REQUEST)

        if provider_user != request.user and not request.user.is_staff:
            return Response({"detail": "Not allowed. Only subsidy provider or staff can mark payment."},
                            status=status.HTTP_403_FORBIDDEN)

        # Normalize status check and only allow Approved -> Payment done
        current_status = (app.status or "").strip().lower()
        if current_status != "approved":
            return Response({"detail": f"Invalid status transition: current status = '{app.status}'."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Perform update in a transaction (atomic)
        with transaction.atomic():
            app.status = "Payment done"   # EXACT string as in your model choice
            app.save(update_fields=["status"])

            # Optionally: record an audit log in a separate model, or set reviewed_at etc.
            # e.g. app.reviewed_at = timezone.now(); app.save(update_fields=["status", "reviewed_at"])

        serializer = self.get_serializer(app)
        return Response(serializer.data, status=status.HTTP_200_OK)
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





@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def apply_subsidy(request):

    if request.method == 'GET':
        apps = SubsidyApplication.objects.filter(
            user=request.user
        ).select_related('subsidy').prefetch_related('documents')

        out = []
        for app in apps:
            out.append({
                "id": app.id,
                "application_id": app.application_id,
                "subsidy_id": app.subsidy.id,
                "subsidy_name": app.subsidy.title,
                "amount":app.subsidy.amount,
                "status": app.status,
                "applied_on": app.submitted_at.isoformat(),
            })

        return Response(out, status=200)

    # POST
    data = request.data.copy()
    data.pop("user", None)  # Prevent frontend overwriting

    serializer = SubsidyApplicationSerializer(
        data=data,
        context={"request": request}
    )

    if serializer.is_valid():
        app = serializer.save()
        return Response(
            {"message": "Application submitted", "application_id": app.application_id},
            status=201
        )

    return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_officer(request, app_id):
    if request.user.role != "admin":
        return Response({"detail": "Not allowed"}, status=403)

    officer_id = request.data.get("officer_id")

    try:
        app = SubsidyApplication.objects.get(id=app_id)
    except SubsidyApplication.DoesNotExist:
        return Response({"detail": "Application not found"}, status=404)

    try:
        officer = User.objects.get(id=officer_id, role="officer")
    except User.DoesNotExist:
        return Response({"detail": "Invalid officer"}, status=400)

    app.assigned_officer = officer
    app.status = "Under Review"
    app.save()

    return Response({"message": "Officer assigned successfully"}, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def officer_dashboard(request):
    if request.user.role != "officer":
        return Response({"detail": "Not allowed"}, status=403)

    apps = SubsidyApplication.objects.filter(
        assigned_officer=request.user
    ).select_related('subsidy')

    serializer = OfficerSubsidyApplicationSerializer(apps, many=True)
    return Response(serializer.data, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_application(request, app_id):
    if request.user.role != "officer":
        return Response({"detail": "Not allowed"}, status=403)

    try:
        app = SubsidyApplication.objects.get(
            id=app_id,
            assigned_officer=request.user
        )
    except SubsidyApplication.DoesNotExist:
        return Response({"detail": "Not found or not assigned to you"}, status=404)

    serializer = OfficerReviewSerializer(app, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        app.reviewed_at = timezone.now()
        app.save()
        return Response({"message": "Application updated", "status": app.status})

    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def officer_application_detail(request, app_id):
    if request.user.role != "officer":
        return Response({"detail": "Not allowed"}, status=403)

    try:
        app = SubsidyApplication.objects.select_related(
            "subsidy", "assigned_officer"
        ).prefetch_related("documents").get(
            id=app_id,
            assigned_officer=request.user
        )
    except SubsidyApplication.DoesNotExist:
        return Response({"detail": "Application not found"}, status=404)

    data = {
        "id": app.id,
        "application_id": app.application_id,

        # Farmer information
        "applicant_name": app.full_name,
        "applicant_email": app.email,
        "mobile": app.mobile,
        "aadhaar": app.aadhaar,
        "address": app.address,
        "state": app.state,
        "district": app.district,
        "taluka": app.taluka,
        "village": app.village,

        # Land details
        "land_area": app.land_area,
        "land_unit": app.land_unit,
        "soil_type": app.soil_type,
        "ownership": app.ownership,

        # Bank details
        "bank_name": app.bank_name,
        "account_number": app.account_number,
        "ifsc": app.ifsc,

        # Subsidy details
        "subsidy_title": app.subsidy.title,
        "subsidy_amount": app.subsidy.amount,

        # Officer review
        "status": app.status,
        "document_status": app.document_status,
        "officer_comment": app.officer_comment,
        "assigned_officer_name": app.assigned_officer.full_name if app.assigned_officer else None,

        "submitted_at": app.submitted_at,
        "reviewed_at": app.reviewed_at,
    }

    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def officer_application_documents(request, app_id):
    if request.user.role != "officer":
        return Response({"detail": "Not allowed"}, status=403)

    try:
        app = SubsidyApplication.objects.get(
            id=app_id,
            assigned_officer=request.user
        )
    except SubsidyApplication.DoesNotExist:
        return Response({"detail": "Application not found"}, status=404)

    docs = app.documents.all()

    data = [{
        "id": d.id,
        "document_type": d.document_type,
        "document_number": d.document_number,
        "uploaded_at": d.uploaded_at,
        "file_url": d.file.url if d.file else None
    } for d in docs]

    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def officer_verify_documents(request, app_id):
    if request.user.role != "officer":
        return Response({"detail": "Not allowed"}, status=403)

    try:
        app = SubsidyApplication.objects.get(
            id=app_id,
            assigned_officer=request.user
        )
    except SubsidyApplication.DoesNotExist:
        return Response({"detail": "Application not found"}, status=404)

    verified = request.data.get("verified")
    if verified is True:
        app.document_status = "Verified"
    else:
        app.document_status = "Rejected"   # FLAG DOCUMENTS
    app.save()

    return Response({
        "message": "Document status updated",
        "document_status": app.document_status
    })

