from rest_framework import serializers
from organizations.models import Designation, Slc, DmaCalender, HolidayCalender, HourType, Company, Department


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'id',
            'name',
            'details',
        )


class DepartmentSerializer(serializers.ModelSerializer):
    company = CompanySerializer()

    class Meta:
        model = Department
        fields = (
            'id',
            'name',
            'details',
            'company',
            'parent',
        )


class DesignationSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer()

    class Meta:
        model = Designation
        fields = (
            'id',
            'name',
            'details',
            'department',
            'parent',
        )


class SlcSerializer(serializers.ModelSerializer):
    slc = DesignationSerializer()

    class Meta:
        model = Slc
        fields = (
            'id',
            'employee',
            'monthly_rate',
            'hourly_rate',
            'ep',
            'planned_hours',
            'planned_value',
            'slc'
        )


class DmaCalenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = DmaCalender
        fields = (
            'id',
            'Company', 'Year', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
            'October', 'November', 'December'
        )


class HolidayCalenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = HolidayCalender
        fields = (
            'id',
            'Year', 'Month', 'holiday_title', 'start_date', 'end_date','hours'
        )


class HourTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = HourType
        fields = (
            'id',
            'title',
            'description',
            'hours_allocated',
        )
