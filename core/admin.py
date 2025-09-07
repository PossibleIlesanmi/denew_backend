from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from accounts.models import User, UserProfile, Task, Deposit, Withdrawal, Invitation, TermsAndConditions, Portfolio, SupportTicket
from accounts.admin import UserAdmin, UserProfileAdmin, TaskAdmin, DepositAdmin, WithdrawalAdmin, InvitationAdmin, TermsAndConditionsAdmin, PortfolioAdmin, SupportTicketAdmin
from django.db.models import Sum
import logging

logger = logging.getLogger(__name__)

class DenewAdminSite(admin.AdminSite):
    site_header = "Denew Networking Admin Dashboard"
    site_title = "Denew Admin"
    index_title = "Platform Management"

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}

        # User statistics
        total_users = User.objects.count()
        verified_users = User.objects.filter(is_verified=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        recent_users = User.objects.filter(date_joined__gte=timezone.now() - timedelta(days=7)).count()
        users_with_referrals = User.objects.exclude(referral_code__isnull=True).exclude(referral_code='').count()

        # Additional statistics
        total_deposits = Deposit.objects.aggregate(total=Sum('amount'))['total'] or 0
        total_withdrawals = Withdrawal.objects.aggregate(total=Sum('amount'))['total'] or 0
        completed_tasks = Task.objects.filter(status='completed').count()

        extra_context.update({
            'total_users': total_users,
            'verified_users': verified_users,
            'staff_users': staff_users,
            'recent_users': recent_users,
            'users_with_referrals': users_with_referrals,
            'verification_rate': (verified_users / total_users * 100) if total_users > 0 else 0,
            'total_deposits': total_deposits,
            'total_withdrawals': total_withdrawals,
            'completed_tasks': completed_tasks,
        })

        logger.info(f"Admin dashboard stats: {extra_context}")
        return super().index(request, extra_context)

# Instantiate the custom admin site
admin_site = DenewAdminSite(name='denew_admin')

# Register all models with the custom admin site
admin_site.register(User, UserAdmin)
admin_site.register(UserProfile, UserProfileAdmin)
admin_site.register(Task, TaskAdmin)
admin_site.register(Deposit, DepositAdmin)
admin_site.register(Withdrawal, WithdrawalAdmin)
admin_site.register(Invitation, InvitationAdmin)
admin_site.register(TermsAndConditions, TermsAndConditionsAdmin)
admin_site.register(Portfolio, PortfolioAdmin)
admin_site.register(SupportTicket, SupportTicketAdmin)