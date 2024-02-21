from datetime import date

from rest_framework.serializers import Serializer
from projects.models import Projects
from django.contrib.auth.models import Group
from django.http import Http404
import sys
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from evms.serializers import CreateEvmsSerializer, EvmsDetailsSerializer, EvmsUpdateSerializer
from projects.serializers import ProjectDetailsSerializer
from users.models import CustomUser
from evms.models import Evms
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


# create EVMS
class CreateEvms(APIView):
    serializer_class = CreateEvmsSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        planned_hours = request.data.pop('planned_hours')
        planned_value = request.data.pop('planned_value')
        project_id = request.data.get('project')
        Projects.objects.filter(id=project_id).update(planned_hours=planned_hours,planned_value=planned_value)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            'success': 'True',
            'status code': status.HTTP_200_OK,
            'message': 'EVMS created successfully',
            'data': []
        }
        status_code = status.HTTP_200_OK
        return Response(response, status=status_code)


# EVMS details
class EvmsDetails(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            evms_list = Evms.objects.get(work_package_number=pk)
            serializer = EvmsDetailsSerializer(evms_list)
            projects = Projects.objects.filter(work_package_number=pk)
            project_serializer = ProjectDetailsSerializer(projects, many=True)
            data = {
                "projects": project_serializer.data,
                "evms": serializer.data
            }
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'EVMS Details',
                        'data': data}
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
        return Response(response)


# update EVMS
class UpdateEvms(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk, format=None):
        try:
            planned_hours = request.data.pop('planned_hours')
            planned_value = request.data.pop('planned_value')
            project_id = request.data.get('project')
            Projects.objects.filter(id=project_id).update(planned_hours=planned_hours, planned_value=planned_value)
            evms = Evms.objects.get(id=pk)
            serializer = EvmsUpdateSerializer(evms, data=request.data)
            # print(serializer.is_valid())
            # print(serializer.errors)
            if serializer.is_valid():
                serializer.save()
                response = {
                    'success': 'True',
                    'status code': status.HTTP_200_OK,
                    'message': 'EVMS Updated Successful',
                    'data': serializer.data
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


# EVMS list for PM
class EvmsListForPm(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk):
        evms_data = []
        try:
            evms_list = Evms.objects.all()
            for evms in evms_list:
                if evms.project.pm_id is int(pk):
                    Serializer = EvmsDetailsSerializer(evms)
                    evms_data.append(Serializer.data)
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'EVMS list',
                        'data': evms_data}
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
        return Response(response)