from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from projects.models import Projects
from users.models import CustomUser


class Meetings(models.Model):
    class MediumType(models.IntegerChoices):
        PHYSICAL = '0', _('PHYSICAL')
        VIRTUAL = '1', _('VIRTUAL')

    class MeetingType(models.IntegerChoices):
        PROJECT = '0', _('PROJECT')
        GENERAL = '1', _('GENERAL')

    room_id = models.CharField(max_length=12, blank=True, null=True)
    participant = models.CharField(max_length=100, blank=True, null=True)
    # project = models.ForeignKey(Projects, to_field="work_package_number",db_column="work_package_number",related_name="meeting_project_details", blank=True, null=True,
    #                              on_delete=models.CASCADE)
    project = models.CharField(_('meeting_project'), max_length=50, blank=True, null=True)
    room_name= models.CharField(_('room name'), max_length=50, blank=True)
    medium = models.IntegerField(_('meeting medium'), choices=MediumType.choices, default=MediumType.PHYSICAL)
    type = models.IntegerField(_('meeting type'), choices=MeetingType.choices, default=MeetingType.PROJECT)
    agenda = models.TextField(_('meeting agenda'), max_length=150, blank=True)
    comments =  models.TextField(_('meeting comments'), max_length=150, blank=True)
    start_time = models.DateTimeField(_('meeting start time'), blank=False)
    end_time = models.DateTimeField(_('meeting end time'), blank=True, null=True)
    duration = models.IntegerField(_('planned value'), blank=True, null=True)
    host = models.ForeignKey(CustomUser, related_name="host", blank=True, null=True, on_delete=models.CASCADE)
    date_created = models.DateField(_('date created'), default=timezone.now)
    date_updated = models.DateField(_('date updated'), default=timezone.now)

    class Meta:
        db_table = 'meeting'
        verbose_name = _('meeting')
        verbose_name_plural = _('meetings')

    def __str__(self):
        return self.project.room_id
