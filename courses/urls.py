from django.urls import path
from . import views

urlpatterns = [
    path('mine/', views.ManageCourseListView.as_view(), name='manage_course_list'),
    path('create/', views.CourseCreateView.as_view(), name="course_create"), 
    path('<pk>/edit/', views.CourseUpdateView.as_view(), name='course_edit'), 
    path('<pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),
    path('<pk>/topic/', views.CourseTopicUpdateView.as_view(), name='course_topic_update'),
    path(
        'topic/<int:topic_id>/content/<model_name>/create/',
        views.ContentCreateUpdateView.as_view(),
        name="topic_content_create"
        ),
    path(
        'topic/<int:topic_id>/content/model_name/<id>/',
        views.ContentCreateUpdateView.as_view(),
        name='topic_content_update'
        ),
]
