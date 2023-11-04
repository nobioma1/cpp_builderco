from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'identifier', 'description', 'start_date', 'end_date', 'status', 'type', 'created_at',
                    'location', 'updated_at')
    search_fields = ('name', 'status', 'identifier')
    list_filter = ('status', 'created_at', 'start_date', 'end_date')
