from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from projects.models import Projects
from users.models import CustomUser


class Wbs(models.Model):
    project = models.ForeignKey(Projects, related_name="wbs_pro_details", blank=True, null=False,
                                on_delete=models.CASCADE)
    work_package_number = models.TextField(null=True, blank=False)
    assignee = models.ForeignKey(CustomUser, related_name="employee_assigned", blank=True, null=False,
                                 on_delete=models.CASCADE)
    reporter = models.ForeignKey(CustomUser, related_name="wbs_reporter", blank=False, null=False,
                                 on_delete=models.CASCADE)
    title = models.CharField(_('title'), max_length=250, blank=False)
    description = models.TextField(_('description'), blank=True)
    start_date = models.DateField(_('start_date'), blank=False)
    end_date = models.DateField(_('end_date'), blank=False)
    hours_worked = models.DecimalField(_('hours_worked'), max_digits=6, decimal_places=1, blank=False)
    status = models.IntegerField(_('wbs_status'), default=True, blank=False)
    progress = models.IntegerField(_('progress percentage'), blank=False)
    comments = models.TextField(_('comments'), max_length=150, blank=True)
    deliverable = models.CharField(_('deliverable'), max_length=550, blank=True)
    date_created = models.DateField(_('date created'), default=timezone.now)
    date_updated = models.DateField(_('date updated'), default=timezone.now)

    class Meta:
        db_table = 'wbs'
        verbose_name = _('wbs')
        verbose_name_plural = _('wbss')
        indexes = [
            models.Index(fields=['title', ])
        ]
        indexes = [
            models.Index(fields=['project', ])
        ]
        indexes = [
            models.Index(fields=['assignee', ])
        ]
        indexes = [
            models.Index(fields=['reporter', ])
        ]

    def __str__(self):
        return self.title


class TimeCard(models.Model):
    project = models.ForeignKey(Projects, related_name="project_details", blank=True, null=True,
                                on_delete=models.CASCADE)
    wbs = models.ForeignKey(Wbs, related_name="wbs_details", blank=True, null=True,
                                on_delete=models.CASCADE)
    time_type = models.CharField(_('time type'), max_length=20, blank=True, null=True, default="RHR")
    submitted = models.BooleanField(_('submitted'), blank=True, null=True, default=False)
    time_card_assignee = models.ForeignKey(CustomUser, related_name="time_card_employee_assigned", blank=False, null=False,
                                 on_delete=models.CASCADE)
    actual_work_done = models.CharField(_('actual_work_done'), max_length=250, blank=True, null=True)
    hour_description = models.TextField(_('hour_description'), max_length=1050, blank=True, null=True)
    hours_today = models.DecimalField(_('hours_today'), max_digits=6, decimal_places=1, blank=False)
    date_created = models.DateField(_('date_created'), default=timezone.now)
    date_updated = models.DateField(_('date_updated'), default=timezone.now)

    class Meta:
        db_table = 'time_card'
        verbose_name = _('time_card')
        verbose_name_plural = _('time_cards')

    def __str__(self):
        return self.actual_work_done


class WeekTimeCard(models.Model):
    employee = models.ForeignKey(CustomUser, related_name="employee", blank=False, null=False,
                                 on_delete=models.CASCADE)
    week_start = models.DateField(_('week start'), default=timezone.now)
    week_end = models.DateField(_('week end'), default=timezone.now)
    total_hours = models.IntegerField(_('total_hours'), blank=False, null=False)
    time_type = models.CharField(_('time type'), max_length=20, blank=True, null=True, default="RHR")
    submitted = models.BooleanField(_('submitted'), blank=True, null=True, default=False)
    pdf_file = models.FileField(upload_to='uploads/weekly_time_cards/files/pdf', blank=True, null=True)
    approved_by=models.ForeignKey(CustomUser, related_name="approved_by", blank=True, null=True,
                                 on_delete=models.CASCADE)
    # submitted_at= models.DateTimeField(_('submitted_at'), default=datetime.now())
    submitted_at= models.DateTimeField(_('submitted_at'), default=timezone.now)
    submitted_by = models.ForeignKey(CustomUser, related_name="submitted_by", blank=False, null=False,on_delete=models.CASCADE)
    date_created = models.DateField(_('date created'), default=timezone.now)
    date_updated = models.DateField(_('date updated'), default=timezone.now)

    class Meta:
        db_table = 'weekly_time_cards'
        verbose_name = _('weekly_time_card')
        verbose_name_plural = _('weekly_time_cards')
        ordering = ('-submitted_at',)


class WbsSharedFiles(models.Model):
    wbs = models.ForeignKey(Wbs, related_name="wbs_id", blank=False, null=False, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/wbs/files/', blank=True, null=True)
    date_created = models.DateTimeField(_('date created'), default=timezone.now)
    date_updated = models.DateTimeField(_('date updated'), default=timezone.now)
    upload_by = models.ForeignKey(CustomUser, related_name="wbs_shared_file_upload_by", blank=False, null=False, on_delete=models.CASCADE)

    class Meta:
        db_table = 'wbs_shared_file'
        verbose_name = _('wbs_hared_file')
        verbose_name_plural = _('wbs_shared_files')