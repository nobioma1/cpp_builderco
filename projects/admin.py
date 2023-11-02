from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'status', 'created_at', 'updated_at')
    search_fields = ('project_name', 'status')
    list_filter = ('status', 'created_at')
