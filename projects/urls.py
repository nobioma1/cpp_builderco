from django.urls import path

from .views import ProjectListView, ProjectCreateView

urlpatterns = [
    path('new/', ProjectCreateView.as_view(), name='project_new'),
    path('', ProjectListView.as_view(), name='projects'),
]
