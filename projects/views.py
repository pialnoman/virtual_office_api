import datetime
import sys
from django.utils import timezone

from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.mail import send_mail
import projects
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from projects.helper import calculate_hours_from_date_to_date
from projects.mails import send_create_project_email, send_update_project_email
from projects.serializers import SubTaskSerializer, CreateProjectSerializer, ProjectDetailsSerializer, \
    UpdateProjectSerializer, ProjectAssigneeSerializer, TdoSerializer, CreateProjectAssigneeSerializer, \
    UpdateSubTaskSerializer, TaskSerializer, ProjectFileSerializer, DocumentListSerializer, \
    UpdateProjectAssigneeSerializer, ProjectAssigneeSerializer2, ProjectDetailsSerializerRapid, \
    ProjectAssigneeRapidSerializer

from users.models import CustomUser
from projects.models import Projects, ProjectAssignee, Tdo, ProjectSharedFiles
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Prefetch
from collections import defaultdict

# create project
from users.serializers import UserDetailSerializer, UserDetailSerializer2, UserDetailRapidSerializer
from virtual_office_API.settings import EMAIL_HOST_USER
from post_office import mail
from wbs.models import Wbs


class CreateProject(APIView):
    serializer_class = TdoSerializer
    serializer_class2 = CreateProjectSerializer
    serializer_class3 = CreateProjectAssigneeSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        print(enumerate(request.data['assignee']))
        count_project_wp = Projects.objects.filter(work_package_number=request.data['work_package_number'])
        work_package_index = str(request.data['work_package_number']) + '.' + str(len(count_project_wp) + 1)
        request.data['work_package_index'] = work_package_index
        user = UserDetailSerializer(request.user).data
        user_company = user['slc_details']['slc']['department']['company']['id']

        if not Tdo.objects.filter(title=request.data['task_delivery_order'], company=user_company).exists():
            # create tdo block #####################
            tdo_data = {
                'company': user_company,
                'title': request.data['task_delivery_order'],
                'description': request.data['tdo_details']
            }
            serializer_tdo = self.serializer_class(data=tdo_data)
            if serializer_tdo.is_valid(raise_exception=True):
                serializer_tdo.save()
                request.data['task_delivery_order'] = serializer_tdo.data['id']
        else:
            tdo = Tdo.objects.filter(title=request.data['task_delivery_order'], company=user_company)[0]
            tdo.description = request.data['tdo_details']
            tdo.save()
            request.data['task_delivery_order'] = TdoSerializer(tdo).data['id']

        if request.data['task_delivery_order'] is not None:
            serializer = self.serializer_class2(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                user_mail_list = []
                pm_mail = []
                description = []
                for idx, item in enumerate(request.data['assignee']):
                    # print(idx, item)
                    if serializer.data is not None:
                        # create assignee block #####################
                        # print('project assignee EP', request.data['estimated_person'][idx])
                        temp_data = {
                            'estimated_person': request.data['estimated_person'][idx],
                            'assignee': item,
                            'is_assignee_active': 1,
                            'project': serializer.data['id'],
                            'date_created': datetime.datetime.now(),
                            'date_updated': datetime.datetime.now()
                        }
                        serializer2 = self.serializer_class3(data=temp_data)
                        if serializer2.is_valid(raise_exception=True):
                            serializer2.save()
                            user_email = UserDetailSerializer(CustomUser.objects.get(id=item)).data['email']
                            pm_email = UserDetailSerializer(CustomUser.objects.get(id=serializer.data['pm'])).data['email']
                            user_mail_list.append(user_email)
                            if len(pm_mail) == 0:
                                pm_mail.append(pm_email)
                            if len(description) == 0:
                                description.append(serializer.data['description'])
                try:
                    # print("View Recipient Emails: ", user_mail_list)
                    send_create_project_email(user_mail_list, description[0], pm_mail)
                except Exception as e:
                    print(e)

                response = {
                    'success': 'True',
                    'status code': status.HTTP_200_OK,
                    'message': 'Project created successfully',
                    'data': serializer.data
                }
                # for idx, item in enumerate(request.data['assignee']):
                #     print(idx, item)
                #     if serializer.data is not None:
                #         # create assignee block #####################
                #         # print('project assignee EP', request.data['estimated_person'][idx])
                #         temp_data = {
                #             'estimated_person': request.data['estimated_person'][idx],
                #             'assignee': item,
                #             'is_assignee_active': 1,
                #             'project': serializer.data['id'],
                #             'date_created': datetime.datetime.now(),
                #             'date_updated': datetime.datetime.now()
                #         }
                #         serializer2 = self.serializer_class3(data=temp_data)
                #         if serializer2.is_valid(raise_exception=True):
                #             serializer2.save()
                #             user_email = UserDetailSerializer(CustomUser.objects.get(id=item)).data['email']
                #             pm_email = UserDetailSerializer(CustomUser.objects.get(id=serializer.data['pm'])).data['email']
                #             description = serializer.data['description']
                #             try:
                #                 print("View Recipient Emails: ", user_email)
                #                 send_create_project_email(user_email, description, pm_email)
                #                 # send_create_project_email(pm_email,
                #                 #                           "(This is a copy to PM)",
                #                 #                           'https://vo.dma-bd.com/#/login/?task_details=' +
                #                 #                           serializer.data['work_package_index'],
                #                 #                           serializer.data['description'])
                #                 # print("Mail Sent Successfully.")
                #             except Exception as e:
                #                 print(e)
                #
                #             response = {
                #                 'success': 'True',
                #                 'status code': status.HTTP_200_OK,
                #                 'message': 'Project created successfully',
                #                 'data': serializer.data
                #             }
            status_code = status.HTTP_200_OK
        return Response(response, status=status_code)


def unique(list1):
    # initialize a null list
    unique_list = []

    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    # print list
    return unique_list


class SubTaskDetails(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, work_package_index):
        try:
            sub_task = SubTaskSerializer(Projects.objects.get(work_package_index=work_package_index)).data
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'Sub Task Details',
                        'data': sub_task}
        except Exception as e:

            response = {'success': 'False', 'status code': status.HTTP_400_BAD_REQUEST,
                        'message': 'on line {}'.format(sys.exc_info()[-1].tb_lineno)}

        return Response(response)


class NewProjectDetails(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            projects = Projects.objects.filter(work_package_number=pk)
            serialized_subtask = ''
            if len(projects) > 0:
                serialized_subtask = SubTaskSerializer(projects[0]).data
            tasks = TaskSerializer(projects, many=True).data
            assignees = []
            for task in tasks:
                # temp_assignees= ProjectAssignee.objects.filter(project_id=task['id'])
                task_assignees = ProjectAssigneeSerializer(ProjectAssignee.objects.filter(project_id=task['id']),
                                                           many=True).data
                task['assignees'] = task_assignees
                for task_assignee in task_assignees:
                    assignees.append(
                        UserDetailSerializer(CustomUser.objects.get(pk=task_assignee['assignee']['id'])).data)

            assignees = unique(assignees)
            response_data = {
                # "tdo": subtask["task_delivery_order"],
                "project": serialized_subtask,
                "subtasks": tasks,
                "assignees": assignees
            }
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'Project Details',
                        'data': response_data}

        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
        return Response(response)


# project details
class ProjectDetails(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            results = []
            projects = Projects.objects.filter(work_package_number=pk)
            for project in projects:
                temp_data = {
                    "project": {},
                    "assignee": []
                }
                serializer = ProjectDetailsSerializer(project)
                temp_data["projects"] = serializer.data
                assignees = ProjectAssignee.objects.filter(project=project.id)
                for assignee in assignees:
                    assignee_serializer = ProjectAssigneeSerializer(assignee)
                    temp_data["assignee"].append(assignee_serializer.data)
                results.append(temp_data)
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'Project Details',
                        'data': results}
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
        return Response(response, status=status.HTTP_404_NOT_FOUND)


# update project
class UpdateProject(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk, format=None):
        try:
            projects = Projects.objects.get(work_package_index=pk)
            serializer = UpdateProjectSerializer(projects, data=request.data)

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                assignees = request.data['assignee']

                for key, assignee in enumerate(assignees):
                    print(key)
                    if not ProjectAssignee.objects.filter(assignee=assignee, project=serializer.data['id']).exists():
                        temp_data = {
                            'assignee': assignee,
                            'estimated_person': request.data['estimated_person'][int(key)],
                            'is_assignee_active': 1,
                            'project': serializer.data['id'],
                            'date_created': datetime.datetime.now(),
                            'date_updated': datetime.datetime.now()
                        }
                        serializer2 = CreateProjectAssigneeSerializer(data=temp_data)
                        if serializer2.is_valid(raise_exception=True):
                            serializer2.save()
                            user_email = UserDetailSerializer(CustomUser.objects.get(id=assignee)).data['email']
                            print(serializer.data)
                            wp_index = SubTaskSerializer(Projects.objects.get(id=serializer.data['id'])).data[
                                'work_package_index']
                            send_update_project_email(user_email,
                                                      UserDetailSerializer(CustomUser.objects.get(id=assignee)).data[
                                                          'first_name'],
                                                      'https://virtualoffice.com.bd/#/login/?task_details=' + wp_index)

                    else:
                        ProjectAssignee.objects.filter(assignee=assignee, project=serializer.data['id']).update(
                            estimated_person=request.data['estimated_person'][int(key)])

                all_assignees = ProjectAssigneeSerializer(ProjectAssignee.objects.filter(project=serializer.data['id']),
                                                          many=True).data
                for assignee in all_assignees:
                    if str(assignee['assignee']['id']) not in assignees:
                        ProjectAssignee.objects.filter(assignee=assignee['assignee']['id'],
                                                       project=serializer.data['id']).delete()

                response = {
                    'success': 'True',
                    'status code': status.HTTP_200_OK,
                    'message': 'Project Updated Successful',
                    'data': serializer.data
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


# class PmProjectAllAssigneeList(APIView):
#     permission_classes = (IsAuthenticated,)
#
#     def get(self, request, pk):
#         try:
#             tasks = Projects.objects.filter(pm=pk)
#             assignees = []
#             for task in tasks:
#                 temp_assignees = ProjectAssigneeSerializer(ProjectAssignee.objects.filter(project=task.id),
#                                                            many=True).data
#                 for item in temp_assignees:
#                     assignees.append(UserDetailSerializer(CustomUser.objects.get(pk=item['assignee']['id'])).data)
#             assignees = unique(assignees)
#             response = {
#                 'success': 'True',
#                 'status code': status.HTTP_200_OK,
#                 'message': 'My Heroes',
#                 'data': assignees,
#                 'user': UserDetailSerializer(request.user).data
#             }
#             return Response(response, status=status.HTTP_200_OK)
#             # return Response(assignees)
#         except Exception as e:
#             response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
#             return Response(response)


class PmProjectAllAssigneeList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            tasks = Projects.objects.filter(pm=pk).prefetch_related(
                Prefetch('project_assignee', queryset=ProjectAssignee.objects.select_related('assignee'))
            )

            assignees_set = set()
            for task in tasks:
                assignees_set.update(item['assignee'] for item in task.project_assignee.values('assignee'))

            assignees = []
            for assignee_id in assignees_set:
                assignee = CustomUser.objects.get(pk=assignee_id)
                assignees.append(UserDetailSerializer(assignee).data)

            response = {
                'success': 'True',
                'status code': status.HTTP_200_OK,
                'message': 'My Heroes',
                'data': assignees,
                'user': UserDetailSerializer(request.user).data
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


# pm wise project list
class PmProjectList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            projects_data = []
            traversed_projects = []
            assigned_projects = Projects.objects.filter(pm=pk).order_by("sub_task")
            for project in assigned_projects:
                temp_project = project
                if temp_project.work_package_number not in traversed_projects:
                    traversed_projects.append(temp_project.work_package_number)
                    subtask_query_set = Projects.objects.filter(work_package_number=temp_project.work_package_number)
                    # print('subtasks',subtask_query_set)
                    subtasks = []
                    assignees = []
                    if len(subtask_query_set) > 0:
                        for task in subtask_query_set:
                            serialized_task = TaskSerializer(task).data
                            temp_assignees = ProjectAssigneeSerializer(ProjectAssignee.objects.filter(project=task.id),
                                                                       many=True).data
                            serialized_task['assignees'] = temp_assignees
                            subtasks.append(serialized_task)
                            for assignee in temp_assignees:
                                assignees.append(
                                    UserDetailSerializer(CustomUser.objects.get(pk=assignee['assignee']['id'])).data)

                    unique_assignees = unique(assignees)
                    serializer = ProjectDetailsSerializer(temp_project)
                    # print(assignees)
                    temp_data = {
                        'assignees': unique_assignees,
                        'project': serializer.data,
                        'subtasks': subtasks
                    }
                    projects_data.append(temp_data)
            response = {'success': 'True', 'status code': status.HTTP_200_OK,
                        'message': 'Assigned Project List for a pm',
                        'data': projects_data}
            return Response(response)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
        return Response(response)



class AllProjectList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            projects_data = []
            traversed_projects = []
            assigned_projects = Projects.objects.all().order_by("sub_task")
            for project in assigned_projects:
                temp_project = project
                if temp_project.work_package_number not in traversed_projects:
                    traversed_projects.append(temp_project.work_package_number)
                    subtask_query_set = Projects.objects.filter(work_package_number=temp_project.work_package_number)
                    # print('subtasks',subtask_query_set)
                    subtasks = []
                    assignees = []
                    if len(subtask_query_set) > 0:
                        for task in subtask_query_set:
                            serialized_task = TaskSerializer(task).data
                            temp_assignees = ProjectAssigneeSerializer(ProjectAssignee.objects.filter(project=task.id),
                                                                       many=True).data
                            serialized_task['assignees'] = temp_assignees
                            subtasks.append(serialized_task)
                            for assignee in temp_assignees:
                                assignees.append(
                                    UserDetailSerializer(CustomUser.objects.get(pk=assignee['assignee']['id'])).data)

                    unique_assignees = unique(assignees)
                    serializer = ProjectDetailsSerializer(temp_project)
                    # print(assignees)
                    temp_data = {
                        'assignees': unique_assignees,
                        'project': serializer.data,
                        'subtasks': subtasks
                    }
                    projects_data.append(temp_data)
            response = {'success': 'True', 'status code': status.HTTP_200_OK,
                        'message': 'All Project List',
                        'data': projects_data,
                        'length' : len(projects_data)}
            return Response(response)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
        return Response(response)


# assigned project list for employee
class AssignedProjectList(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk):
        try:
            projects_data = []
            traversed_projects = []
            assigned_projects = ProjectAssignee.objects.filter(assignee=pk).select_related('project')
            for project in assigned_projects:
                temp_project = Projects.objects.get(pk=project.project_id)
                if temp_project.work_package_number not in traversed_projects:
                    traversed_projects.append(temp_project.work_package_number)
                    subtask_query_set = Projects.objects.filter(work_package_number=temp_project.work_package_number)
                    # print('subtasks',subtask_query_set)
                    subtasks = []
                    assignees = []
                    if len(subtask_query_set) > 0:
                        for task in subtask_query_set:
                            serialized_task = TaskSerializer(task).data
                            temp_assignees = ProjectAssigneeSerializer(ProjectAssignee.objects.filter(project=task.id),
                                                                       many=True).data
                            serialized_task['assignees'] = temp_assignees
                            subtasks.append(serialized_task)
                            for assignee in temp_assignees:
                                assignees.append(
                                    UserDetailSerializer(CustomUser.objects.get(pk=assignee['assignee']['id'])).data)

                    unique_assignees = unique(assignees)
                    serializer = ProjectDetailsSerializer(temp_project)
                    # print(assignees)
                    temp_data = {
                        'assignees': unique_assignees,
                        'project': serializer.data,
                        'subtasks': subtasks,
                        'sub_task': serializer.data['sub_task']
                    }
                    projects_data.append(temp_data)
            response = {'success': 'True', 'status code': status.HTTP_200_OK,
                        'message': 'Assigned Project List for an employee',
                        'data': projects_data}
            return Response(response)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
        return Response(response)


class ChangePM(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        try:
            Projects.objects.filter(work_package_number=request.data['wp']).update(pm=request.data['pm'])
            response = {'success': 'True', 'status code': status.HTTP_200_OK,
                        'message': 'Project Manager changed'}
            return Response(response)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


# assigned project list for employee
class ProjectWiseFileList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            serializerData = []
            user_info = CustomUser.objects.get(id=pk)
            if user_info.groups.filter(name='employee').exists():
                project_list = Projects.objects.values('work_package_number').distinct()
                for project_info in project_list:
                    project_details = Projects.objects.filter(
                        work_package_number=project_info['work_package_number']).first()
                    projectAssigneeInfo = ProjectAssignee.objects.get(assignee=pk, project=project_details.id)
                    if projectAssigneeInfo:
                        project_ids = projectAssigneeInfo.project_id
                        projectInfo = Projects.objects.get(id=project_ids)
                        file_info = ProjectSharedFiles.objects.filter(
                            work_package_number=projectInfo.work_package_number)
                        file_serializer = DocumentListSerializer(file_info, many=True)
                        serilizer = ProjectDetailsSerializer(projectInfo)
                        total_serializer = {"project": serilizer.data, "files": file_serializer.data}
                        serializerData.append(total_serializer)

            if user_info.groups.filter(name='pm').exists():
                project_list = Projects.objects.values('work_package_number').distinct()

                for project_info in project_list:
                    project_details = Projects.objects.filter(
                        work_package_number=project_info['work_package_number']).first()
                    projectAssigneeInfo = ProjectAssignee.objects.get(assignee=pk, project=project_details.id)
                    if projectAssigneeInfo:
                        project_ids = projectAssigneeInfo.project_id
                        projectInfo = Projects.objects.get(id=project_ids)
                        file_info = ProjectSharedFiles.objects.filter(
                            work_package_number=projectInfo.work_package_number)
                        file_serializer = DocumentListSerializer(file_info, many=True)
                        serilizer = ProjectDetailsSerializer(projectInfo)

                        assignee_serilizer = {"project": serilizer.data, "files": file_serializer.data}
                    pm_project_list = Projects.objects.filter(id=projectAssigneeInfo.project_id, pm=pk).first()
                    if projectAssigneeInfo.assignee != pm_project_list.pm:
                        projectInfo = Projects.objects.get(id=pm_project_list.id)
                        file_info = ProjectSharedFiles.objects.filter(
                            work_package_number=projectInfo.work_package_number)
                        pmfile_serializer = DocumentListSerializer(file_info, many=True)
                        pmserilizer = ProjectDetailsSerializer(projectInfo)
                        serializerData = {"project": pmserilizer.data, "files": pmfile_serializer.data}
                    serializerData.append(assignee_serilizer)

            response = {'success': 'True', 'status code': status.HTTP_200_OK,
                        'message': 'Shared Document List For Each Project',
                        'data': serializerData}
            return Response(response)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
        return Response(response)


class ProjectWiseFileInsert(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        work_package_number = request.data.get('work_package_number')
        upload_by = request.data.get('upload_by')
        files = int(request.data.get('files')) + 1

        for i in range(1, files):
            indexval = str(i)
            attribute_name = str('file' + indexval)
            file = request.data.get(attribute_name)
            requested_data = {"work_package_number": work_package_number, "file": file, "upload_by": upload_by}
            serializer = ProjectFileSerializer(data=requested_data)
            if serializer.is_valid():
                serializer.save()
            else:
                serializer.errors()
        response = {
            'success': 'True',
            'status code': status.HTTP_200_OK,
            'message': 'Document Insert Successful'
        }
        return Response(response)


class ChangeProjectStatus(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        try:
            Projects.objects.filter(work_package_number=pk).update(status=request.data['status'])
            response = {'success': 'True', 'status code': status.HTTP_200_OK,
                        'message': 'Project Status updated',
                        }
            return Response(response)

        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


class RemoveAssignee(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        try:
            print(request.data)
            # print(ProjectAssignee.objects.filter(assignee=request.data['assignee'], project=request.data['project']))
            ProjectAssignee.objects.filter(assignee=request.data['assignee'], project=request.data['project']).delete()
            response = {'success': 'True', 'status code': status.HTTP_200_OK,
                        'message': 'Assignee removed',
                        }
            return Response(response)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


# assignee list of a project
class ProjectAssigneeList(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk):
        try:
            project = ProjectDetailsSerializer(Projects.objects.get(work_package_index=pk)).data

            assignees = ProjectAssigneeSerializer(ProjectAssignee.objects.filter(project=project['id']), many=True).data
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'project assignee list',
                        'data': assignees}
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
        return Response(response)


class DateToDate(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, from_date, to_date):
        print(from_date, to_date)
        try:
            hours = calculate_hours_from_date_to_date(from_date, to_date)

            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'project assignee list',
                        'total_hours': hours}
            return Response(response)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


class NoWBSList(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, from_date, to_date):
        try:
            hours = calculate_hours_from_date_to_date(from_date, to_date)

            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'project assignee list',
                        'total_hours': hours}
            return Response(response)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


class DeleteSubTask(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, work_package_index):
        try:
            Projects.objects.filter(work_package_index=work_package_index).delete()
            response = {'success': 'True', 'status code': status.HTTP_200_OK,
                        'message': 'Sub Task has been deleted'}
            return Response(response)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


class ChangeTDOTitle(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        try:
            tdo = Tdo.objects.get(pk=pk)
            tdo.title = request.data['title']
            tdo.save()
            response = {'success': 'True', 'status code': status.HTTP_200_OK,
                        'message': 'Task Delivery order name has been changed'}
            return Response(response)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


class TdoList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        try:
            user = UserDetailSerializer(request.user).data
            user_company = user['slc_details']['slc']['department']['company']['id']
            tdo_list = Tdo.objects.filter(company=user_company)
            serialized_data = TdoSerializer(tdo_list, many=True)
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'data': serialized_data.data}
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


class ProjectManagerList(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        all_pm = UserDetailSerializer(CustomUser.objects.filter(groups__name='pm'), many=True).data
        response = {
            'success': 'True',
            'status code': status.HTTP_200_OK,
            'message': 'Project Manager List',
            'data': all_pm
        }
        return Response(response)


class WPList(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            work_package_numbers = Projects.objects.values_list('work_package_number', flat=True).distinct()
            sub_tasks = Projects.objects.values_list('sub_task', flat=True)
            wp_nums = []
            for item in work_package_numbers:
                wp_nums.append(item)

            if len(wp_nums) == 0:
                wp_nums.append(1000)

            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'wp': wp_nums,
                        'sub_tasks': unique(sub_tasks)}
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


class CheckWPandSubTask(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, sub_task, wp):
        try:
            wp_exists = False
            sub_task_exixts = False
            if Projects.objects.filter(work_package_number=wp).exists():
                wp_exists = True

            if Projects.objects.filter(sub_task=sub_task).exists():
                sub_task_exixts = True
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'wp_found': wp_exists,
                        'sub_task_found': sub_task_exixts}
            return Response(response)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


class AllProjectFiles(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            files = DocumentListSerializer(ProjectSharedFiles.objects.all(), many=True).data
            response = {
                'success': 'True',
                'status code': status.HTTP_200_OK,
                'message': 'Project Manager List',
                'data': files
            }
            return Response(response)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


# class ProjectDetails(APIView):
#     permission_classes = (IsAuthenticated,)

#     def get(self, request, pk):
#         try:
#             results = []
#             projects = Projects.objects.filter(work_package_number=pk)
#             for project in projects:
#                 temp_data = {
#                     "project": {},
#                     "assignee": []
#                 }
#                 serializer = ProjectDetailsSerializer(project)
#                 temp_data["projects"] = serializer.data
#                 assignees = ProjectAssignee.objects.filter(project=project.id)
#                 for assignee in assignees:
#                     assignee_serializer = ProjectAssigneeSerializer(assignee)
#                     temp_data["assignee"].append(assignee_serializer.data)
#                 results.append(temp_data)
#             response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'Project Details',
#                         'data': results}
#         except Exception as e:
#             response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
#         return Response(response, status=status.HTTP_404_NOT_FOUND)


class assigneesWithNoWbs(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user = UserDetailSerializer(request.user).data
            results = []
            projects = Projects.objects.filter(pm=user['id'])

            for project in projects:
                temp_data = {"project": ProjectDetailsSerializer(project).data, "assignees": [], "allassignees": []}

                assignees = ProjectAssignee.objects.filter(project=project.id)
                allassignee = ProjectAssignee.objects.all()
                for assignee in assignees:
                    print(assignee.assignee.id)
                    wbs_list = Wbs.objects.filter(assignee=assignee.assignee.id, project=project.id)
                    # print(len(wbs_list))
                    assignee_serializer = ProjectAssigneeSerializer(assignee)
                    temp_data["allassignees"].append(assignee_serializer.data)
                    if len(wbs_list) == 0:
                        assignee_serializer = ProjectAssigneeSerializer(assignee)
                        temp_data["assignees"].append(assignee_serializer.data)

                results.append(temp_data)
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'Project Details',
                        'data': results, }

            return Response(response)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


class AssigneesWithNoWbsRapid(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:

            current_date = timezone.now().date()
            user = UserDetailRapidSerializer(request.user).data
            results = []
            projects_vo = Projects.objects.prefetch_related('project_assignee').filter(pm=user['id']).filter(planned_delivery_date__gte=current_date)

            for project in projects_vo:
                temp_data = {"project": ProjectDetailsSerializerRapid(project).data, "assignees": [], "allassignees": []}

                assignees = project.project_assignee.select_related('assignee').filter(project=project.id)
                for assignee in assignees:
                    wbs_list = Wbs.objects.filter(assignee=assignee.assignee.id, project=project.id).count()
                    assignee_serializer = ProjectAssigneeRapidSerializer(assignee)
                    temp_data["allassignees"].append(assignee_serializer.data)
                    if wbs_list == 0:
                        assignee_serializer = ProjectAssigneeRapidSerializer(assignee)
                        temp_data["assignees"].append(assignee_serializer.data)

                results.append(temp_data)
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'Project Details',
                        'data': results, }

            return Response(response)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


class AssigneesWithNoWbsUser(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user = UserDetailSerializer2(request.user).data
            results = []
            # projects = Projects.objects.filter(pm=user['id'])
            projects = Projects.objects.filter(project_assignee__assignee__id=user['id'])

            for project in projects:
                temp_data = {"project": ProjectDetailsSerializer(project).data, "assignees": [], "allassignees": []}

                assignees = ProjectAssignee.objects.filter(project=project.id)
                allassignee = ProjectAssignee.objects.all()
                for assignee in assignees:
                    # print(assignee.assignee.id)
                    wbs_list = Wbs.objects.filter(assignee=assignee.assignee.id, project=project.id)
                    # print(len(wbs_list))
                    assignee_serializer = ProjectAssigneeSerializer2(assignee)
                    temp_data["allassignees"].append(assignee_serializer.data)
                    if len(wbs_list) == 0:
                        assignee_serializer = ProjectAssigneeSerializer2(assignee)
                        temp_data["assignees"].append(assignee_serializer.data)

                results.append(temp_data)
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'Project Details',
                        'data': results, }

            return Response(response)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


class UpdateProjectDates(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            subtask = Projects.objects.filter(work_package_index=request.data['work_package_index']).update(
                start_date=request.data['start_date'], planned_delivery_date=request.data['planned_delivery_date'])
            response = {'success': 'True', 'status code': status.HTTP_200_OK, 'message': 'Project Updated'}
            return Response(response)

        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response)


# Ron pm wise project list OBSOLETE
# class RonPmProjectList(APIView):
#     permission_classes = (IsAuthenticated,)
#     def get(self, request, pk):
#         try:
#             projects_data = []
#             traversed_projects = []
#             tdo_names = []
#             tdo_finder = {}
#             count = 0
#             assigned_projects = Projects.objects.filter(pm=pk).order_by("sub_task")
#             # assinged_projects: think it as 'project_manager_created_projects'
#             for project in assigned_projects:
#                 temp_project = project
#
#                 if temp_project.work_package_number not in traversed_projects:
#                     traversed_projects.append(temp_project.work_package_number)
#                     subtask_query_set = Projects.objects.filter(work_package_number=temp_project.work_package_number)
#                     # print('subtasks',subtask_query_set)
#                     subtasks = []
#                     assignees = []
#                     if len(subtask_query_set) > 0:
#                         for task in subtask_query_set:
#                             serialized_task = TaskSerializer(task).data
#                             temp_assignees = ProjectAssigneeSerializer(ProjectAssignee.objects.filter(project=task.id),
#                                                                     many=True).data
#                             serialized_task['assignees'] = temp_assignees
#                             subtasks.append(serialized_task)
#                             for assignee in temp_assignees:
#                                 assignees.append(
#                                     UserDetailSerializer(CustomUser.objects.get(pk=assignee['assignee']['id'])).data)
#
#                     unique_assignees = unique(assignees)
#                     serializer = ProjectDetailsSerializer(temp_project)
#                     if temp_project.task_delivery_order_id not in tdo_names:
#                         tdo_names.append(temp_project.task_delivery_order_id)
#                         temp_data = {
#                             'assignees': [unique_assignees],
#                             'project': [serializer.data],
#                             'subtasks': [subtasks]
#                         }
#                         projects_data.append(temp_data)
#                         tdo_finder.update({temp_project.task_delivery_order_id: count})
#                         count += 1
#
#                     else:
#                         index = temp_project.task_delivery_order_id
#                         projects_data[tdo_finder[index]]['assignees'].append(unique_assignees)
#                         projects_data[tdo_finder[index]]['project'].append(serializer.data)
#                         projects_data[tdo_finder[index]]['subtasks'].append(subtasks)
#
#             response = {
#                         'success': 'True',
#                         'status code': status.HTTP_200_OK,
#                         'message': 'Assigned Project List for a pm',
#                         'data': projects_data
#                         }
#             return Response(response)
#         except Exception as e:
#             response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
#
#         return Response(response)
#
#
# # Fixed Ron

def y():
    pass

# class FixRonPmProjectList(APIView):
#     permission_classes = (IsAuthenticated,)
#     def get(self, request, pk):
#         try:
#             projects_data = []
#             traversed_projects = []
#             tdo_names = []
#             tdo_finder = {}
#             count = 0
#             assigned_projects = Projects.objects.filter(pm=pk).order_by("sub_task")
#             # assinged_projects: think it as 'project_manager_created_projects'
#             for project in assigned_projects:
#                 temp_project = project
#
#                 if temp_project.work_package_number not in traversed_projects:
#                     traversed_projects.append(temp_project.work_package_number)
#                     subtask_query_set = Projects.objects.filter(work_package_number=temp_project.work_package_number)
#                     # print('subtasks',subtask_query_set)
#                     subtasks = []
#                     assignees = []
#                     if len(subtask_query_set) > 0:
#                         for task in subtask_query_set:
#                             serialized_task = TaskSerializer(task).data
#                             temp_assignees = ProjectAssigneeSerializer(ProjectAssignee.objects.filter(project=task.id),
#                                                                     many=True).data
#                             serialized_task['assignees'] = temp_assignees
#                             subtasks.append(serialized_task)
#                             for assignee in temp_assignees:
#                                 assignees.append(
#                                     UserDetailSerializer(CustomUser.objects.get(pk=assignee['assignee']['id'])).data)
#
#                     unique_assignees = unique(assignees)
#                     serializer = ProjectDetailsSerializer(temp_project)
#                     if temp_project.task_delivery_order_id not in tdo_names:
#                         tdo_names.append(temp_project.task_delivery_order_id)
#                         temp_data = {
#                             'id': temp_project.task_delivery_order_id,
#                             'title': temp_project.task_delivery_order.title,
#                             'projects': [
#                                 {
#                                     'assignees': unique_assignees,
#                                     'project': serializer.data,
#                                     'subtasks': subtasks
#                                 }
#                             ]
#                         }
#                         projects_data.append(temp_data)
#                         tdo_finder.update({temp_project.task_delivery_order_id: count})
#                         count += 1
#
#                     else:
#                         index = temp_project.task_delivery_order_id
#
#                         # projects_data[tdo_finder[index]]['assignees'].append(unique_assignees)
#                         projects_data[tdo_finder[index]]['projects'].append(
#                             {
#                                 'assignees': unique_assignees,
#                                 'project': serializer.data,
#                                 'subtasks': subtasks,
#                             }
#                         )
#
#             response = {
#                         'success': 'True',
#                         'status code': status.HTTP_200_OK,
#                         'message': 'Assigned Project List for a pm',
#                         'data': projects_data
#                         }
#             return Response(response)
#         except Exception as e:
#             response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
#
#         return Response(response)


def x():
    pass


# class FixRonPmProjectList(APIView):
#     permission_classes = (IsAuthenticated,)
#
#     def get(self, request, pk):
#         try:
#             projects_data = []
#             traversed_projects = {}
#             tdo_names = {}
#             tdo_finder = {}
#             count = 0
#
#             assigned_projects = Projects.objects.filter(pm=pk).order_by("sub_task").select_related('task_delivery_order').prefetch_related('project_assignee')
#
#             for project in assigned_projects:
#                 temp_project = project
#
#                 if temp_project.work_package_number not in traversed_projects:
#                     traversed_projects[temp_project.work_package_number] = True
#                     subtask_query_set = Projects.objects.filter(work_package_number=temp_project.work_package_number)
#                     subtasks = []
#                     assignees = []
#
#                     if subtask_query_set.exists():
#                         for task in subtask_query_set:
#                             serialized_task = TaskSerializer(task).data
#                             temp_assignees = ProjectAssigneeSerializer(ProjectAssignee.objects.filter(project=task.id), many=True).data
#                             serialized_task['assignees'] = temp_assignees
#                             subtasks.append(serialized_task)
#                             for assignee in temp_assignees:
#                                 assignees.append(UserDetailSerializer(CustomUser.objects.get(pk=assignee['assignee']['id'])).data)
#
#                     unique_assignees = list({assignee['id']: assignee for assignee in assignees}.values())
#                     serializer = ProjectDetailsSerializer(temp_project)
#
#                     if temp_project.task_delivery_order_id not in tdo_names:
#                         tdo_names[temp_project.task_delivery_order_id] = True
#                         temp_data = {
#                             'id': temp_project.task_delivery_order_id,
#                             'title': temp_project.task_delivery_order.title,
#                             'projects': [
#                                 {
#                                     'assignees': unique_assignees,
#                                     'project': serializer.data,
#                                     'subtasks': subtasks
#                                 }
#                             ]
#                         }
#                         projects_data.append(temp_data)
#                         tdo_finder[temp_project.task_delivery_order_id] = count
#                         count += 1
#                     else:
#                         index = temp_project.task_delivery_order_id
#                         projects_data[tdo_finder[index]]['projects'].append(
#                             {
#                                 'assignees': unique_assignees,
#                                 'project': serializer.data,
#                                 'subtasks': subtasks,
#                             }
#                         )
#
#             response = {
#                 'success': 'True',
#                 'status code': status.HTTP_200_OK,
#                 'message': 'Assigned Project List for a pm',
#                 'data': projects_data
#             }
#             return Response(response)
#         except Exception as e:
#             response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
#
#         return Response(response)

def z():
    pass


class FixRonPmProjectList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            projects_data = []
            traversed_projects = {}
            tdo_names = {}
            tdo_finder = {}
            count = 0

            # assigned_projects = Projects.objects.filter(pm=pk).order_by("sub_task").prefetch_related('project_assignee', 'task_delivery_order')
            assigned_projects = Projects.objects.all().order_by("sub_task").prefetch_related('project_assignee', 'task_delivery_order')

            # Fetch all related data in a single query
            subtask_query_set = Projects.objects.filter(work_package_number__in=[p.work_package_number for p in assigned_projects]).prefetch_related('project_assignee')

            for project in assigned_projects:
                temp_project = project

                if temp_project.work_package_number not in traversed_projects:
                    traversed_projects[temp_project.work_package_number] = True
                    subtasks = []
                    assignees = []

                    # Fetch subtasks and assignees from the pre-fetched query set
                    for task in subtask_query_set:
                        if task.work_package_number == temp_project.work_package_number:
                            serialized_task = TaskSerializer(task).data
                            temp_assignees = ProjectAssigneeSerializer2(task.project_assignee.all(), many=True).data
                            serialized_task['assignees'] = temp_assignees
                            subtasks.append(serialized_task)
                            for assignee in temp_assignees:
                                user = CustomUser.objects.get(pk=assignee['assignee']['id'])
                                assignees.append(UserDetailSerializer2(user).data)

                    unique_assignees = list({assignee['id']: assignee for assignee in assignees}.values())
                    serializer = ProjectDetailsSerializer(temp_project)

                    if temp_project.task_delivery_order_id not in tdo_names:
                        tdo_names[temp_project.task_delivery_order_id] = True
                        temp_data = {
                            'id': temp_project.task_delivery_order_id,
                            'title': temp_project.task_delivery_order.title if temp_project.task_delivery_order else None,
                            'projects': [
                                {
                                    'assignees': unique_assignees,
                                    'project': serializer.data,
                                    'subtasks': subtasks
                                }
                            ]
                        }
                        projects_data.append(temp_data)
                        tdo_finder[temp_project.task_delivery_order_id] = count
                        count += 1
                    else:
                        index = temp_project.task_delivery_order_id
                        projects_data[tdo_finder[index]]['projects'].append(
                            {
                                'assignees': unique_assignees,
                                'project': serializer.data,
                                'subtasks': subtasks,
                            }
                        )

            response = {
                'success': 'True',
                'status code': status.HTTP_200_OK,
                'message': 'Assigned Project List for a pm',
                'data': projects_data
            }
            return Response(response)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)

        return Response(response)






class TdoIndex(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, idx):
        try:
            projects_data = []
            traversed_projects = []
            tdo_names = []
            tdo_finder = {}
            count = 0
            company_name = ""
            assigned_projects = Projects.objects.order_by("sub_task")
            for project in assigned_projects:
                if idx == project.task_delivery_order_id:
                    temp_project = project
                    company_name = temp_project.task_delivery_order.title
                    
                    if temp_project.task_delivery_order_id not in traversed_projects:
                        traversed_projects.append(temp_project.work_package_number)
                        subtask_query_set = Projects.objects.filter(work_package_number=temp_project.work_package_number)
                        subtasks = []
                        assignees = []
                        if len(subtask_query_set) > 0:
                            for task in subtask_query_set:
                                serialized_task = TaskSerializer(task).data
                                temp_assignees = ProjectAssigneeSerializer(ProjectAssignee.objects.filter(project=task.id),
                                                                        many=True).data
                                serialized_task['assignees'] = temp_assignees
                                subtasks.append(serialized_task)
                                for assignee in temp_assignees:
                                    assignees.append(
                                        UserDetailSerializer(CustomUser.objects.get(pk=assignee['assignee']['id'])).data)

                        unique_assignees = unique(assignees)
                        serializer = ProjectDetailsSerializer(temp_project)
                        if temp_project.task_delivery_order_id not in tdo_names:
                            tdo_names.append(temp_project.task_delivery_order_id)
                            temp_data = {
                                'id': temp_project.task_delivery_order_id,
                                'title': temp_project.task_delivery_order.title,
                                'projects': [
                                    {
                                        'assignees': unique_assignees,
                                        'project': serializer.data,
                                        'subtasks': subtasks
                                    }
                                ]
                            }
                            projects_data.append(temp_data)
                            tdo_finder.update({temp_project.task_delivery_order_id: count})
                            count += 1

                        else:
                            index = temp_project.task_delivery_order_id
                            projects_data[tdo_finder[index]]['projects'].append(
                                {
                                    'assignees': unique_assignees,
                                    'project': serializer.data,
                                    'subtasks': subtasks,
                                }
                            )   

            response = {
                        'success': 'True',
                        'status code': status.HTTP_200_OK,
                        'message': 'Project List for ' + company_name,
                        'data': projects_data
                        }
            return Response(response)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e) 

        return Response(response) 

