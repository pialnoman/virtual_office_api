from users.serializers import UserDetailSerializer
from rest_framework import serializers
from meetings.models import Meetings
from projects.serializers import ProjectDetailsSerializer
from django.utils import timezone


class CreateMeetingsSerializer(serializers.ModelSerializer):
    # start_time = serializers.DateTimeField(format="%Y-%m-%d %I:%M:%S %p")
    duration = serializers.IntegerField(required=False)
    class Meta:
        model = Meetings
        fields = (
            'room_id',
            'room_name',
            'participant',
            'type',
            'agenda',
            'project',
            'comments',
            'start_time',
            'duration',
            'host'
            # 'date_created',
            # 'date_updated'
        )


class MeetingsDetailsSerializer(serializers.ModelSerializer):
    # project = ProjectDetailsSerializer()
    host = UserDetailSerializer()
    start_time = serializers.DateTimeField(format="%Y-%m-%d %I:%M:%S %p", read_only=True)
    class Meta:
        model = Meetings
        fields = (
            'id',
            'room_id',
            'room_name',
            'participant',
            'project',
            'type',
            'medium',
            'agenda',
            'comments',
            'start_time',
            'end_time',
            'duration',
            'host',
            'date_created',
            'date_updated'
        )


class MeetingsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meetings
        fields = (
            'room_id',
            'room_name',
            'participant',
            'project',
            'agenda',
            'comments',
            'start_time',
            'end_time',
            'duration',
            'host',
            'date_updated'
        )

    def update(self, instance, validated_data):
        instance.room_id = validated_data.get('room_id', instance.room_id)
        instance.participant = validated_data.get('participant', instance.participant)
        instance.project = validated_data.get('project', instance.project)
        instance.agenda = validated_data.get('agenda', instance.agenda)
        instance.comments = validated_data.get('comments', instance.comments)
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.end_time = validated_data.get('end_time', instance.end_time)
        instance.host = validated_data.get('host', instance.host)
        instance.date_updated = validated_data.get('date_updated', timezone.now)
        instance.save()
        return instance
