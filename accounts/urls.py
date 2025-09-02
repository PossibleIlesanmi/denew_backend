from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication and Profile
    path('api/register/', views.register_user, name='register_user'),
    path('api/login/', views.login_user, name='login_user'),
    path('api/logout/', views.logout_user, name='logout_user'),
    path('api/profile/', views.get_user_profile, name='get_user_profile'),
    path('api/profile/update/', views.update_user_profile, name='update_user_profile'),
    path('api/dashboard/', views.dashboard_data, name='dashboard_data'),
    
    # Task System
    path('api/tasks/', views.list_tasks, name='list_tasks'),
    path('api/tasks/current/', views.get_current_task, name='get_current_task'),
    path('api/tasks/products/', views.get_products, name='get_products'),
    path('api/tasks/start-set/', views.start_task_set, name='start_task_set'),
    path('api/tasks/start/', views.start_task, name='start_task'),
    path('api/tasks/complete/', views.submit_task, name='submit_task'),  # Corrected view name
    path('api/account/reset/', views.reset_account, name='reset_account'),
    
    # Balance and VIP
    path('api/account/balance/', views.get_balance, name='get_balance'),
    path('api/vip-level/', views.get_vip_level, name='get_vip_level'),
    
    # Password and Security
    path('api/lost-pin/send-code/', views.send_verification_code, name='send_verification_code'),
    path('api/lost-pin/verify-code/', views.verify_code, name='verify_code'),
    path('api/lost-pin/reset-pin/', views.reset_pin, name='reset_pin'),
    path('api/withdrawal-pin/set/', views.set_withdrawal_pin, name='set_withdrawal_pin'),
    
    # Deposits and Withdrawals
    path('api/deposits/', views.make_deposit, name='make_deposit'),
    path('api/withdrawals/', views.request_withdrawal, name='request_withdrawal'),
    path('api/withdrawals/list/', views.list_all_withdrawals, name='list_all_withdrawals'),
    path('api/withdrawals/<int:withdrawal_id>/', views.get_withdrawal_details, name='get_withdrawal_details'),
    path('api/withdrawals/<int:withdrawal_id>/complete/', views.complete_withdrawal, name='complete_withdrawal'),
    path('api/withdrawals/bulk-complete/', views.bulk_complete_withdrawals, name='bulk_complete_withdrawals'),
    
    # Invitations and Support
    path('api/invitations/', views.get_invitations, name='get_invitations'),
    path('api/invite/', views.invite_friend, name='invite_friend'),
    path('api/support/', views.create_support_ticket, name='create_support_ticket'),
    
    # Terms and Portfolio
    path('api/terms/', views.get_terms, name='get_terms'),
    path('api/portfolio/', views.get_portfolio, name='get_portfolio'),
    path('api/portfolio/update/', views.update_portfolio, name='update_portfolio'),
    path('api/transaction-history/', views.get_transaction_history, name='get_transaction_history'),
    path('api/transaction-history/enhanced/', views.get_enhanced_transaction_history, name='get_enhanced_transaction_history'),
    
    # Campaigns
    path('api/campaigns/', views.get_campaigns, name='get_campaigns'),
]