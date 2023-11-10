from django.urls import path

from .views import upload_file_view, project_files_list

urlpatterns = [
    path('upload/', upload_file_view, name='upload_file'),
    path('', project_files_list, name='project_files'),
]
