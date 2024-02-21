from django.urls import path
from .views import DmaCalenderDetails, HolidayCalenderDetails, HoursSpentAndLeft,WorkTypesList

urlpatterns = [
    path('calender/all/', DmaCalenderDetails.as_view()),
    path('holiday/all/', HolidayCalenderDetails.as_view()),
    path('user/hours/used-left/<str:pk>/', HoursSpentAndLeft.as_view()),
    path('work-types/', WorkTypesList.as_view()),
]
