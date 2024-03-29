
from pickle import NONE
from typing import Any
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.detail import DetailView
from django.forms.models import modelform_factory
from django.apps import apps
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.db.models import Count
from django.core.cache import cache
from . models import Course, Topic,Content, Subject
from . forms import TopicFormSet
from students.forms import CourseEnrollForm

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
        
        # retrive model name and id from query parameters 
        model_name = request.GET.get('model_name')
        id = request.GET.get('id')
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user 
            obj.save()
            if not id:
                # new content 
                Content.objects.create(topic=self.topic, item=obj)
            return redirect('topic_content_list', self.topic.id) # type: ignore
        return self.render_to_response({'form': form, 'object': self.obj})

class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content, id=id, topic__course__owner=request.user)
        topic = content.topic 
        content.item.delete()# type: ignore
        content.delete()
        return redirect('topic_content_list', topic.id) # type: ignore

class TopicContentList(TemplateResponseMixin, View):
    template_name = 'courses/manage/topic/content_list.html'

    def get(self, request, topic_id):
        topic = get_object_or_404(Topic, id=topic_id, course__owner=request.user)
        return self.render_to_response({'topic': topic})
    
class TopicOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():# type: ignore
            Topic.objects.filter(id=id, course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})

class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():# type: ignore
            Content.objects.filter(id=id, topic__course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})
    
class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'courses/course/list.html'

    def get(self, request, subject=None):
        subjects = cache.get('all_subjects')
        if not subjects:
            subjects = Subject.objects.annotate(total_courses=Count('courses'))
            cache.set('all_subjects', subjects)
        all_courses = Course.objects.annotate(total_topics = Count('topics'))

        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            key = f'subject_{subject.id}_courses' # type: ignore
            courses = cache.get(key)
            if not courses:
                courses = all_courses.filter(subject=subject)
                cache.set(key, courses)
        else:
            courses = cache.get('all_courses')
            if not courses:
                courses = all_courses
                cache.set('all_courses', courses)
        return self.render_to_response({
            'subjects': subjects,
            'subject': subject,
            'courses': courses
            })

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(initial={'course':self.object}) # type: ignore
        return context
