from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, update_last_login
import json

from django.db.models import Sum
from rest_framework import serializers

from organizations.serializers import SlcSerializer, DesignationSerializer
from projects.models import ProjectAssignee
from users.models import CustomUser
from django.contrib.auth.password_validation import validate_password
from rest_framework_jwt.settings import api_settings

# from organizations.serializers import DesignationSerializer, SlcSerializer

JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=128, write_only=True)
    # token = serializers.CharField(max_length=255, read_only=True)
    # group = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)
        user = authenticate(email=email, password=password)
        print('user auth: ', user)
        groups = []
        group_list = user.groups.all()

        for group in group_list.iterator():
            print(group)
            groups.append(group.name)
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password is not found.'
            )
        if user.is_active == 1:
            # print('yes')
            group = Group.objects.get(user=user)
            try:
                payload = JWT_PAYLOAD_HANDLER(user)
                jwt_token = JWT_ENCODE_HANDLER(payload)

                update_last_login(None, user)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError(
                    'User with given email and password does not exists'
                )
            return {
                'email': user.email,
                'token': jwt_token,
                'group': json.dumps(groups),
            }
        else:
            return {
                'email': user.email,
                'token': '',
                'group': '',
            }


class RegisterSerializer(serializers.ModelSerializer):
    profile_pic = serializers.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'password', 'email', 'phone', 'profile_pic')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        print(validated_data)
        user = CustomUser.objects.create_user(**validated_data)
        user.username = validated_data['first_name']+validated_data['last_name']
        user.save()
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format="%Y-%m-%d %I:%M:%S %p")

    # designation = DesignationSerializer()
    slc_details = SlcSerializer()
    total_ep = serializers.SerializerMethodField()

    def get_total_ep(self, obj):
        return list(ProjectAssignee.objects.filter(assignee=obj.id).aggregate(Sum('estimated_person')).values())[0]

    class Meta:
        model = CustomUser
        # fields = ('id', 'email', 'date_of_birth', 'first_name', 'last_name', 'date_joined', 'phone', 'profile_pic', 'slc_details', 'address', 'blood_group','total_ep','designation','is_active')
        fields = ('id', 'email', 'date_of_birth', 'first_name', 'last_name', 'date_joined', 'phone', 'profile_pic', 'slc_details', 'address', 'blood_group','total_ep','designation','is_active')


class UserDetailRapidSerializer(serializers.ModelSerializer):
    # date_joined = serializers.DateTimeField(format="%Y-%m-%d %I:%M:%S %p")

    # designation = DesignationSerializer()
    # slc_details = SlcSerializer()
    # total_ep = serializers.SerializerMethodField()

    # def get_total_ep(self, obj):
    #     return list(ProjectAssignee.objects.filter(assignee=obj.id).aggregate(Sum('estimated_person')).values())[0]

    class Meta:
        model = CustomUser
        # fields = ('id', 'email', 'date_of_birth', 'first_name', 'last_name', 'date_joined', 'phone', 'profile_pic', 'slc_details', 'address', 'blood_group','total_ep','designation','is_active')
        fields = ('id', 'first_name', 'last_name')




class UserDetailSerializer2(serializers.ModelSerializer):
    # date_joined = serializers.DateTimeField(format="%Y-%m-%d %I:%M:%S %p")

    # designation = DesignationSerializer()
    # slc_details = SlcSerializer()
    # total_ep = serializers.SerializerMethodField()

    def get_total_ep(self, obj):
        return list(ProjectAssignee.objects.filter(assignee=obj.id).aggregate(Sum('estimated_person')).values())[0]

    class Meta:
        model = CustomUser
        # fields = ('id', 'email', 'date_of_birth', 'first_name', 'last_name', 'date_joined', 'phone', 'profile_pic', 'slc_details', 'address', 'blood_group','total_ep','designation','is_active')
        fields = ('id', 'email', 'first_name', 'last_name')




class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'date_of_birth', 'first_name', 'last_name', 'date_joined', 'phone', 'address', 'blood_group']

    def update(self, instance, validated_data):
        instance.phone = validated_data.get('phone', instance.phone)
        # instance.gender = validated_data.get('gender', instance.gender)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        # instance.address = validated_data.get('address', instance.address)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.address = validated_data.get('address', instance.address)
        instance.blood_group = validated_data.get('blood_group', instance.blood_group)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    model = CustomUser

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class UploadProPicSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'profile_pic']

    def update(self, instance, validated_data):
        instance.profile_pic = validated_data.get('profile_pic', instance.profile_pic)
        instance.save()
        return instance
