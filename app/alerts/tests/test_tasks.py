from django.core import mail
from rest_framework.test import APITestCase
from accounts.models import User
from ..models import Alert
from ..tasks import DailySetupTask, SingleAlertTask, OnlyProPlanAllowed
from plans.actions import create_user_plan_subscription
from plans.models import Plan
from subscriptions.models import PlanSubscriptionStatus
from libs.services import services
from libs.querido_diario import QueridoDiarioABC
from libs.querido_diario.serializers import GazettesResult
from unittest import mock


class TestAlertViewSet(APITestCase):
    @classmethod
    def setUpUser(cls):
        cls.QueridoDiarioMock = mock.MagicMock(spec=QueridoDiarioABC)
        services.register(QueridoDiarioABC, cls.QueridoDiarioMock)

        cls.data_login = {
            "email": "email@diariodoclima.org.br",
            "password": "password",
        }

        cls.data_user = {
            **cls.data_login,
            "city": "Cidade",
            "full_name": "Nome Completo",
            "gender": "f",
            "state": "UF",
            "sector": "private",
        }
        cls.user = User.objects.create_user(**cls.data_user)
        cls.user.save()

        cls.user_other = User.objects.create_user(
            email="email1@diariodoclima.org.br",
            password="password",
            city="Cidade",
            full_name="Nome Completo1",
            gender="f",
            state="UF",
            sector="private",
        )
        cls.user_other.save()

        cls.alert = Alert(
            user=cls.user,
            query_string="ffg, yj",
            territories=[
                "1501402",
            ],
            sub_themes=["tutorial", "django", "hell", "la", "SF"],
            gov_entities=["django", "hell", "SF"],
        )
        cls.alert.save()

        cls.alert_other = Alert(
            user=cls.user_other,
            query_string="ffg, yj",
            sub_themes=["tutorial", "django", "hell", "la", "SF"],
            gov_entities=["django", "hell", "SF"],
        )
        cls.alert_other.save()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setUpUser()

    def setup_pro_plan(self):
        plan = Plan(
            title='Pro',
            html='',
            pagseguro_plan_id='reference-plan',
            trial_days=7,
        )
        plan.save()

        plan_subscription = create_user_plan_subscription(
            user=self.user, plan=plan)

        plan_subscription_status = PlanSubscriptionStatus(
            plan_subscription=plan_subscription,
            pagseguro_data=PlanSubscriptionStatus.DATA_ACTIVE,
        )
        plan_subscription_status.save()

    def test_daily_setup_task(self):
        alerts_ids = []

        def dummy_subtask(**kwargs):
            alert_id: str = kwargs.get("alert_id")
            alerts_ids.append(alert_id)

        task = DailySetupTask(subtask=dummy_subtask)
        task()

        alerts_ids_query = Alert.objects.values_list("id", flat=True)
        alerts_ids_query_list = [id for id in alerts_ids_query]

        self.assertEquals(alerts_ids, alerts_ids_query_list)

    def test_single_task_free_user(self):
        task = SingleAlertTask(alert_id=self.alert.id)
        with self.assertRaises(OnlyProPlanAllowed):
            task.verify_permissions()

    def test_single_task_pro_user_zero(self):
        self.setup_pro_plan()
        self.QueridoDiarioMock.gazettes.return_value = GazettesResult(
            total_gazettes=0,
            gazettes=[],
        )
        task = SingleAlertTask(alert_id=self.alert.id)
        task()
        self.assertEquals(task.results.total_gazettes, 0)
        emails_len = len(mail.outbox)
        self.assertEquals(emails_len, 0)

    def test_single_task_pro_user_many(self):
        self.setup_pro_plan()
        self.QueridoDiarioMock.gazettes.return_value = GazettesResult(
            total_gazettes=5,
            gazettes=[],
        )
        task = SingleAlertTask(alert_id=self.alert.id)
        task()
        self.assertEquals(task.results.total_gazettes, 5)
        emails_len = len(mail.outbox)
        self.assertEquals(emails_len, 1)

    def test_single_task_pro_user_many_with_no_territory(self):
        self.setup_pro_plan()
        self.QueridoDiarioMock.gazettes.return_value = GazettesResult(
            total_gazettes=5,
            gazettes=[],
        )
        task = SingleAlertTask(alert_id=self.alert_other.id)
        task()
        self.assertEquals(task.results.total_gazettes, 5)
        emails_len = len(mail.outbox)
        self.assertEquals(emails_len, 1)
