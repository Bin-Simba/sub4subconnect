from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from allauth.socialaccount.admin import SocialAccountAdmin
from allauth.socialaccount.models import SocialAccount
from .models import User, AppUser

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin users management (staff and superusers only)"""
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    def get_queryset(self, request):
        """Only show staff and superuser accounts in Admin section"""
        qs = super().get_queryset(request)
        return qs.filter(is_staff=True)
    
    class Meta:
        verbose_name = "Admin User"
        verbose_name_plural = "Admin Users"

# Unregister the default SocialAccount admin
admin.site.unregister(SocialAccount)

# Create custom admin for AppUser that appears in Social Accounts section
@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    """App users management - appears in Social Accounts section"""
    list_display = ('email', 'first_name', 'last_name', 'social_url', 'youtube_url', 'created_at')
    list_filter = ('created_at', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'social_url', 'youtube_url')
    ordering = ('-created_at',)
    readonly_fields = ('password_hash', 'created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('email', 'first_name', 'last_name', 'is_active')
        }),
        ('Social Accounts', {
            'fields': ('social_url', 'youtube_url'),
            'description': 'User\'s social media profile links'
        }),
        ('System Information', {
            'fields': ('password_hash', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Re-register SocialAccount with custom admin that shows related AppUser data
@admin.register(SocialAccount)
class CustomSocialAccountAdmin(SocialAccountAdmin):
    """Enhanced Social Account admin showing app user data"""
    list_display = ('user', 'provider', 'uid', 'get_app_user_email', 'date_joined')
    list_filter = ('provider', 'date_joined')
    search_fields = ('uid', 'user__email', 'extra_data')
    
    def get_app_user_email(self, obj):
        """Get email from related AppUser if exists"""
        try:
            # Look for AppUser with same email
            from .models import AppUser
            app_user = AppUser.objects.filter(email=obj.extra_data.get('email', '')).first()
            return app_user.email if app_user else obj.extra_data.get('email', 'N/A')
        except:
            return 'N/A'
    get_app_user_email.short_description = 'App User Email'
