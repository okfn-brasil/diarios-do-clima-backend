from django.db.models import Q
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from ..models import Report
from ..serializers import ReportSerializer


class ReportsApiView(RetrieveAPIView):
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = ReportSerializer

    def get_queryset(self):
        query = Q(reportuseraccess__user=self.request.user) | Q(is_public=True)
        return Report.objects.filter(query)
