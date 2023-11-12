from django.urls import path

from .views import ProjectCreateView, project_list_view, project_detail_view, project_manage_view

urlpatterns = [
    path('<uuid:pk>/manage', project_manage_view, name='manage_project'),
    path('<uuid:pk>/', project_detail_view, name='project'),
    path('new/', ProjectCreateView.as_view(), name='project_new'),
    path('', project_list_view, name='projects'),
]
