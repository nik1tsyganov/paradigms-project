"""rest_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from task_api.models import Task, Timer, Project
from task_api import views

app_name = 'tasks'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='project_view'),
    path('<pk>/project_stats/', views.ProjectStatsView.as_view(), name='statistics'),
    path('projects_create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('<pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    path('<pk>/tasks/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('average/', views.AverageView.as_view(), name='statistics'),
    path('<id>/tasks/<pk>/detail/', views.TaskDetailView.as_view(), name='detail'),
    path('<id>/tasks/<pk>/delete/', views.TaskDeleteView.as_view(), name='delete_task'),
    path('<id>/tasks/<pk>/update/', views.TaskUpdateView.as_view(), name='update'),
    path('<pk>/tasks/create/', views.TaskCreateView.as_view(), name='create'),
    path('<project>/tasks/<id>/update/<pk>/delete', views.TimerDeleteView.as_view(), name='deletetime'),
    path('<id>/tasks/<pk>/new_time', views.TimerCreateView.as_view(), name='timeentry'),
    path('<id>/tasks/<pk>/entries', views.TimerDetailView.as_view(), name='timeentries'),
    path('<project>/tasks/<id>/update/<pk>/time_update', views.TimerUpdateView.as_view(), name='timeupdate'),
    path('api/', include('rest_framework.urls', namespace='rest_framework'))
]
