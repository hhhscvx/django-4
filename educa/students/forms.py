from django import forms
from courses.models import Course


class CourseEnrollForm(forms.Form):  # форма для зачисления, будет заполняться сама (courses/views) и будет невидимой
    course = forms.ModelChoiceField(  # выбор объекта из модели
        queryset=Course.objects.all(),  # набор для выбора (все курсы)
        widget=forms.HiddenInput)
