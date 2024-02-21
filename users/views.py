import json
from datetime import date, datetime
from django.contrib.auth.models import Group, update_last_login
from django.db.models import Q
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os

from projects.models import Projects
from projects.serializers import SubTaskSerializer
from users.serializers import ChangePasswordSerializer, LoginSerializer, RegisterSerializer, UserDetailSerializer, \
    UserUpdateSerializer, UploadProPicSerializer, JWT_PAYLOAD_HANDLER, JWT_ENCODE_HANDLER
from users.models import CustomUser
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework import generics
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import AllowAny
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text
from .auth import EmailOrUsernameModelBackend
from django.core.mail import send_mail
import sms_api
import sys
from operator import attrgetter
from rest_framework.parsers import MultiPartParser
import itertools


# user register
from .mails import send_registration_email


class Register(APIView):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
    parser_classes = (MultiPartParser,)

    def post(self, request):
        try:
            print('from views1', request.data)
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            print('from views2', serializer.data)
            response = {
                'success': 'True',
                'status code': status.HTTP_200_OK,
                'message': 'User registered  successfully',
                'data': []
            }
            message = "Your account has been created successfully. Please wait until your account being activated. " \
                      "you will be notified soon once it is get activated. "
            # sms_api.SmsGateway.post(
            #     {
            #         'number': request.data['phone'],
            #         'message': message
            #     }
            # )
            send_registration_email(request.data['email'],serializer.data['first_name'])
            # send_mail('New user registration', message, 'dmavirtualoffice21@gmail.com', [request.data['email']],
            #           fail_silently=False, )
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            response = {
                'success': 'False',
                'status code': status.HTTP_400_BAD_REQUEST,
                'message': 'User registration failed',
                'errors': serializer.errors
            }
            # response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response, status=status.HTTP_201_CREATED)


# possible assignees for a new project
class PossibleAssigneeList(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            users = CustomUser.objects.filter(is_active=True).exclude(is_superuser=1)
            serializer = UserDetailSerializer(users, many=True)
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'Possible assignee list',
                        'data': serializer.data}
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
        return Response(response)


# user login
class Login(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        print(request.data)
        response = {
            'success': 'True',
            'status code': status.HTTP_200_OK,
            'message': 'User logged in  successfully',
            # 'exp': serializer.data['token'],
        }
        user_data = CustomUser.objects.filter(email=request.data.get('email')).first()
        # is_phone_unique = CustomUser.objects.filter(phone=request.data.get('phone')).first()
        if user_data is None:
            response['success'] = 'False'
            response['status code'] = status.HTTP_404_NOT_FOUND
            response['message'] = "User Not Found"
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        elif user_data.is_active == 1 and user_data.groups.count() > 0:
            auth_user = EmailOrUsernameModelBackend.authenticate(user_data, username=request.data.get('email'),
                                                                 password=request.data.get('password'))
            if auth_user is None:
                response['success'] = "False"
                response['status code'] = status.HTTP_400_BAD_REQUEST
                response['message'] = "Wrong Credentials"
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    payload = JWT_PAYLOAD_HANDLER(auth_user)
                    jwt_token = JWT_ENCODE_HANDLER(payload)
                    groups = []
                    group_list = auth_user.groups.all()
                    for group in group_list.iterator():
                        groups.append(group.name)
                    update_last_login(None, auth_user)
                    response['success'] = 'True'
                    response['user_id'] = auth_user.id
                    response['token'] = jwt_token
                    response['groups'] = json.dumps(groups)
                    response['status code'] = status.HTTP_200_OK
                    response['message'] = 'User Logged in'
                    return Response(response, status=status.HTTP_200_OK)
                except CustomUser.DoesNotExist:
                    response['success'] = 'False'
                    response['status code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
                    response['message'] = 'Internal Server Error'
                    return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        elif user_data.groups.count() < 1:
            response['success'] = 'False'
            response['status code'] = status.HTTP_403_FORBIDDEN
            response['message'] = 'This user has no role in virtual office'
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        else:
            response['success'] = 'False'
            response['status code'] = status.HTTP_403_FORBIDDEN
            response['message'] = 'User is not approved yet. Please wait for admin approval.'
            return Response(response, status=status.HTTP_403_FORBIDDEN)


# user logout 
class Logout(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        # using Django logout
        logout(request)
        content = {
            'success': True,
            'status code': status.HTTP_201_CREATED,
            'message': 'logout Successfully',
        }
        return Response(content)


# user profile view
class UserDetail(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        response = {
            'success': 'True',
            'status code': status.HTTP_200_OK,
            'message': 'User found successfully',
            'data': []
        }
        try:
            user = CustomUser.objects.get(id=pk)
        except ObjectDoesNotExist:
            response['message'] = 'User not found'
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        serializer = UserDetailSerializer(user, many=False)
        response['data'] = serializer.data
        return Response(response, status=status.HTTP_200_OK)


# user  profile update
class UserUpdate(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def post(self, request, pk):
        print(request.data)
        response = {
            'success': 'True',
            'status code': status.HTTP_200_OK,
            'message': 'Profile Updated',
            'data': []
        }
        if self.request.user.id != int(pk):
            response['status code'] = status.HTTP_400_BAD_REQUEST
            response['message'] = 'You can not update this profile!!'
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        user = CustomUser.objects.get(id=pk)
        id = user.id
        serializer = UserUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response['data'] = serializer.data
            return Response(response, status=status.HTTP_201_CREATED)
        response['message'] = 'Something went wrong'
        response['data'] = serializer.errors
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


# upload profile picture
class ChangeProfileImage(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def post(self, request, pk):
        print(request, pk)
        response = {
            'success': 'True',
            'status code': status.HTTP_200_OK,
            'message': 'Profile Picture Updated',
            'data': []
        }
        if self.request.user.id != int(pk):
            response['status code'] = status.HTTP_400_BAD_REQUEST
            response['message'] = 'You can not update this profile!!'
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        user = CustomUser.objects.get(id=pk)
        serializer = UploadProPicSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response['data'] = serializer.data
            return Response(response, status=status.HTTP_201_CREATED)
        response['message'] = 'Something went wrong'
        response['data'] = serializer.errors
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


class ChangePassword(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer
    model = CustomUser

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AllPermissions(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            # user = CustomUser.objects.get(email=request.user)
            group_permissions = request.user.get_group_permissions()
            # all_permissions = request.user.get_all_permissions()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Permission List',
                'data': group_permissions,
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response, status=status.HTTP_200_OK)
