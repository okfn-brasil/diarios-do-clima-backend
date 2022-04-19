from rest_framework.generics import ListAPIView
from .models import Plan
from .serializers import PlanSerializer


class PlanApiView(ListAPIView):
    serializer_class = PlanSerializer
    queryset = Plan.objects.all()
