from django import forms
from .models import Task, Timer, Project
from django.db import models
from django.utils import timezone
from django.utils.timezone import utc

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_name']

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'project', 'status']

class TimerForm(forms.ModelForm):
    model = Timer
    begin = forms.DateTimeField(widget=forms.HiddenInput())
    end = forms.DateTimeField(widget=forms.HiddenInput())

    def get_initial(self):
        self.object = self.get_object()
        print(vars(self.object))
        initial = {
            'begin': self.object.begin,
            'end': self.object.end,
        }
        print(initial)
        return initial


    def clean(self):
        cleaned_data = super(TimerForm, self).clean()
        begin = cleaned_data.get('begin')
        end = cleaned_data.get('end')

        if not begin and not end:
            raise forms.ValidationError('Bad')
