from django.urls import path

from .views import list_members_view

urlpatterns = [
    path('', list_members_view, name='project_members'),
]
