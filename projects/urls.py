from django.urls import path

from .views import project_list_view, ProjectCreateView, project_detail_view

urlpatterns = [
    path('<uuid:pk>/', project_detail_view, name='project'),
    path('new/', ProjectCreateView.as_view(), name='project_new'),
    path('', project_list_view, name='projects'),
]
