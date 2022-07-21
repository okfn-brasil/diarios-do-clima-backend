from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from libs.services import services
from libs.querido_diario import QueridoDiarioABC
from libs.querido_diario.serializers import GazettesResult, GazetteFilters
from plans.models import Plan
from subscriptions.models import PlanSubscription
from subscriptions.selectors import user_get_latest_plan_subscription
from django.utils import timezone
from libs.utils.datetime import datetime_from_date_str_diario


class GazettesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        self.get_user_plan()
        self.setup_query_data()
        self.pro_subtheme_validation()
        self.pro_since_validation()
        data = self.get_gazettes()

        return Response(data.json())

    def get_user_plan(self):
        user = self.request.user
        try:
            user_plan_subscription: PlanSubscription = user_get_latest_plan_subscription(
                user=user,
            )
        except PlanSubscription.DoesNotExist:
            raise ValidationError(
                {
                    'plan_subscription': [
                        'usuario deve ter uma assinatura ativa',
                    ],
                },
            )
        self.plan: Plan = user_plan_subscription.plan

    def setup_query_data(self):
        entities = self.request.GET.getlist('entities', [])
        self.subthemes = self.request.GET.getlist('subtheme', [])
        self.since = self.request.GET.get('since', None)
        self.filters_data = {
            'entities': entities,
            'subtheme': self.subthemes,
            'territory_id': self.request.GET.get('territory_id', None),
            'since': self.since,
            'until': self.request.GET.get('until', None),
            'querystring': self.request.GET.get('querystring', None),
            'offset': self.request.GET.get('offset', None),
            'size': self.request.GET.get('size', None),
            'pre_tags': self.request.GET.get('pre_tags', None),
            'post_tags': self.request.GET.get('post_tags', None),
        }

    def pro_subtheme_validation(self):
        has_subtheme = len(self.subthemes) > 0
        if has_subtheme and not self.plan.to_charge():
            raise ValidationError(
                {'subtheme': 'sub temas somente disponiveis para plano pro'})

    def pro_since_validation(self):
        if self.since is not None:
            today: timezone.datetime = timezone.now()
            since_date = datetime_from_date_str_diario(date=self.since)
            since_date = timezone.make_aware(since_date)

            date_diff: timezone.timedelta = today - since_date
            since_older_then_3_months = date_diff.days > 90

            if since_older_then_3_months and not self.plan.to_charge():
                raise ValidationError(
                    {'since': 'data somente disponivel para plano pro'})

    def get_gazettes(self) -> GazettesResult:
        querido_diario: QueridoDiarioABC = services.get(QueridoDiarioABC)
        filters = GazetteFilters(**self.filters_data)
        return querido_diario.gazettes(filters=filters)
