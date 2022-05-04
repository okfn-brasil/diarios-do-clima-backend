from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from ..models import Report
from ..serializers import ReportSerializer


class ReportsPublicApiView(ListAPIView):
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = ReportSerializer
    queryset = Report.objects.filter(is_public=True)
