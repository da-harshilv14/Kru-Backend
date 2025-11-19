from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import SubsidyApplicationSerializer, DocumentSerializer, OfficerReviewSerializer, OfficerSubsidyApplicationSerializer
from .models import SubsidyApplication, Document
from django.utils import timezone
from django.contrib.auth import get_user_model
from notifications.utils import notify_user

User = get_user_model()

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

        notify_user(
            user=request.user,
            notif_type="application",
            subject="Subsidy Application Submitted",
            message=f"Your application for '{app.subsidy.title}' has been submitted successfully."
        )
        
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
    app.status = "Pending"
    app.save()

    # 🔥 Notify the officer that a new application was assigned
    notify_user(
        user=officer,
        notif_type="application",
        subject="New Application Assigned",
        message=f"A new subsidy application (ID: {app.application_id}) has been assigned to you."
    )

    # 🔥 Notify the farmer also (optional but recommended)
    notify_user(
        user=app.user,
        notif_type="application",
        subject="Officer Assigned",
        message=f"Your application for '{app.subsidy.title}' has been assigned to Officer {officer.full_name}."
    )

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
        serializer.save()  # 🟢 Application status + officer_comment updated

        # Refresh to get updated status
        app.refresh_from_db()

        app.reviewed_at = timezone.now()
        app.save()

        # 🔥 Send notification to the farmer based on status
        current_status = app.status

        if current_status == "Approved":
            notify_user(
                user=app.user,
                notif_type="application",
                subject="✅ Application Approved!",
                message=f"🎉 Success! Your application for the '{app.subsidy.title}' subsidy has been Approved by Officer {request.user.full_name}. See the details below!"
            )

            notify_user(
                user=app.user,
                notif_type="payment",
                subject="💰 Subsidy Credited to Your Account!",
                message=f"🏦 Action Complete: The subsidy amount of ₹{app.subsidy.amount} for '{app.subsidy.title}' has been successfully credited to your registered bank account. Happy farming!"
            )

        elif current_status == "Rejected":
            comment = app.officer_comment or "Please check your application dashboard for missing documentation or non-eligibility criteria."
            notify_user(
                user=app.user,
                notif_type="application",
                subject="❌ Application Rejected",
                message=f"⚠️ Important Update: We regret to inform you that your subsidy application for '{app.subsidy.title}' was rejected. Reason: {comment}. You may be able to appeal or re-apply."
            )

        elif current_status == "Under Review":
            notify_user(
                user=app.user,
                notif_type="application",
                subject="⏳ Application Under Review",
                message=f"🔎 Processing: Your application for '{app.subsidy.title}' is actively Under Review by Officer {request.user.full_name}. We aim to finalize the decision soon. Thank you for your patience."
            )

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

    verified = str(request.data.get("verified")).lower() in ["true", "1", "yes"]

    if verified:
        app.document_status = "Verified"
    else:
        app.document_status = "Rejected"

    app.save()


    return Response({
        "message": "Document status updated",
        "document_status": app.document_status
    })

