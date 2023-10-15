from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .. models  import Subject, Course, Content
from . serializers import CourseSerializer, SubjectSerializer, CourseWithContentsSerializer
from courses.api import serializers
from . permissions import IsEnrolled


class SubjectListView(generics.ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

class SubjectDetailView(generics.RetrieveAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

# class CourseEnrollView(APIView):
#     authentication_classes = BasicAuthentication
#     permission_classes = (IsAuthenticated)
#     def post(self, request, pk, format=None):
#         course = get_object_or_404(Course, pk=pk)
#         course.students.add(request.user)
#         return Response({'enrolled': True})
    
class CourseViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    @action(
        detail=True,
        methods=['post'],
        authentication_classes = [BasicAuthentication], 
        permission_classes = [IsAuthenticated]
        )
    def enroll(self, request, *args, **kwargs):
        course = self.get_object()
        course.students.add(request.user)
        return Response({'enrolled': True})
    
    @action(detail=True, 
            methods=['get'],
            serializer_class=CourseWithContentsSerializer,
            authentication_classes = [BasicAuthentication],
            permission_classes = [IsAuthenticated, IsEnrolled]
            )
    def contents(self, request, *args,**kwargs):
        return self.retrieve(request, *args, **kwargs)
    

