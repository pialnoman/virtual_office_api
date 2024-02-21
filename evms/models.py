from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from projects.models import Projects
from users.models import CustomUser


class Evms(models.Model):
    project = models.ForeignKey(Projects, related_name="evms_pro_details", blank=False, null=False,
                                on_delete=models.CASCADE)
    work_package_number = models.TextField(_('work package umber'), blank=False, null=True)
    earned_value = models.DecimalField(_('earned value'), max_digits=20, decimal_places=4, blank=False)
    actual_cost = models.DecimalField(_('actual cost'), max_digits=20, decimal_places=4, blank=False)
    estimate_at_completion = models.DecimalField(_('estimate at completion'), max_digits=20, decimal_places=4,
                                                 blank=False)
    estimate_to_completion = models.DecimalField(_('estimate to completion'), max_digits=20, decimal_places=4,
                                                 blank=False)
    variance_at_completion = models.DecimalField(_('variance at completion'), max_digits=20, decimal_places=4,
                                                 blank=True, null=True)
    budget_at_completion = models.DecimalField(_('budget at completion'), max_digits=20, decimal_places=4, blank=False)
    date_created = models.DateField(_('date created'), default=timezone.now)
    date_updated = models.DateField(_('date updated'), default=timezone.now)

    class Meta:
        db_table = 'evms'
        verbose_name = _('evms')
        verbose_name_plural = _('evmss')

    def __str__(self):
        return self.project.project
