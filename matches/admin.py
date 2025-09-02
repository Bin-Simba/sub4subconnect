from django.contrib import admin
from .models import Connection

@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('from_user__first_name', 'from_user__last_name', 'to_user__first_name', 'to_user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Connection Details', {
            'fields': ('from_user', 'to_user', 'status', 'message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
