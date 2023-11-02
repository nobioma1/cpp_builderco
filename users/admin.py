from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'date_joined', "is_staff", 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_active', 'date_joined', "is_staff")
