from django.urls import path, include
from rest_framework import routers
from . import views

app_name='courses'

router = routers.DefaultRouter()
router.register('courses', views.CourseViewset)

urlpatterns = [
    path('', include(router.urls)),
    path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
    path('subjects/<pk>/', views.SubjectDetailView.as_view(), name='subject_detail'), 
    # path('course/<pk>/enroll/', views.CourseEnrollView.as_view(), name="course_enroll")
]
