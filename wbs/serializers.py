from rest_framework import serializers

from projects.models import ProjectSharedFiles
from wbs.models import TimeCard, Wbs, WbsSharedFiles, WeekTimeCard
from users.serializers import UserDetailSerializer, UserDetailSerializer2
from projects.serializers import ProjectDetailsForWbsSerializer, ProjectDetailsSerializer, DocumentListSerializer
from django.utils import timezone


class CreateWbsSerializer(serializers.ModelSerializer):
    date_created = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    date_updated = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = Wbs
        fields = (
            'id',
            'project',
            'work_package_number',
            'assignee',
            'reporter',
            'title',
            'description',
            'start_date',
            'end_date',
            'hours_worked',
            'status',
            'progress',
            'comments',
            'deliverable',
            'date_created',
            'date_updated'
        )


class WbsDetailsSerializer(serializers.ModelSerializer):
    reporter = UserDetailSerializer()
    assignee = UserDetailSerializer()
    project = ProjectDetailsForWbsSerializer()
    files = serializers.SerializerMethodField()

    def get_files(self,obj):
        return WbsFileSerializer(WbsSharedFiles.objects.filter(wbs_id=obj.id), many=True).data
        # return DocumentListSerializer(ProjectSharedFiles.objects.filter(work_package_number=obj.project.work_package_number),many=True).data

    class Meta:
        model = Wbs
        fields = (
            'id',
            'project',
            'assignee',
            'reporter',
            'title',
            'description',
            'start_date',
            'end_date',
            'hours_worked',
            'files',
            'status',
            'progress',
            'comments',
            'deliverable',
            'date_created',
            'date_updated'
        )


class WbsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wbs
        fields = (
            'id',
            'project',
            'assignee',
            'title',
            'description',
            'start_date',
            'end_date',
            'status',
            'progress',
            'comments',
            'deliverable',
            'date_updated'
        )

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.status = validated_data.get('status', instance.status)
        instance.progress = validated_data.get('progress', instance.progress)
        instance.comments = validated_data.get('comments', instance.comments)
        instance.deliverable = validated_data.get('deliverable', instance.deliverable)
        instance.date_updated = validated_data.get('date_updated', timezone.now)
        instance.save()
        return instance


class WbsStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wbs
        fields = (
            'id',
            'status',
            'date_updated'
        )

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.date_updated = validated_data.get('date_updated', timezone.now)
        instance.save()
        return instance


class CreateTimeCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeCard
        fields = (
            'id',
            'project',
            'wbs',
            'time_type',
            'submitted',
            'time_card_assignee',
            'actual_work_done',
            'hours_today',
            'date_created',
            'date_updated'
        )


class TimeCardDetailsSerializer(serializers.ModelSerializer):
    time_card_assignee = UserDetailSerializer()
    project = ProjectDetailsForWbsSerializer()
    wbs = WbsDetailsSerializer()

    class Meta:
        model = TimeCard
        fields = (
            'id',
            'project',
            'wbs',
            'time_type',
            'submitted',
            'time_card_assignee',
            'actual_work_done',
            'hours_today',
            'date_created',
            'date_updated'
        )


class WbsWiseTimeCardListSerializer(serializers.ModelSerializer):
    time_card_assignee = UserDetailSerializer()
    project = ProjectDetailsForWbsSerializer()

    class Meta:
        model = TimeCard
        fields = (
            'id',
            'project',
            'time_type',
            'submitted',
            'time_card_assignee',
            'actual_work_done',
            'hours_today',
            'date_created',
            'date_updated'
        )


class TimecardUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeCard
        fields = (
            'id',
            'actual_work_done',
            'time_type',
            'hours_today',
            'date_updated'
        )

    def update(self, instance, validated_data):
        instance.actual_work_done = validated_data.get('actual_work_done', instance.time_type)
        instance.time_type = validated_data.get('time_type', instance.time_type)
        instance.hours_today = validated_data.get('hours_today', instance.hours_today)
        instance.date_updated = validated_data.get('date_updated', timezone.now)
        instance.save()
        return instance


class WbsFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = WbsSharedFiles
        fields = (
            'wbs_id',
            'file',
            'upload_by'
        )


class SubmitWeeklyTimeCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeekTimeCard
        fields = (
            'id',
            'employee',
            'week_start',
            'week_end',
            'total_hours',
            'approved_by',
            'submitted',
            'submitted_by',
            'pdf_file',
            'date_created',
            'date_updated'
        )


class UpdateWeeklyTimeCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeekTimeCard
        fields = (
            'id',
            'employee',
            'week_start',
            'week_end',
            'total_hours',
            'approved_by',
            'submitted',
            'submitted_at',
            'submitted_by',
            'pdf_file',
            'date_created',
            'date_updated'
        )

        def update(self, instance, validated_data):
            instance.pdf_file = validated_data.get('pdf_file', instance.pdf_file)
            instance.total_hours = validated_data.get('total_hours', instance.total_hours)
            instance.date_updated = validated_data.get('date_updated', timezone.now)
            instance.submitted_by = validated_data.get('user', instance.submitted_by)
            instance.save()
            return instance


class UserSubmitWeeklyTimeCardSerializer(serializers.ModelSerializer):
    employee = UserDetailSerializer2()

    class Meta:
        model = WeekTimeCard
        fields = (
            'id',
            'employee',
            'week_start',
            'week_end',
            'total_hours',
            'approved_by',
            'submitted',
            'submitted_at',
            'submitted_by',
            'pdf_file',
            'date_created',
            'date_updated'
        )
