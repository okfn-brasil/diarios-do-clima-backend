from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from ..models import Report
from ..serializers import ReportSerializer


class ReportsPrivateApiView(ListAPIView):
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = ReportSerializer

    def get_queryset(self):
        query_user = Q(reportuseraccess__user=self.request.user)
        query_private = Q(is_public=False)
        query = query_user & query_private
        return Report.objects.filter(query)
