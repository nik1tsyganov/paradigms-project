from .models import Task, Timer, Project
from rest_framework import serializers

class ProjectSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = Project
    fields = ['project_name']

class TaskSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = Task
    fields = ['id', 'name', 'description', 'project', 'status']

class TimerSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = Timer
    fields = ['task', 'begin', 'end']
