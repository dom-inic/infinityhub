from rest_framework import serializers
from ..models import Subject, Course, Topic, Content

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'title', 'slug']

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['order', 'title', 'description']

class CourseSerializer(serializers.ModelSerializer):
    topics = TopicSerializer(many=True, read_only=True)
    class Meta:
        model = Course
        fields = ['id', 'subject', 'title', 'slug', 'overview', 'created', 'owner', 'topics']

class ItemRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return value.render()
    
class ContentSerializer(serializers.ModelSerializer):
    item = ItemRelatedField(read_only= True)

    class Meta:
        model = Content
        fields = ['order', 'item']

class TopicWithContentsSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True)

    class Meta:
        model = Topic
        fields = ['order', 'title', 'description', 'contents']

class CourseWithContentsSerializer(serializers.ModelSerializer):
    topics = TopicWithContentsSerializer(many=True)

    class Meta:
        model = Course
        fields = ['id', 'subject', 'title', 'slug', 'overview', 'created', 'owner', 'topics']
