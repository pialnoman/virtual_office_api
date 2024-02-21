from rest_framework import serializers
from evms.models import Evms
from users.serializers import UserDetailSerializer
from projects.serializers import ProjectDetailsSerializer
from django.utils import timezone


class CreateEvmsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evms
        fields = (
            'project',
            'work_package_number',
            'earned_value',
            'actual_cost',
            'estimate_at_completion',
            'estimate_to_completion',
            'variance_at_completion',
            'budget_at_completion',
            'date_created',
            'date_updated'
        )


class EvmsDetailsSerializer(serializers.ModelSerializer):
    project = ProjectDetailsSerializer()

    class Meta:
        model = Evms
        fields = (
            'id',
            'project',
            'work_package_number',
            'earned_value',
            'actual_cost',
            'estimate_at_completion',
            'estimate_to_completion',
            'variance_at_completion',
            'budget_at_completion',
            'date_created',
            'date_updated'
        )


class EvmsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evms
        fields = (
            'earned_value',
            'actual_cost',
            'estimate_at_completion',
            'estimate_to_completion',
            'variance_at_completion',
            'budget_at_completion',
            'date_updated'
        )

    def update(self, instance, validated_data):
        instance.earned_value = validated_data.get('earned_value', instance.earned_value)
        instance.actual_cost = validated_data.get('actual_cost', instance.actual_cost)
        instance.estimate_at_completion = validated_data.get('estimate_at_completion', instance.estimate_at_completion)
        instance.estimate_to_completion = validated_data.get('estimate_to_completion', instance.estimate_to_completion)
        instance.variance_at_completion = validated_data.get('variance_at_completion', instance.variance_at_completion)
        instance.budget_at_completion = validated_data.get('budget_at_completion', instance.budget_at_completion)
        instance.date_updated = timezone.now().date()
        instance.save()
        return instance