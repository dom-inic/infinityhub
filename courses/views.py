
from pickle import NONE
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.base import TemplateResponseMixin, View
from django.forms.models import modelform_factory
from django.apps import apps
from . models import Course, Topic,Content
from . forms import TopicFormSet

class OwnerMixin(object):

    def get_queryset(self):
        qs = super().get_queryset() # type: ignore
        return qs.filter(owner=self.request.user) # type: ignore
    
class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user # type: ignore
        return super().form_valid(form) # type: ignore
    
class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
    # queryset  = object_list
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')

class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'

class ManageCourseListView(OwnerCourseMixin,ListView):
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.views_courses'

class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'

class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'

class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'

class CourseTopicUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/topic/formset.html'
    course = None

    def get_formset(self, data=None):
        return TopicFormSet(instance=self.course, data=data)
    
    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course,id=pk,owner=request.user)
        return super().dispatch(request, pk)
    
    def get(self, request,*args, **kwargs):
        formset= self.get_formset()
        return self.render_to_response({'course': self.course, 'formset': formset})
    
    def post(self,request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save() 
            return redirect('manage_course_list')
        return self.render_to_response({'course': self.course, 'formset': formset})
        
class ContentCreateUpdateView(TemplateResponseMixin, View):
    topic = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'image', 'video', 'file']:
            return apps.get_model(app_label='courses', model_name=model_name)
        return None
    
    def get_form(self,model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner',
                                                'order',
                                                'created',
                                                'updated'
                                                ])
        return Form(*args, **kwargs)
    
    def dispatch(self,request,topic_id, model_name, id=None):
        self.topic = get_object_or_404(Topic, id=topic_id,course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model, id=id,owner=request.user) # type: ignore
        return super().dispatch(request,topic_id,model_name,id)
    
    def get(self,request, topic_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})
    
    def post(self, request, topic_id, model_name, id=None):
        form = self.get_form(self.model, 
                            instance = self.obj, 
                            data = request.POST,
                            files = request.FILES
                            )
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user 
            obj.save()
            if not id:
                # new content 
                Content.objects.create(topic=self.topic, item=obj)
            return redirect('topic_content_list', self.topic.id) # type: ignore
        return self.render_to_response({'form': form, 'object': self.obj})
