from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils import timezone  # Add this import
from .models import User, UserProfile, Task, Deposit, Withdrawal, Invitation, TermsAndConditions, Portfolio, SupportTicket,Product  # Add Product here

# Admin Actions
@admin.action(description='Mark selected users as verified')
def make_verified(modeladmin, request, queryset):
    queryset.update(is_verified=True)

@admin.action(description='Mark selected users as unverified')
def make_unverified(modeladmin, request, queryset):
    queryset.update(is_verified=False)

@admin.action(description='Approve selected withdrawals')
def approve_withdrawals(modeladmin, request, queryset):
    for withdrawal in queryset:
        if withdrawal.status == 'pending':
            withdrawal.status = 'completed'
            withdrawal.processed_at = timezone.now()
            withdrawal.save()
            withdrawal.user.balance -= withdrawal.amount
            withdrawal.user.save()

@admin.action(description='Reject selected withdrawals')
def reject_withdrawals(modeladmin, request, queryset):
    for withdrawal in queryset:
        if withdrawal.status == 'pending':
            withdrawal.status = 'rejected'
            withdrawal.processed_at = timezone.now()
            withdrawal.user.balance += withdrawal.amount  # Refund
            withdrawal.user.save()
            withdrawal.save()

# Inline for UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Information'
    fields = ('avatar', 'bio', 'location', 'website')

# Custom User Admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    actions = [make_verified, make_unverified]
    list_display = (
        'username', 'email', 'full_name', 'phone_number',
        'verification_badge', 'staff_badge', 'referral_info', 'balance', 'join_date'
    )
    list_filter = (
        'is_staff', 'is_superuser', 'is_active', 'is_verified',
        'date_joined', 'last_login', 'vip_level'
    )
    search_fields = ('username', 'email', 'full_name', 'phone_number', 'referral_code')
    ordering = ('-date_joined',)
    list_per_page = 25

    def verification_badge(self, obj):
        return format_html('<span style="color: green;">✓ Verified</span>' if obj.is_verified else '<span style="color: red;">✗ Unverified</span>')
    verification_badge.short_description = 'Verification Status'

    def staff_badge(self, obj):
        return format_html('<span style="color: blue;">👑 Staff</span>' if obj.is_staff else '<span style="color: gray;">👤 User</span>')
    staff_badge.short_description = 'Role'

    def referral_info(self, obj):
        return format_html('<code>{}</code>' if obj.referral_code else '<span style="color: gray;">No referral</span>', obj.referral_code)
    referral_info.short_description = 'Referral Code'

    def join_date(self, obj):
        return obj.date_joined.strftime('%Y-%m-%d')
    join_date.short_description = 'Joined'

    fieldsets = (
        ('Account Info', {
            'fields': ('username', 'email', 'password'),
            'classes': ('wide',)
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'full_name', 'phone_number'),
            'classes': ('wide',)
        }),
        ('Platform Settings', {
            'fields': ('referral_code', 'is_verified', 'vip_level', 'balance',
                      'email_notifications', 'sms_notifications', 'twofa_enabled',
                      'profile_picture', 'withdrawal_password'),
            'classes': ('wide',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        ('Create New User', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'full_name', 'phone_number',
                      'password1', 'password2', 'is_verified', 'vip_level', 'balance'),
        }),
    )

    readonly_fields = ('last_login', 'date_joined')

# UserProfile Admin
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_email', 'location', 'has_avatar', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'user__full_name', 'location')
    readonly_fields = ('created_at', 'updated_at')

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def has_avatar(self, obj):
        return format_html('<span style="color: green;">✓</span>' if obj.avatar else '<span style="color: gray;">✗</span>')
    has_avatar.short_description = 'Avatar'

# Withdrawal Admin
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_method', 'wallet_address', 'status', 'created_at', 'processed_at')
    list_filter = ('status', 'payment_method', 'created_at', 'processed_at')
    search_fields = ('user__username', 'user__email', 'wallet_address')
    actions = [approve_withdrawals, reject_withdrawals]
    list_per_page = 25

    def save_model(self, request, obj, form, change):
        if obj.status in ['completed', 'rejected'] and not obj.processed_at:
            obj.processed_at = timezone.now()
        super().save_model(request, obj, form, change)

# Invitation Admin
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'referee_email', 'referee_name', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('referrer__username', 'referrer__email', 'referee_email', 'referee_name')
    list_per_page = 25

# Task Admin
class TaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'task_type', 'earnings', 'status', 'created_at')
    list_filter = ('status', 'task_type', 'created_at')
    search_fields = ('user__username', 'user__email')
    list_per_page = 25

# Deposit Admin
class DepositAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_method', 'wallet_address', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('user__username', 'user__email', 'wallet_address')
    list_per_page = 25

# TermsAndConditions Admin
class TermsAndConditionsAdmin(admin.ModelAdmin):
    list_display = ('version', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('content', 'version')

class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_value', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('user__username', 'user__email')
    list_per_page = 25


class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'priority', 'status', 'created_at')
    list_filter = ('priority', 'status', 'created_at')
    search_fields = ('user__username', 'user__email', 'subject', 'message')
    list_per_page = 25

    # NEW: Product Admin (add this class)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'description', 'created_at')  # Adjust fields to your model
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    list_per_page = 25
    readonly_fields = ('created_at',)

# Register models
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Deposit, DepositAdmin)
admin.site.register(Withdrawal, WithdrawalAdmin)
admin.site.register(Invitation, InvitationAdmin)
admin.site.register(TermsAndConditions, TermsAndConditionsAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(SupportTicket, SupportTicketAdmin)
admin.site.register(Product, ProductAdmin)  # NEW: Add this line

