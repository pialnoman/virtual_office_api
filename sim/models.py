from datetime import timezone
from django.db import models
from users.models import CustomUser

class SIMCard(models.Model):
    imei_number = models.CharField(max_length=25, null=True, blank=True)
    sim_number = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15)
    activation_date = models.DateField(blank=True, null = True)
    ACTIVATION_CHOICES = (
        ('1', 'Yes'),
        ('0', 'No'),
        ('2', 'Decommissioned'),

    )
    activation_status = models.CharField(max_length=1, choices=ACTIVATION_CHOICES, default=0)
    project = models.CharField(max_length=100, null=True, blank=True)
    deployment_location = models.CharField(max_length=50, blank=True, null=True)
    assignee = models.CharField(max_length=50, blank = True, null = True)
    OPERATOR_CHOICES = (
        ("Robi", "Robi"),
        ("Grameenphone", "Grameenphone"),
        ("Airtel", "Airtel"),
        ("Banglalink", "Banglalink"),
        ("Teletalk", "Teletalk")        
    )
    remarks = models.TextField(blank=True, null = True)
    amount = models.DecimalField(max_digits=5, decimal_places=2,blank=True, null = True,default=0)
    sim_operator = models.CharField(max_length=20, choices=OPERATOR_CHOICES, blank=True, null = True)
