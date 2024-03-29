from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.shortcuts import render
from django.template.loader import render_to_string
from .fields import OrderField

# Create your models here.

class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self) -> str:
        return self.title

class Course(models.Model):
    owner = models.ForeignKey(User, related_name="courses_created",on_delete=models.CASCADE)
    students = models.ManyToManyField(User, related_name='courses_joined', blank=True)
    subject = models.ForeignKey(Subject, related_name="courses", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self) -> str:
        return self.title
    
class Topic(models.Model):
    course = models.ForeignKey(Course, related_name='topics', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['course']) # type: ignore

    class Meta:
        ordering = ['order']

    def __str__(self) -> str:
        return f'{self.order}. {self.title}'
    
class Content(models.Model):
    topic  = models.ForeignKey(Topic, related_name='contents', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,
                                    on_delete=models.CASCADE,
                                    limit_choices_to={'model__in': (
                                        'text',
                                        'video',
                                        'image',
                                        'file'
                                    )}
                                    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['topic']) # type: ignore

    class Meta:
        ordering = ['order']


# abstract model 
class ItemBase(models.Model):
    # reverse relationship for child models i.e text_related,video_related .. 
    owner = models.ForeignKey(User, related_name='%(class)s_related', on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.title
    
    def render(self):
        return render_to_string(
            f'courses/content/{self._meta.model_name}.html', {'item':self}
            )
    
class Text(ItemBase):
    content = models.TextField()

class File(ItemBase):
    file = models.FileField(upload_to='files')

class Image(ItemBase):
    file = models.FileField(upload_to='images')

class Video(ItemBase):
    url = models.URLField()
