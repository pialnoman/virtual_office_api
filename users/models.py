from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from .managers import CustomUserManager
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.core.mail import send_mail
import sms_api
from virtual_office_API.settings import EMAIL_HOST_USER
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
# from organizations.models import Designation, Slc


class CustomUser(AbstractUser):
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=('Required. 150 characters or fewer. Letters, digits and @/./+/-/ only.'),
        error_messages={
            'unique': _("An user with that username already exists."),
        },
        null=True,
        blank=True
    )
    email = models.EmailField(_('email_address'), unique=True, null=True, blank=True)

    phone = models.CharField(_('phone_number'), max_length=15,error_messages={'unique': _("An user with this phone number already exists."),}, blank=True, unique=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    address = models.CharField(_('address'), max_length=250, blank=True)
    id_card_mac = models.CharField(_('id card mac'), max_length=250, blank=True, null=True)
    blood_group = models.CharField(_('blood group'), max_length=10, blank=True)
    profile_pic = models.ImageField(upload_to='uploads/users/images/', blank=True, null=True)
    designation = models.ForeignKey(to='organizations.Designation', blank=True, null=True, on_delete=models.CASCADE)
    slc_details = models.ForeignKey(to='organizations.Slc', related_name="user_slc_details", blank=True, null=True, on_delete=models.CASCADE)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    # USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    class Meta:
        db_table = 'auth_user'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.first_name + " " + self.last_name or self.username or self.email


@receiver(pre_save, sender=CustomUser)
def pre_save_activate_user(sender, instance, **kwargs):
    try:
        previous_data = CustomUser.objects.get(id=instance.id)
        # print(instance, previous_data.is_active, instance.is_active)
        if previous_data.is_active == 0 and previous_data.is_active != instance.is_active:
            message = "Your registered account with the email address " + instance.email + "has been activated. You " \
                                                                                           "can now login and update " \
                                                                                           "your profile. "
            # sms_api.SmsGateway.post(
            #     {
            #         'number': instance.phone,
            #         'message': message
            #     }
            # )
            send_mail('User account activation', message, EMAIL_HOST_USER, [instance.email], fail_silently=False, )
        if previous_data.is_active == 1 and previous_data.is_active != instance.is_active:
            message = "Your registered account with the email address " + instance.email + "has been deactivated. " \
                                                                                           "Please " \
                                                                                           "contact with the concern. "
            # sms_api.SmsGateway.post(
            #     {
            #         'number': instance.phone,
            #         'message': message
            #     }
            # )
            send_mail('User account deactivation', message, EMAIL_HOST_USER, [instance.email],
                      fail_silently=False, )
    except ObjectDoesNotExist:
        pass
