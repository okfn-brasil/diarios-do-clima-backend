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
        self.territory_ids = self.request.GET.getlist('territory_id', [])

        self.scraped_since = self.request.GET.get("scraped_since", None)
        self.scraped_until = self.request.GET.get("scraped_until", None)
        self.published_since = self.request.GET.get("published_since", None)
        self.published_until = self.request.GET.get("published_until", None)

        self.filters_data = {
            'entities': entities,
            'subtheme': self.subthemes,
            'territory_ids': self.territory_ids,
            'scraped_since': self.scraped_since,
            'scraped_until': self.scraped_until,
            'published_since': self.published_since,
            'published_until': self.published_until,
            'querystring': self.request.GET.get('querystring', None),
            'offset': self.request.GET.get('offset', None),
            'size': self.request.GET.get('size', None),
            'pre_tags': self.request.GET.get('pre_tags', None),
            'post_tags': self.request.GET.get('post_tags', None),
            'sort_by': self.request.GET.get('sort_by', None),
        }

    def pro_subtheme_validation(self):
        has_subtheme = len(self.subthemes) > 0
        if has_subtheme and not self.plan.to_charge():
            raise ValidationError(
                {'subtheme': 'sub temas somente disponiveis para plano pro'})

    def pro_since_validation(self):
        if self.published_since is not None:
            today: timezone.datetime = timezone.now()
            since_date = datetime_from_date_str_diario(
                date=self.published_since,
            )
            since_date = timezone.make_aware(since_date)

            date_diff: timezone.timedelta = today - since_date
            since_older_then_3_months = date_diff.days > 92

            if since_older_then_3_months and not self.plan.to_charge():
                raise ValidationError(
                    {'published_since': 'data somente disponivel para plano pro'},
                )

    def get_gazettes(self) -> GazettesResult:
        querido_diario: QueridoDiarioABC = services.get(QueridoDiarioABC)
        filters = GazetteFilters(**self.filters_data)
        return querido_diario.gazettes(filters=filters)
