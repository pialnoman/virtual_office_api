from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from organizations.models import Company
from users.models import CustomUser


class Tdo(models.Model):
    title = models.CharField(_('task delivery order'), max_length=50, blank=False, null=True, default=1)
    description = models.CharField(_('task delivery order details'), max_length=550, blank=True, null=True)
    company = models.ForeignKey(Company, related_name="tdo_company", blank=True, null=True, on_delete=models.CASCADE)
    date_created = models.DateTimeField(_('date created'), default=timezone.now)
    date_updated = models.DateTimeField(_('date updated'), default=timezone.now)

    class Meta:
        db_table = 'tdo'
        verbose_name = _('tdo')
        verbose_name_plural = _('tdos')

    def __str__(self):
        return self.title


class Projects(models.Model):
    class ProjectStatus(models.IntegerChoices):
        GOING = '0', _('OnGoing')
        COMPLETED = '1', _('Completed')
        HOLD = '2', _('Hold')
        CANCELLED = '3', _('Cancelled')

    task_delivery_order = models.ForeignKey(Tdo, related_name="tdo_title", blank=False, null=True,
                                            on_delete=models.CASCADE)
    sub_task = models.CharField(_('subtask name'), max_length=50, blank=True)
    description = models.TextField(_('subtask details'), blank=True,null=True)
    work_package_number = models.TextField(_('work package number'), blank=True)
    work_package_index = models.CharField(_('work package index'), max_length=550, blank=True,
                                             null=True)
    task_title = models.CharField(_('task title'), max_length=150, blank=True)
    estimated_person = models.DecimalField(_('estimated person'), max_digits=4, decimal_places=2, blank=True, default=1.0)
    start_date = models.DateField(blank=False, null=True)
    planned_delivery_date = models.DateField(blank=False, null=True)
    pm = models.ForeignKey(CustomUser, related_name="project_manager", blank=False, null=True, on_delete=models.CASCADE)
    # pl = models.ForeignKey(CustomUser, related_name="project_lead", blank=True, null=True, on_delete=models.CASCADE)
    planned_hours = models.DecimalField(_('planned hours'), max_digits=19, decimal_places=2, blank=False, null=True)
    planned_value = models.DecimalField(_('planned value'), blank=False,max_digits=19, decimal_places=2, null=True)
    remaining_hours = models.DecimalField(_('remaining hours'), max_digits=19, decimal_places=2, blank=False,null=True)
    status = models.IntegerField(_('status'), choices=ProjectStatus.choices, default=ProjectStatus.GOING)
    date_created = models.DateTimeField(_('date created'), default=timezone.now)
    date_updated = models.DateTimeField(_('date updated'), default=timezone.now, blank=True) 

    class Meta:
        db_table = 'project'
        verbose_name = _('project')
        verbose_name_plural = _('projects')
        indexes = [
            models.Index(fields=['work_package_index', ])
        ]

    def is_ongoing(self):
        return self.status in {
            self.ProjectStatus.GOING
        }


class ProjectAssignee(models.Model):
    project = models.ForeignKey(Projects, related_name="project_assignee", blank=False, null=False, on_delete=models.CASCADE)
    assignee = models.ForeignKey(CustomUser, related_name="project_assignee", blank=False, null=False, on_delete=models.CASCADE)
    estimated_person = models.CharField(_('remaining hours'), max_length=10, blank=True, null=True)
    is_assignee_active = models.BooleanField(_('assignee status'), default=True, blank=False)
    date_created = models.DateTimeField(_('date created'), default=timezone.now)
    date_updated = models.DateTimeField(_('date updated'), default=timezone.now)

    class Meta:
        db_table = 'project_assignee'
        verbose_name = _('project_assignee')
        verbose_name_plural = _('project_assignees')

    # def __str__(self):
    #     return self.assignee


class ProjectSharedFiles(models.Model):
    work_package_number = models.CharField(max_length=200, blank=True, null=True)
    file = models.FileField(upload_to='uploads/project/files/', blank=True, null=True)
    date_created = models.DateTimeField(_('date created'), default=timezone.now)
    date_updated = models.DateTimeField(_('date updated'), default=timezone.now)
    upload_by = models.ForeignKey(CustomUser, related_name="file_upload_by", blank=False, null=False, on_delete=models.CASCADE)

    class Meta:
        db_table = 'project_shared_file'
        verbose_name = _('shared_file')
        verbose_name_plural = _('shared_file')

    # def __str__(self):
    #     return self.project
