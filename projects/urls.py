from django.urls import path

from .views import ProjectListView, ProjectCreateView, ProjectDetailView

urlpatterns = [
    path('<uuid:pk>/', ProjectDetailView.as_view(), name='project'),
    path('new/', ProjectCreateView.as_view(), name='project_new'),
    path('', ProjectListView.as_view(), name='projects'),
]
