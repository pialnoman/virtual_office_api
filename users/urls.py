from django.urls import path
from .views import ChangePassword, Login, Logout, Register, UserDetail, UserUpdate, ChangeProfileImage, \
    PossibleAssigneeList, AllPermissions

urlpatterns = [
    path('register/', Register.as_view()),
    path('login/', Login.as_view()),
    path('logout/', Logout.as_view()),
    path('profile/details/<str:pk>/', UserDetail.as_view(), name="User_details"),
    path('profile/update/<str:pk>/', UserUpdate.as_view(), name="User_update"),
    path('change/password/', ChangePassword.as_view(), name="User_update"),
    path('change/profile/image/<str:pk>/', ChangeProfileImage.as_view(), name="Change_profile_image"),
    path('assignee/list/', PossibleAssigneeList.as_view()),
    path('permissions/all/', AllPermissions.as_view(), name="all_permissions"),
    # path('permissions/all/', AllPermissions.as_view(), name="all_permissions"),
]