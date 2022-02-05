from django.db import models
from django.utils import timezone
from django.urls import reverse
import datetime
from datetime import timezone
# Create your models here.
class Project(models.Model):
    project_name = models.CharField(max_length=200, unique=True)

    def __str__(self):
      return f'{self.id}: {self.project_name}'

class Task(models.Model):

  COMPLETED = 'Completed'
  IN_PROGRESS = 'In progress'
  INPUT = [(COMPLETED, 'Completed'), (IN_PROGRESS, 'In progress')]

  name = models.CharField(max_length=200)
  description = models.CharField(max_length=200)
  project = models.ForeignKey('Project', on_delete=models.CASCADE)
  status = models.CharField(max_length=200, choices=INPUT)

  def __str__(self):
    return f'{self.id}: {self.name}'

class Timer(models.Model):
  task = models.ForeignKey(Task, on_delete=models.CASCADE)
  begin = models.CharField(max_length=200)
  end = models.CharField(max_length=200)
  duration = models.CharField(max_length=200)

  def get_absolute_url(self):
    return reverse('/tasks/<pk>/detail', kwargs={'pk': self.pk})

  def __str__(self):
    return f'{self.id}: {self.begin}: {self.end}'
