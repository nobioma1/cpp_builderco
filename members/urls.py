from django.urls import path

from .views import list_members_view, add_members_view

urlpatterns = [
    path('add/', add_members_view, name='add_member'),
    path('', list_members_view, name='project_members'),
]
