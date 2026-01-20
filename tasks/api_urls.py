from django.urls import path
from .views import task_detail_api, task_list_api

urlpatterns=[
    path("tasks/",task_list_api,name="api_tasks"),
    path("tasks/<int:task_id>", task_detail_api, name="api_task_detail"),
]