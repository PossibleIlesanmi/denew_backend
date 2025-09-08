from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.utils.safestring import mark_safe  # For safe HTML
from .models import User, UserProfile, Task, Deposit, Withdrawal, Invitation, TermsAndConditions, Portfolio, SupportTicket, Product

# Admin Actions (existing ones unchanged)
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

# NEW: Bulk action for confirming deposits (triggers signal for balance update)
@admin.action(description='Confirm selected deposits (updates user balances)')
def confirm_deposits(modeladmin, request, queryset):
    updated = 0
    for deposit in queryset:
        if deposit.status == 'pending':
            deposit.status = 'confirmed'
            deposit.save()  # This triggers the post_save signal to update balance
            updated += 1
        elif deposit.status == 'rejected':
            # Optional: Refund if previously rejected, but skip for now as per app logic
            pass
    modeladmin.message_user(request, f'Successfully confirmed {updated} deposits. User balances updated automatically.', level='success')

# Inline for UserProfile (unchanged)
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Information'
    fields = ('avatar', 'bio', 'location', 'website')

# Custom User Admin (unchanged)
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

# UserProfile Admin (unchanged)
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

# Withdrawal Admin (unchanged)
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

# Invitation Admin (unchanged)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'referee_email', 'referee_name', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('referrer__username', 'referrer__email', 'referee_email', 'referee_name')
    list_per_page = 25

# Task Admin (unchanged)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'task_type', 'earnings', 'status', 'created_at')
    list_filter = ('status', 'task_type', 'created_at')
    search_fields = ('user__username', 'user__email')
    list_per_page = 25

# UPDATED: Deposit Admin (enhanced for auto-balance and bulk confirm)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'amount', 'payment_method', 'wallet_address', 'status', 'created_at', 'user_balance_after')  # Added user_link and user_balance_after
    list_filter = ('status', 'payment_method', 'created_at')  # Existing filters
    search_fields = ('user__username', 'user__email', 'wallet_address')
    actions = [confirm_deposits]  # Add the new bulk confirm action
    list_per_page = 25

    # NEW: Clickable user link
    def user_link(self, obj):
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'

    # NEW: Show user's balance after this deposit (for quick reference)
    def user_balance_after(self, obj):
        if obj.status == 'confirmed':
            return f"${(obj.user.balance):.2f}"  # Assumes signal updated it
        return "Pending"
    user_balance_after.short_description = 'User Balance (After)'

    # UPDATED: Override save_model to default status='confirmed' on creation
    def save_model(self, request, obj, form, change):
        if not change:  # On creation (not edit)
            if not obj.status or obj.status == 'pending':  # Default to confirmed for admin adds
                obj.status = 'confirmed'
        super().save_model(request, obj, form, change)

    # NEW: Form fields for add/edit (make status prominent)
    fields = ('user', 'amount', 'payment_method', 'wallet_address', 'status')

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

# TermsAndConditions Admin (unchanged)
class TermsAndConditionsAdmin(admin.ModelAdmin):
    list_display = ('version', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('content', 'version')

# Portfolio Admin (unchanged)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_value', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('user__username', 'user__email')
    list_per_page = 25

# SupportTicket Admin (unchanged)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'priority', 'status', 'created_at')
    list_filter = ('priority', 'status', 'created_at')
    search_fields = ('user__username', 'user__email', 'subject', 'message')
    list_per_page = 25

# Product Admin (unchanged from your version)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'price', 'is_combined')
    list_filter = ('is_combined',)
    search_fields = ('name', 'icon')
    list_per_page = 25
    
    def has_add_permission(self, request):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True

# Register models (unchanged)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Deposit, DepositAdmin)
admin.site.register(Withdrawal, WithdrawalAdmin)
admin.site.register(Invitation, InvitationAdmin)
admin.site.register(TermsAndConditions, TermsAndConditionsAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(SupportTicket, SupportTicketAdmin)
admin.site.register(Product, ProductAdmin)