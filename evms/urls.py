from django.urls import path
from .views import CreateEvms, EvmsDetails, UpdateEvms, EvmsListForPm

urlpatterns = [
    path('create/', CreateEvms.as_view()),
    path('details/<str:pk>/', EvmsDetails.as_view()),
    path('update/<str:pk>/', UpdateEvms.as_view()),
    path('list/<str:pk>/', EvmsListForPm.as_view()),
]
