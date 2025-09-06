from django_cron import CronJobBase, Schedule
from django.db.models import Sum
from .models import Invitation, Task, User

class CalculateCommissions(CronJobBase):
    RUN_EVERY_MINS = 1440  # Run daily
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'accounts.calculate_commissions'

    def do(self):
        for invitation in Invitation.objects.all():
            referee = User.objects.filter(email=invitation.referee_email).first()
            if referee:
                earnings = Task.objects.filter(user=referee, status='completed').aggregate(total=Sum('earnings'))['total'] or 0
                commission = earnings * 0.2
                invitation.referrer.balance += commission
                invitation.referrer.save()