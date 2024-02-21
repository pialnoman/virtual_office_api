from datetime import date
from django.db.models import Sum
from django.utils import timezone, dateformat
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import sys
import os
import pendulum
from datetime import datetime
import datetime as dt
from projects.serializers import CreateProjectAssigneeSerializer, UpdateProjectRemainingHrsSerializer, \
    ProjectDetailsSerializer, ProjectAssigneeSerializer, TaskSerializer, ProjectAssigneeSerializer2
from projects.views import unique
from users.models import CustomUser
from users.serializers import UserDetailSerializer, UserDetailSerializer2
from wbs.helper import wbs_wise_file_insert, project_wise_file_insert
from wbs.mails import send_wbs_create_email
from wbs.serializers import CreateTimeCardSerializer, CreateWbsSerializer, WbsDetailsSerializer, WbsUpdateSerializer, \
    TimeCardDetailsSerializer, WbsStatusUpdateSerializer, WbsWiseTimeCardListSerializer, TimecardUpdateSerializer, \
    WbsFileSerializer, SubmitWeeklyTimeCardSerializer, UpdateWeeklyTimeCardSerializer, \
    UserSubmitWeeklyTimeCardSerializer
from wbs.models import TimeCard, Wbs, WeekTimeCard
from projects.models import Projects, ProjectAssignee
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny


# create wbs
class CreateWbs(APIView):
    serializer_class = CreateWbsSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            print('req data', request.data)
            assignee_list = str(request.data['assignee']).replace('[', '').replace(']', '').split(',')
            print("assignee_list", assignee_list)
            for assignee in assignee_list:
                print('assignee', assignee)

                wbs_create_data = request.data
                wbs_create_data._mutable = True
                wbs_create_data['assignee'] = int(assignee)
                serializer = self.serializer_class(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                print('data', serializer.data)
                if int(request.data['total_files']) > 0:
                    result = wbs_wise_file_insert(request=request, wbs_id=serializer.data['id'],
                                                  upload_by=UserDetailSerializer(request.user, many=False).data['id'])
                    print(result)
                user_data = UserDetailSerializer(CustomUser.objects.get(id=assignee)).data
                print(user_data)
                # print("The details that are going to pass is: ", serializer.data['description'])
                send_wbs_create_email(user_data['email'], user_data['first_name'], serializer.data['description'])

            # result = project_wise_file_insert(request=request, work_package_number=request.data.get('work_package_number'),upload_by=UserDetailSerializer(request.user, many=False).data['id'])

            response = {
                'success': 'True',
                'status code': status.HTTP_200_OK,
                'message': 'WBS created  successfully',
                'data': [serializer.data]
            }
            status_code = status.HTTP_200_OK
            return Response(response, status=status_code)
        except Exception as e:
            response = 'on line {}'.format(
                sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


# wbs details
class WbsDetails(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            wbs = Wbs.objects.get(id=pk)
            serializer = WbsDetailsSerializer(wbs)
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'WBS Details',
                        'data': serializer.data}
        except Exception as e:
            response = 'on line {}'.format(
                sys.exc_info()[-1].tb_lineno), str(e)
        return Response(response)


# update wbs
class UpdateWbs(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, pk, format=None):
        # print(request.data)
        try:
            wbs = Wbs.objects.get(id=pk)
            temp_data = request.data
            temp_data._mutable = True
            temp_data['date_updated'] = dateformat.format(timezone.now(), 'Y-m-d')
            serializer = WbsUpdateSerializer(wbs, data=temp_data)
            # print(serializer.errors)
            if serializer.is_valid():
                serializer.save()
                # uploading files
                result = project_wise_file_insert(request=request, work_package_number=wbs.project.work_package_number,
                                                  upload_by=UserDetailSerializer(request.user, many=False).data['id'])
                print(result)
                # uploading files end here
                print(request.data)
                if serializer.data:
                    temp = {
                        "project": request.data['project'],
                        "wbs": serializer.data['id'],
                        "time_card_assignee": request.data['assignee'],
                        "actual_work_done": request.data['actual_work_done'],
                        "hours_today": request.data['hours_worked'],
                    }
                    wbs_status_data = {
                        'id': pk,
                        'status': 2,
                        'date_updated': dateformat.format(timezone.now(), 'Y-m-d')
                    }
                    wbs_status_update_serializer = WbsStatusUpdateSerializer(wbs, data=wbs_status_data)
                    if wbs_status_update_serializer.is_valid():
                        wbs_status_update_serializer.save()

                    serializer2 = CreateTimeCardSerializer(data=temp)
                    serializer2.is_valid()
                    print(serializer2.errors)
                    if serializer2.is_valid():
                        serializer2.save()
                        project = Projects.objects.get(id=request.data['project'])
                        temp2 = {
                            "remaining_hours": float(project.remaining_hours) - float(request.data['hours_worked'])
                        }
                        serializer3 = UpdateProjectRemainingHrsSerializer(project, data=temp2)
                        if serializer3.is_valid():
                            serializer3.save()
                            print(serializer.data)
                            user_email = \
                                UserDetailSerializer(CustomUser.objects.get(id=serializer.data['assignee'])).data[
                                    'email']

                            if int(request.data['total_files']) > 0:
                                result = wbs_wise_file_insert(request=request, wbs_id=serializer.data['id'],
                                                              upload_by=
                                                              UserDetailSerializer(request.user, many=False).data['id'])
                                print(result)

                            send_wbs_create_email(user_email, UserDetailSerializer(
                                CustomUser.objects.get(id=serializer.data['assignee'])).data['first_name'])
                            response = {
                                'success': 'True',
                                'status code': status.HTTP_200_OK,
                                'message': 'wbs Updated Successful',
                                'data': serializer.data
                            }
                            return Response(response, status=status.HTTP_200_OK)
                        else:
                            response = {
                                'success': 'False',
                                'status code': status.HTTP_400_BAD_REQUEST,
                                'message': 'failed to update remaining hours'
                            }
                            return Response(response, status=status.HTTP_200_OK)
                    else:
                        response = {
                            'success': 'False',
                            'status code': status.HTTP_400_BAD_REQUEST,
                            'message': 'failed to insert in time card'
                        }
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors)
        except Exception as e:
            response = 'on line {}'.format(
                sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


# update wbs status
class UpdateWbsStatus(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, pk, format=None):
        # print(request.data)
        try:
            wbs = Wbs.objects.get(id=pk)
            temp_data = request.data
            temp_data['date_updated'] = dateformat.format(timezone.now(), 'Y-m-d')
            # print(temp_data)
            serializer = WbsStatusUpdateSerializer(wbs, data=temp_data)
            # print(serializer.errors)
            if serializer.is_valid():
                serializer.save()
                response = {
                    'success': 'True',
                    'status code': status.HTTP_200_OK,
                    'message': 'wbs Updated Successful',
                    'data': serializer.data
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors)
        except Exception as e:
            response = 'on line {}'.format(
                sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


# WBS list for employee
class WbsListForEmployee(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            wbsList = Wbs.objects.filter(assignee=pk).order_by('-date_updated')
            serializer = WbsDetailsSerializer(wbsList, many=True).data
            for wbs in serializer:
                if datetime.strptime(wbs['end_date'], '%Y-%m-%d').date() < date.today() and wbs['status'] != 3:
                    Wbs.objects.filter(pk=wbs['id']).update(status=4)

            response = {'success': 'True', 'status code': status.HTTP_200_OK,
                        'message': 'Assigned WBS List for an employee',
                        'data': serializer.data}
            return Response(response)
        except Exception as e:
            response = 'on line {}'.format(
                sys.exc_info()[-1].tb_lineno), str(e)
        return Response({'success': 'False', 'status code': status.HTTP_400_BAD_REQUEST, 'message': 'Bad Request'})


# project wise WBS list
class WbsListForProject(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            wbsList = Wbs.objects.filter(work_package_number=pk).order_by('-date_updated')
            Serializer = WbsDetailsSerializer(wbsList, many=True)
            response = {'success': 'True', 'status code': status.HTTP_200_OK,
                        'message': 'Assigned WBS List for a project',
                        'data': Serializer.data}
        except Exception as e:
            response = 'on line {}'.format(
                sys.exc_info()[-1].tb_lineno), str(e)
        return Response(response)


# Pm wise WBS list
class AllWbsListForPm(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            pm_project_list = Projects.objects.filter(pm=pk).order_by('date_updated')
            pm_project_list_serializer = ProjectDetailsSerializer(data=pm_project_list, many=True)
            pm_project_list_serializer.is_valid()
            temp_data = []
            temp_id = []
            for project in pm_project_list_serializer.data:
                # print(project['sub_task'])
                pm_wbs_list = Wbs.objects.filter(project=project['id']).order_by('-id')
                # print(pm_wbs_list)
                serializer2 = WbsDetailsSerializer(data=pm_wbs_list, many=True)
                serializer2.is_valid()
                for wbs in serializer2.data:
                    print('***', datetime.strptime(wbs['end_date'], '%Y-%m-%d').date() > date.today())
                    if datetime.strptime(wbs['end_date'], '%Y-%m-%d').date() < date.today() and wbs['status'] != 3:
                        Wbs.objects.filter(pk=wbs['id']).update(status=4)
                    temp_data.append(wbs)
                    temp_id.append(wbs['id'])

            assignee_project_list = ProjectAssignee.objects.filter(assignee=pk).order_by('date_updated')
            assignee_project_list_serializer = ProjectAssigneeSerializer(data=assignee_project_list, many=True)
            assignee_project_list_serializer.is_valid()
            # print("temp_project_id_list", assignee_project_list_serializer.data)
            for project in assignee_project_list_serializer.data:
                if project['project'] is not None:
                    pm_wbs_list = Wbs.objects.filter(project=project['project']['id']).order_by('-id')
                    serializer2 = WbsDetailsSerializer(data=pm_wbs_list, many=True)
                    serializer2.is_valid()
                    for wbs in serializer2.data:
                        if datetime.strptime(wbs['end_date'], '%Y-%m-%d').date() < date.today() and wbs['status'] != 3:
                            Wbs.objects.filter(pk=wbs['id']).update(status=4)
                        if wbs['id'] not in temp_id:
                            print('true')
                            temp_data.append(wbs)
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'PM wise WBS List',
                        'data': temp_data}
            return Response(response)
        except Exception as e:
            response = 'on line {}'.format(
                sys.exc_info()[-1].tb_lineno), str(e)
        return Response(response)


# Whole WBS list of assigned projects of an employee
class AllUserWbsListOfProject(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk):
        try:
            wbs_project_list = []
            temp = []
            assigned_projects = ProjectAssignee.objects.filter(assignee=pk).order_by('-date_updated')
            serializer = CreateProjectAssigneeSerializer(assigned_projects, many=True)
            for AssignedProject in serializer.data:
                assigned_wbs_list = Wbs.objects.filter(project=AssignedProject['project']).order_by('-id')
                wbs_project_list.append(assigned_wbs_list)
            for wbs_list in wbs_project_list:
                serializer2 = WbsDetailsSerializer(wbs_list, many=True)
                for wbs in serializer2.data:
                    temp.append(wbs)
            # print(temp)
            response = {'success': 'True', 'status code': status.HTTP_200_OK,
                        'message': 'Assigned WBS List for a project',
                        'data': temp}
        except Exception as e:
            response = 'on line {}'.format(
                sys.exc_info()[-1].tb_lineno), str(e)
        return Response(response)


# completed WBS count for a project
class CompletedWbsVsTotalCount(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            completed_wbs_count = Wbs.objects.filter(
                work_package_number=pk, status=4).count()
            total_wbs_count = Wbs.objects.filter(
                work_package_number=pk).count()
            response = {
                'success': 'True',
                'status code': status.HTTP_200_OK,
                'message': 'Completed WBS count for a project',
                'data': {
                    "completed_wbs": completed_wbs_count,
                    "total_wbs": total_wbs_count
                }
            }
        except Exception as e:
            response = 'on line {}'.format(
                sys.exc_info()[-1].tb_lineno), str(e)
        return Response(response)


# create time card
class CreateTimeCard(APIView):
    serializer_class = CreateTimeCardSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            'success': 'True',
            'status code': status.HTTP_200_OK,
            'message': 'Time card created successfully',
            'data': []
        }
        status_code = status.HTTP_200_OK
        return Response(response, status=status_code)


# time card details
class TimeCardDetails(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            time_card = TimeCard.objects.get(id=pk)
            serializer = TimeCardDetailsSerializer(time_card)
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'time card details',
                        'data': serializer.data}
        except Exception as e:
            response = 'on line {}'.format(
                sys.exc_info()[-1].tb_lineno), str(e)
        return Response(response)


class AllTimeCards(APIView):
    permission_classes = (IsAuthenticated,)

    # def get(self,request,pk):
    # try:
    # time_cards = TimeCard.objects.filter()


# wbs wise time card list
class WbsWiseTimeCardList(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk):
        try:
            time_card = TimeCard.objects.filter(wbs=pk).order_by('-date_updated')
            serializer = WbsWiseTimeCardListSerializer(time_card, many=True)
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'time card for a WBS',
                        'data': serializer.data}
        except Exception as e:
            response = 'on line {}'.format(
                sys.exc_info()[-1].tb_lineno), str(e)
        return Response(response)


# user wise time card list
class UserWiseTimeCardList(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk):
        try:
            time_card = TimeCard.objects.filter(time_card_assignee=pk).order_by('-date_updated')
            serializer = WbsWiseTimeCardListSerializer(time_card, many=True)
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'time card for a user',
                        'data': serializer.data}
        except Exception as e:
            response = 'on line {}'.format(
                sys.exc_info()[-1].tb_lineno), str(e)
        return Response(response)


# user wise time card list
class UserWiseWeeklyTimeCardList(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk):
        try:
            pendulum.week_starts_at(pendulum.SUNDAY)
            pendulum.week_ends_at(pendulum.SATURDAY)
            today = pendulum.now()
            print(today.start_of('week'))
            start = today.start_of('week')
            print(start.to_datetime_string())
            end = today.end_of('week')
            print(end.to_datetime_string())
            time_card = TimeCard.objects.filter(time_card_assignee=pk, date_updated__gte=start,
                                                date_updated__lte=end).order_by('date_updated')
            serializer = WbsWiseTimeCardListSerializer(time_card, many=True)
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'time card for a user',
                        'data': serializer.data, 'start_date': start, 'end_date': end}
        except Exception as e:
            response = 'on line {}'.format(
                sys.exc_info()[-1].tb_lineno), str(e)
        return Response(response)


class TimecardUpdate(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, pk, format=None):
        try:
            print(request.data)
            timecard = TimeCard.objects.get(id=pk)
            temp_data = request.data
            # temp_data['date_updated'] = dateformat.format(timezone.now(), 'Y-m-d')
            print(temp_data)
            serializer = TimecardUpdateSerializer(timecard, data=temp_data)
            if serializer.is_valid():
                print(serializer.errors)
                serializer.save()
                response = {
                    'success': 'True',
                    'status code': status.HTTP_200_OK,
                    'message': 'timecard Updated Successful',
                    'data': serializer.data
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    'success': 'False',
                    'status code': status.HTTP_400_BAD_REQUEST,
                    'message': 'failed to update timecard'
                }
                return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            response = 'on line {}'.format(
                sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


# add time card API
class AddTimeCard(APIView):
    permission_classes = (AllowAny,)
    serializer_class = CreateTimeCardSerializer

    def post(self, request):
        try:
            print(request.data)
            data = {
                'time_type': request.data['hours_type'],
                'actual_work_done': request.data['actual_work_done'],
                'hour_description': request.data['hour_description'],
                'submitted': 0,
                'hours_today': request.data['hours'],
                'project': request.data['project'],
                'wbs': request.data['wbs'],
                'time_card_assignee': request.data['assignee'],
                'date_created': datetime.now().date(),
                'date_updated': datetime.now().date()
            }
            print(data)
            new_time_card = self.serializer_class(data=data)
            new_time_card.is_valid(raise_exception=True)
            new_time_card.save()

            response = {
                'success': 'True',
                'status code': status.HTTP_200_OK,
                'message': 'Timecard added Successfully',
                'data': new_time_card.data
            }
            return Response(response)
        except Exception as e:
            response = 'on line {}'.format(
                sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


class SubmitTimeCard(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        total_hours = 0
        print(request.data)

        for item in request.data['time_cards'].split(","):
            total_hours += float(TimeCard.objects.filter(pk=item)[0].hours_today)
            TimeCard.objects.filter(pk=item).update(submitted=True)

        new_weekly_submission = {
            'employee': request.data['employee'],
            'total_hours': total_hours,
            'week_start': request.data['week_start'],
            # 'pdf_file': request.data.get('pdf_file'),
            'week_end': request.data['week_end'],
            'submitted': 1,
            'submitted_at': datetime.now(),
            'submitted_by': request.user.id
        }
        print(new_weekly_submission)
        week_timecard = WeekTimeCard.objects.filter(week_start=request.data['week_start'],
                                                    week_end=request.data['week_end'],
                                                    employee=request.data['employee']).exists()
        if week_timecard:
            existing_tc = WeekTimeCard.objects.filter(week_start=request.data['week_start'],
                                                      week_end=request.data['week_end'],
                                                      employee=request.data['employee']).first()
            print(existing_tc)
            updated_timecard = UpdateWeeklyTimeCardSerializer(existing_tc, data=new_weekly_submission)

            if updated_timecard.is_valid():
                updated_timecard.save()

        else:
            try:
                submitted_week_timecard = SubmitWeeklyTimeCardSerializer(data=new_weekly_submission)
                if submitted_week_timecard.is_valid(raise_exception=True):
                    submitted_week_timecard.save()
                else:
                    print('else')
                    print(submitted_week_timecard.errors)
            except Exception as e:
                print(e)

        response = {
            'success': 'True',
            'status code': status.HTTP_200_OK,
            'message': 'Time Cards Submitted Successfully',
            'data': 'Time Cards Submitted'
        }
        return Response(response, status=status.HTTP_200_OK)


class UserSubmittedWeeklyTimecards(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        try:
            submitted_timecards = []
            if request.user.has_perm('projects.add_projects'):

                my_projects = TaskSerializer(Projects.objects.filter(pm=user.id), many=True).data
                assignees = []
                for task in my_projects:
                    task_assignees = ProjectAssigneeSerializer2(ProjectAssignee.objects.filter(project_id=task['id']),
                                                               many=True).data
                    for task_assignee in task_assignees:

                        assignee_id = task_assignee['assignee']['id']
                        assignee = CustomUser.objects.get(pk=assignee_id)

                        if assignee.is_active:
                            data = UserDetailSerializer2(assignee, many=False).data
                            assignees.append(data)

                        # assignees.append(
                        #     UserDetailSerializer2(CustomUser.objects.get(pk=task_assignee['assignee']['id']),
                        #                          many=False).data)

                assignees.append(UserDetailSerializer2(CustomUser.objects.get(pk=user.id), many=False).data)
                assignees = unique(assignees)  # making assignees array distinct
                # print("See the List: ", assignees)

                for assignee in assignees:
                    tc_list = UserSubmitWeeklyTimeCardSerializer(WeekTimeCard.objects.filter(employee=assignee['id']).order_by('-submitted_at'),
                                                                 many=True).data
                    for tc in tc_list:
                        submitted_timecards.append(tc)


            else:
                submitted_timecards = UserSubmitWeeklyTimeCardSerializer(WeekTimeCard.objects.filter(employee=user.id),
                                                                         many=True).data

            for tc in submitted_timecards:
                tc['RHR'] = TimeCard.objects.filter(time_card_assignee=tc['employee']['id'], time_type='RHR',
                                                    date_created__range=(tc['week_start'], tc['week_end'])).aggregate(
                    Sum('hours_today')).get('hours_today__sum')
                tc['SIC'] = TimeCard.objects.filter(time_card_assignee=tc['employee']['id'], time_type='SIC',
                                                    date_created__range=(tc['week_start'], tc['week_end'])).aggregate(
                    Sum('hours_today')).get('hours_today__sum')
                tc['HOL'] = TimeCard.objects.filter(time_card_assignee=tc['employee']['id'], time_type='HOL',
                                                    date_created__range=(tc['week_start'], tc['week_end'])).aggregate(
                    Sum('hours_today')).get('hours_today__sum')
                tc['PB1'] = TimeCard.objects.filter(time_card_assignee=tc['employee']['id'], time_type='PB1',
                                                    date_created__range=(tc['week_start'], tc['week_end'])).aggregate(
                    Sum('hours_today')).get('hours_today__sum')
                tc['PB2'] = TimeCard.objects.filter(time_card_assignee=tc['employee']['id'], time_type='PB2',
                                                    date_created__range=(tc['week_start'], tc['week_end'])).aggregate(
                    Sum('hours_today')).get('hours_today__sum')
                tc['WFH'] = TimeCard.objects.filter(time_card_assignee=tc['employee']['id'], time_type='WFH',
                                                    date_created__range=(tc['week_start'], tc['week_end'])).aggregate(
                    Sum('hours_today')).get('hours_today__sum')
                tc['OTO'] = TimeCard.objects.filter(time_card_assignee=tc['employee']['id'], time_type='OTO',
                                                    date_created__range=(tc['week_start'], tc['week_end'])).aggregate(
                    Sum('hours_today')).get('hours_today__sum')
                tc['VAC'] = TimeCard.objects.filter(time_card_assignee=tc['employee']['id'], time_type='VAC',
                                                    date_created__range=(tc['week_start'], tc['week_end'])).aggregate(
                    Sum('hours_today')).get('hours_today__sum')
                tc['COM'] = TimeCard.objects.filter(time_card_assignee=tc['employee']['id'], time_type='COM',
                                                    date_created__range=(tc['week_start'], tc['week_end'])).aggregate(
                    Sum('hours_today')).get('hours_today__sum')
            response = {
                'success': 'True',
                'status code': status.HTTP_200_OK,
                'message': 'Submitted Weekly timecards',
                'data': submitted_timecards
            }
            # print("response1111111", response)
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = 'on line {}'.format(
                sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


class UploadWbsDocs(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        upload_by = request.data.get('upload_by')
        files = int(request.data.get('files')) + 1

        for i in range(1, files):
            indexval = str(i)
            attribute_name = str('file' + indexval)
            file = request.data.get(attribute_name)
            requested_data = {"wbs_id": request.data.get('wbs_id'), "file": file, "upload_by": upload_by}
            serializer = WbsFileSerializer(data=requested_data)
            if serializer.is_valid():
                serializer.save()
            else:
                serializer.errors()

        response = {
            'success': 'True',
            'status code': status.HTTP_200_OK,
            'message': 'WBS docs uploaded',
            'data': 'Time Cards Submitted'
        }
        return Response(response, status=status.HTTP_200_OK)


class ConsumedHours(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user = UserDetailSerializer(request.user).data
            hours = {}
            hours['RHR'] = TimeCard.objects.filter(time_card_assignee=user["id"], time_type='RHR',
                                                   date_created__year=dt.date.today().year).aggregate(
                Sum('hours_today')).get('hours_today__sum')
            hours['SIC'] = TimeCard.objects.filter(time_card_assignee=user['id'], time_type='SIC',
                                                   date_created__year=dt.date.today().year).aggregate(
                Sum('hours_today')).get('hours_today__sum')
            hours['HOL'] = TimeCard.objects.filter(time_card_assignee=user['id'], time_type='HOL',
                                                   date_created__year=dt.date.today().year).aggregate(
                Sum('hours_today')).get('hours_today__sum')
            hours['PB1'] = TimeCard.objects.filter(time_card_assignee=user['id'], time_type='PB1',
                                                   date_created__year=dt.date.today().year).aggregate(
                Sum('hours_today')).get('hours_today__sum')
            hours['PB2'] = TimeCard.objects.filter(time_card_assignee=user['id'], time_type='PB2',
                                                   date_created__year=dt.date.today().year).aggregate(
                Sum('hours_today')).get('hours_today__sum')
            hours['WFH'] = TimeCard.objects.filter(time_card_assignee=user['id'], time_type='WFH',
                                                   date_created__year=dt.date.today().year).aggregate(
                Sum('hours_today')).get('hours_today__sum')
            hours['OTO'] = TimeCard.objects.filter(time_card_assignee=user['id'], time_type='OTO',
                                                   date_created__year=dt.date.today().year).aggregate(
                Sum('hours_today')).get('hours_today__sum')
            hours['VAC'] = TimeCard.objects.filter(time_card_assignee=user['id'], time_type='VAC',
                                                   date_created__year=dt.date.today().year).aggregate(
                Sum('hours_today')).get('hours_today__sum')
            hours['COM'] = TimeCard.objects.filter(time_card_assignee=user['id'], time_type='COM',
                                                   date_created__year=dt.date.today().year).aggregate(
                Sum('hours_today')).get('hours_today__sum')

            return Response({'data': hours})
        except Exception as e:
            response = 'on line {}'.format(
                sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)
