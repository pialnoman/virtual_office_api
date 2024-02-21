import datetime
import sys

from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from organizations.serializers import DmaCalenderSerializer, HolidayCalenderSerializer, HourTypeSerializer
from users.models import CustomUser
from wbs.models import TimeCard
from .models import DmaCalender, HolidayCalender, HourType
from rest_framework.permissions import IsAuthenticated, AllowAny
from users.serializers import UserDetailSerializer
from datetime import date


class DmaCalenderDetails(APIView):
    permission_classes = (AllowAny,)
    serializer_class = DmaCalenderSerializer

    def get(self, request):
        try:
            calender = DmaCalender.objects.all()
            serializer = DmaCalenderSerializer(calender, many=True)
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'DMA calender Details',
                        'data': serializer.data}
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)

        return Response(response)


class HolidayCalenderDetails(APIView):
    permission_classes = (AllowAny,)
    serializer_class = HolidayCalenderSerializer

    def get(self, request):
        try:
            calender = HolidayCalender.objects.all()
            serializer = HolidayCalenderSerializer(calender, many=True)
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'DMA calender Details',
                        'data': serializer.data}
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)

        return Response(response)


class HoursSpentAndLeft(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request,pk):
        try:
            user = UserDetailSerializer(CustomUser.objects.get(pk=pk)).data
            user_company = user['slc_details']['slc']['department']['company']['id']
            current_year = date.today().year
            hour_types=HourTypeSerializer(HourType.objects.filter(company=user_company),many=True).data
            for type in hour_types:
                hours_spent=TimeCard.objects.filter(time_card_assignee=user['id'], time_type=type['title'],date_created__year=current_year).aggregate(Sum('hours_today')).get('hours_today__sum')
                type['spent']=hours_spent

            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'Hours used and left',
                        'data': hour_types}
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = 'on line {}'.format(
                sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)



class WorkTypesList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user = UserDetailSerializer(request.user).data
            if user['slc_details'] is None:
                hour_types = HourTypeSerializer(HourType.objects.all(), many=True).data
            else:
                user_company = user['slc_details']['slc']['department']['company']['id']
                hour_types = HourTypeSerializer(HourType.objects.filter(company=user_company), many=True).data
            print(hour_types)
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'Work type list',
                        'data': hour_types}
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = 'on line {}'.format(
                sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)
