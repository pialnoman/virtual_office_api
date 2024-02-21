from meetings.models import Meetings
import sys
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from meetings.serializers import CreateMeetingsSerializer, MeetingsDetailsSerializer, MeetingsUpdateSerializer
from users.serializers import CustomUser
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from datetime import datetime
from django.db.models import Q
import sms_api


# create Meeting
class CreateMeetings(APIView):
    serializer_class = CreateMeetingsSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # user_mail = CustomUser.objects.get(id=request.data['participant'])
            # print(user_mail)
            response = {
                'success': 'True',
                'status code': status.HTTP_200_OK,
                'message': 'Meeting created successfully',
                'data': []
            }
            participants = request.data['participant'].split(',')

            for participant in participants:
                user_mail = CustomUser.objects.get(pk=participant)
                send_mail(
                    'New Meeting!!!',
                    'In order to discuss the work plan and highlight each team memebers role a meeting has been scheduled on ' + str(datetime.strptime(request.data['start_time'], "%Y-%m-%d %H:%M:%S.%f")),
                    'dmavirtualoffice21@gmail.com',
                    [user_mail],
                    fail_silently=False,
                )
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
        return Response(response)


# Meetings details
class MeetingsDetails(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        project_data = []
        try:
            metings = Meetings.objects.get(id=pk)
            serializer = MeetingsDetailsSerializer(metings)
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'Meetings Details',
                        'data': serializer.data}
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
        return Response(response)


# update Meetings
class UpdateMeetings(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk, format=None):
        try:
            meeting = Meetings.objects.get(id=pk)
            serializer = MeetingsUpdateSerializer(meeting, data=request.data)
            if serializer.is_valid():
                serializer.save()
                user_mail = CustomUser.objects.get(id=request.data['participant'])
                response = {
                    'success': 'True',
                    'status code': status.HTTP_200_OK,
                    'message': 'Meetings Updated Successful',
                    'data': serializer.data
                }
                send_mail(
                    'Meeting initiated',
                    'A meeting has been called at ' + str(datetime.strptime(request.data['start_time'],"%Y-%m-%d %H:%M:%S.%f")),
                    'awronno.adhar@gmail.com',
                    [user_mail],
                    fail_silently=False,
                )
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


# Meetings list
class MeetingsList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        meeting_list = []
        try:
            meetings = Meetings.objects.filter(Q(participant__icontains=pk)|Q(host=request.user.id))
            serializer = MeetingsDetailsSerializer(meetings, many=True)
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'Meetings list',
                        'data': serializer.data}
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
        return Response(response)

