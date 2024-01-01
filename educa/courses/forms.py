from django import forms
from .models import Course, Module
from django.forms.models import inlineformset_factory

ModuleFormSet = inlineformset_factory(Course, Module,  # связанные объекты
                                      fields=['title', 'description'],
                                      extra=2, can_delete=True)  # количество форм и возможность удалять
