from django.urls import path

from .views import upload_file_view, project_files_list, list_file_versions

urlpatterns = [
    path('<uuid:file_id>/versions', list_file_versions, name='file_versions'),
    path('upload/', upload_file_view, name='upload_file'),
    path('', project_files_list, name='project_files'),
]
