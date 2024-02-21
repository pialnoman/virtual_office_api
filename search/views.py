import itertools

from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from meetings.models import Meetings
from meetings.serializers import MeetingsDetailsSerializer
from projects.models import Projects, ProjectAssignee
from projects.serializers import ProjectDetailsSerializer, TaskSerializer, ProjectAssigneeSerializer
from projects.views import unique
from users.models import CustomUser
from users.serializers import UserDetailSerializer


class Search(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            models = {
                'user': 'CustomUser',
                'project': 'Projects'
            }
            key = request.GET.get('key')
            users = UserDetailSerializer(CustomUser.objects.filter(Q(first_name__icontains=key) | Q(last_name__icontains=key)), many=True).data
            projects = ProjectDetailsSerializer(Projects.objects.filter(Q(sub_task__icontains=key) | Q(task_title__icontains=key)), many=True).data
            #meetings = MeetingsDetailsSerializer(Meetings.objects.filter(Q(sub_task__icontains=key) | Q(task_title__icontains=key)), many=True).data

            result = {
                'employees': users,
                'projects': build_projects_data(projects)
            }

            response = {
                'success': True,
                'status code': status.HTTP_200_OK,
                'data': result
            }
            # return Response(response)
        except Exception as e:
            print("line 52")
            response = {
                'success': 'False',
                'status code': status.HTTP_400_BAD_REQUEST,
                'message': str(e),
            }
            print(str(e))

        return Response(response)


def build_projects_data(projects):
    projects_data = []
    traversed_projects = []
    for project in projects:
        print(project['id'])
        temp_project = Projects.objects.get(pk=project['id'])
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

    return projects_data

