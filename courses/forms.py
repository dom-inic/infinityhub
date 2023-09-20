from django import forms 
from django.forms.models import inlineformset_factory
from . models import Course, Topic

TopicFormSet = inlineformset_factory(
    Course,
    Topic,
    fields=['title', 'description'],
    extra=2,
    can_delete=True
    )