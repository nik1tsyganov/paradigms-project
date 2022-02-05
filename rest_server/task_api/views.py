from django.db.models.expressions import OrderBy
from django.urls.base import reverse_lazy
from .models import Task, Timer, Project
from rest_framework import viewsets, permissions
from .serializers import TaskSerializer, TimerSerializer, ProjectSerializer
from django.template.defaulttags import register
from django.views.generic import *
from django.urls import reverse
from .forms import TaskForm, TimerForm, ProjectForm
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseRedirect
from django.http import JsonResponse, Http404
from django.db import models
from django.forms import *
import calendar
import datetime
from collections import defaultdict

# Project views
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('id')
    serializer_class = ProjectSerializer

class ProjectListView(ListView):
    template_name = 'tasks/project_list.html'
    queryset = Project.objects.all().order_by('id')
    context_object_name = 'projects'

class ProjectCreateView(CreateView):
    model = Project
    template_name = 'tasks/project-create.html'
    form_class = ProjectForm

    def get_success_url(self):
        return '/projects'

class ProjectStatsView(DetailView):
    model = Project
    context_object_name = 'data'
    template_name = 'tasks/project_stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.get_object()
        context['tasks'] = self.get_object().task_set.all()
        t = TimeMetrics()
        context['weeks'] = t.get_totals_weeks(context['tasks'])
        context['months'] = t.get_totals_months(context['tasks'])
        return context

class AverageView(ListView):
    template_name = 'tasks/average.html'
    queryset = Project.objects.all().order_by('id')
    context_object_name = 'data'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.all().order_by('id')
        context['tasks'] = self.get_tasks(context['projects'])
        t = TimeMetrics()
        context['weeks'] = t.get_avgs_weeks(context['tasks'])
        context['months'] = t.get_avgs_months(context['tasks'])
        return context

    def get_tasks(self, projects):
        tasks = []
        for project in projects:
            tasks.extend(project.task_set.all())
        return tasks

class ProjectDetailView(DetailView):
    model = Project
    context_object_name = 'data'
    template_name = 'tasks/project_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.get_object()
        context['tasks'] = self.get_object().task_set.all()
        return context

class ProjectDeleteView(DeleteView):
    model = Project
    template_name = 'tasks/project_delete.html'

    def get_success_url(self):
        return '/projects'

# Task views
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by('id')
    serializer_class = TaskSerializer

class TaskListView(ListView):
    template_name = 'tasks/task_list.html'
    queryset = Task.objects.all().order_by('id')
    context_object_name = 'tasks'

class TaskDeleteView(DeleteView):
    model = Task
    template_name = 'tasks/task_delete.html'

    def get_success_url(self):
        return f"/projects/{self.kwargs['id']}/tasks"

class TaskCreateView(CreateView):
    model = Task
    template_name = 'tasks/task-create.html'
    form_class = TaskForm

    def form_valid(self, form):
        form.instance.task = Project.objects.get(pk=self.kwargs['pk'])
        form.save()
        return super(TaskCreateView, self).form_valid(form)

    def get_success_url(self):
        return f"/projects/{self.kwargs['pk']}/tasks"

class TaskDetailView(DetailView):
    model = Task
    context_object_name = 'data'
    template_name = 'tasks/task_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task'] = self.get_object()
        context['timers'] = self.get_object().timer_set.all()
        return context

class TaskUpdateView(UpdateView):
    model = Task
    template_name = 'tasks/task_update.html'
    form_class = TaskForm


    def get_initial(self):
        self.object = self.get_object()
        initial = {
            'name': self.object.name,
            'description': self.object.description,
            'project': self.object.project.project_name,
            'status': self.object.status
        }
        print(initial['project'])
        return initial

    def get_success_url(self):
        return f"/projects/{self.kwargs['id']}/tasks/"

# Timer views
class TimerCreateView(CreateView):
    model = Timer
    template_name = 'tasks/timer_create.html'
    form = TimerForm
    fields = ['begin', 'end']

    def form_valid(self, form):
        form.instance.task = Task.objects.get(pk=self.kwargs['pk'])
        form.save()
        return super(TimerCreateView, self).form_valid(form)

    def get_success_url(self):
        return f"/projects/{self.kwargs['id']}/tasks/{self.kwargs['pk']}/update/"

class TimerDetailView(DetailView):
    model=Task
    context_object_name = 'data'
    template_name = 'tasks/timer_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task'] = self.get_object()
        context['timers'] = self.get_object().timer_set.all()
        t = TimeMetrics()
        context['weeks'] = t.get_weeks(context['timers'])
        context['months'] = t.get_months(context['timers'])
        return context

class TimerUpdateView(UpdateView):
    model = Timer
    template_name = 'tasks/timer_update.html'
    form = TimerForm
    fields = ['begin', 'end']
    
    def form_valid(self, form):
        form.instance.task = Task.objects.get(pk=self.kwargs['id'])
        form.instance.task.timer_set.get(id=self.kwargs['pk']).save()
        return super(TimerUpdateView, self).form_valid(form)

    def get_initial(self):
        if self.request.method == 'GET':
            form = TimerForm
            self.object = Timer.objects.get(id=self.kwargs['pk'])
            print(self.object.begin)
            parse_begin = datetime.datetime.strptime(self.object.begin, '%m-%d-%Y %H:%M:%S.%f').strftime('%Y-%m-%dT%H:%M:%S')
            parse_end = datetime.datetime.strptime(self.object.end, '%m-%d-%Y %H:%M:%S.%f').strftime('%Y-%m-%dT%H:%M:%S')
            print(parse_begin, parse_end)
            initial_data = {
                'begin': parse_begin,
                'end': parse_end
            }
            print(initial_data)
            return initial_data
        else:
            return {}
        

    def get_success_url(self):
        return f"/projects/{self.kwargs['project']}/tasks/{self.kwargs['id']}/update/"

class TimerDeleteView(DeleteView):
    model = Timer
    template_name = 'tasks/confirm-delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = Timer.objects.get(id=self.kwargs['pk'])
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return f"/projects/{self.kwargs['project']}/tasks/{self.kwargs['id']}/update/"

class TimerViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by('id')
    serializer_class = TaskSerializer

class TimerListView(ListView):
    template_name = 'tasks/timer_list.html'
    queryset = Task.objects.all().order_by('id')
    context_object_name = 'tasks'

class TimeMetrics:
    def get_totals_weeks(self, tasks):
        timers = []
        for task in tasks:
            timers.extend(task.timer_set.all())
        print(self.get_weeks(timers))
        return self.get_weeks(timers)

    def get_totals_months(self, tasks):
        timers = []
        for task in tasks:
            timers.extend(task.timer_set.all())
        print(self.get_months(timers))
        return self.get_months(timers)

    def get_avgs_weeks(self, tasks):
        timers = []
        for task in tasks:
            timers.extend(task.timer_set.all())
        
        weeks = self.get_weeks(timers)
        for week, s in weeks.items():
            nums = [int(i) for i in s.split() if i.isdigit()]
            seconds = nums[0]*3600 + nums[1]*60 + nums[2]
            avg_seconds = seconds / len(tasks)
            hours = int(avg_seconds//3600)
            minutes = int(avg_seconds//60 % 60)
            seconds = int(avg_seconds % 60)
            weeks[week] = f'{hours} hours, {minutes} minutes, {seconds} seconds'
        return weeks
         

    def get_avgs_months(self, tasks):
        timers = []
        for task in tasks:
            timers.extend(task.timer_set.all())
        
        months = self.get_months(timers)
        for month, s in months.items():
            nums = [int(i) for i in s.split() if i.isdigit()]
            seconds = nums[0]*3600 + nums[1]*60 + nums[2]
            avg_seconds = seconds / len(tasks)
            hours = int(avg_seconds//3600)
            minutes = int(avg_seconds//60 % 60)
            seconds = int(avg_seconds % 60)
            months[month] = f'{hours} hours, {minutes} minutes, {seconds} seconds'
        return months

    def get_weeks(self, timers):
        ''' Returns the time worked for each week of the task '''
        times = list(map(
            lambda t: (datetime.datetime.strptime(t.begin,'%m-%d-%Y %H:%M:%S.%f'), 
                       datetime.datetime.strptime(t.end,'%m-%d-%Y %H:%M:%S.%f')), 
                       timers))

        week_values = defaultdict(list)
        for time in times:
            week_year = f'{time[0].isocalendar().week}, {time[0].isocalendar().year}'
            week_values[week_year].append(time)

        return self.get_time_worked_per_val(week_values, "Week")

    def get_months(self, timers):
        ''' Returns the time worked for each month of the task '''
        times = list(map(
            lambda t: (datetime.datetime.strptime(t.begin,'%m-%d-%Y %H:%M:%S.%f'), 
                       datetime.datetime.strptime(t.end,'%m-%d-%Y %H:%M:%S.%f')), 
                       timers))

        month_values = defaultdict(list)
        for time in times:
            month_year = f'{time[0].month}, {time[0].isocalendar().year}'
            month_values[month_year].append(time)
        return self.get_time_worked_per_val(month_values, "Month")

    def get_time_worked_per_val(self, values, s):
        ''' Helper function to get the total time worked for a given input 
        
        values is a dictionary mapping a string of the form (month, year) or (week, year)
        to a tuple datetimes representing start and end. The function iterates over this 
        dictionary and returns another dict which maps those strings to the total time 
        worked across potentially several tasks in the same week/month.
        '''
        time_worked_per_val = {}
        for val, times in values.items():
            time_worked = list(map(lambda a: (abs(a[1] - a[0])), times))
            time_worked = sum(time_worked, datetime.timedelta(0, 0))

            # calculate seconds, hours, minutes worked for task
            seconds = time_worked.total_seconds()
            hours = int(seconds//3600)
            minutes = int(seconds//60 % 60)
            seconds = int(seconds % 60)
            time_worked_per_val[val] = f'{hours} hours, {minutes} minutes, {seconds} seconds'
            s_val, year = val.split(',')
            # update key for a more readable string
            if s == 'Month':
                months = {index : month for index, month in enumerate(calendar.month_abbr) if month}
                key = f'{months[int(s_val)]}. {year}'
            else:
                d = f'{year}-W{s_val}'[1:]
                key = f"Week of {datetime.datetime.strptime(d + '-1', '%G-W%V-%u')}"
                key = key[:-9]
            time_worked_per_val[key] = time_worked_per_val.pop(val)

        return time_worked_per_val
