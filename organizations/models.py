import calendar
from hashlib import md5
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.db.models.functions import ExtractMonth
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta

from users.models import CustomUser


class Company(models.Model):
    name = models.CharField(_('Name'), max_length=150, blank=False)
    details = models.TextField(_('Description'), max_length=350, blank=True)
    website = models.CharField(_('Website'), max_length=350, blank=True)
    e_tin = models.CharField(_('eTIN'), max_length=350, blank=True)
    vat_certificate = models.CharField(_('VAT Certificate'), max_length=350, blank=True)
    incorporation_number = models.CharField(_('Incorporartion#'), max_length=350, blank=True)

    # trade_license_number = models.CharField(_('trade license number'), max_length=150, blank=True)

    class Meta:
        db_table = 'company'
        verbose_name = _('company')
        verbose_name_plural = _('Companies')

    def __str__(self):
        return self.name


class Department(models.Model):
    company = models.ForeignKey(to='organizations.Company', blank=False, null=False, on_delete=models.PROTECT)
    name = models.CharField(_('department name'), max_length=150, blank=False)
    details = models.TextField(_('department details'), max_length=350, blank=True)
    parent = models.ForeignKey('self', verbose_name='Select a department parent', null=True, blank=True,
                               related_name='children', on_delete=models.PROTECT)

    class Meta:
        db_table = 'department'
        verbose_name = _('department')
        verbose_name_plural = _('departments')

    def __str__(self):
        return self.name


class Designation(models.Model):
    department = models.ForeignKey(to='organizations.Department', blank=False, null=False, on_delete=models.PROTECT)
    name = models.CharField(_('designation name'), max_length=150, blank=False)
    details = models.TextField(_('designation details'), max_length=350, blank=True)
    parent = models.ForeignKey('self', verbose_name='Select a designation parent', null=True, blank=True,
                               related_name='children', on_delete=models.PROTECT)

    class Meta:
        db_table = 'designation'
        verbose_name = _('Labor Classification')
        verbose_name_plural = _('Labor Classification')

    def __str__(self):
        return self.name


YEAR_CHOICES = []
for r in range(2000, (datetime.now().year + 20)):
    YEAR_CHOICES.append((r, r))

MONTHS = (
    ('January', 'January'),
    ('February', 'February'),
    ('March', 'March'),
    ('April', 'April'),
    ('May', 'May'),
    ('June', 'June'),
    ('July', 'July'),
    ('August', 'August'),
    ('September', 'September'),
    ('October', 'October'),
    ('November', 'November'),
    ('December', 'December'),
)


class DmaCalender(models.Model):
    # WEEK_DAYS = (
    #     ('Saturday', 'Saturday'),
    #     ('Sunday', 'Sunday'),
    #     ('Monday', 'Monday'),
    #     ('Tuesday', 'Tuesday'),
    #     ('Wednesday', 'Wednesday'),
    #     ('Thursday', 'Thursday'),
    #     ('Friday', 'Friday'),
    # )
    # week_start_day = models.CharField(_('Select week start day'), max_length=20, choices=WEEK_DAYS, default='Select',
    #                                   blank=False, null=False)
    # week_holiday_1 = models.CharField(_('Select week holiday 1'), max_length=20, choices=WEEK_DAYS, default='Select',
    #                                   blank=False, null=False)
    # week_holiday_2 = models.CharField(_('Select week holiday 2'), max_length=20, choices=WEEK_DAYS, default='Select',
    #                                   blank=False, null=True)
    # government_holidays = models.IntegerField(_('government holidays'), blank=True, null=True)
    # company_reserved_holidays = models.IntegerField(_('company\'s reserved holidays'), blank=True, null=True)
    # allocated_leave_per_year = models.IntegerField(_('allocated leave per head in a year'), blank=True, null=True)

    Company = models.ForeignKey(to='organizations.Company', blank=False, null=False, on_delete=models.CASCADE)
    Year = models.IntegerField(_('Year'), choices=YEAR_CHOICES, default=datetime.now().year, blank=False, null=False)
    January = models.IntegerField(_('January (in days)'), default=0, blank=True, null=False)
    February = models.IntegerField(_('February (in days)'), default=0, blank=True, null=False)
    March = models.IntegerField(_('March (in days)'), default=0, blank=True, null=False)
    April = models.IntegerField(_('April (in days)'), default=0, blank=True, null=False)
    May = models.IntegerField(_('May (in days)'), default=0, blank=True, null=False)
    June = models.IntegerField(_('June (in days)'), default=0, blank=True, null=False)
    July = models.IntegerField(_('July (in days)'), default=0, blank=True, null=False)
    August = models.IntegerField(_('August (in days)'), default=0, blank=True, null=False)
    September = models.IntegerField(_('September (in days)'), default=0, blank=True, null=False)
    October = models.IntegerField(_('October (in days)'), default=0, blank=True, null=False)
    November = models.IntegerField(_('November (in days)'), default=0, blank=True, null=False)
    December = models.IntegerField(_('December (in days)'), default=0, blank=True, null=False)
    # Working_days = models.IntegerField(_('Working Days'), blank=False, null=True)
    Total = models.IntegerField(_('Total working days'), default=0, blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        self.Total = (
                    self.January + self.February + self.March + self.April + self.May + self.June + self.July + self.August + self.September + self.October + self.November + self.December)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'dma_calender'
        verbose_name = _('DMA calenders')
        verbose_name_plural = _('DMA calenders')

    def __str__(self):
        return str(self.Year)


HOLIDAYS = (
    ('Language Movement Day', 'Language Movement Day'),
    ('Sheikh Mujibur Rahman\'s Birth Anniversary', 'Sheikh Mujibur Rahman\'s Birth Anniversary'),
    ('Independence Day of Bangladesh', 'Independence Day of Bangladesh'),
    ('Mid-Sha\'ban', 'Mid-Sha\'ban'),
    ('Bengali New Year (Pôhela Boishakh)', 'Bengali New Year (Pôhela Boishakh)'),
    ('Labour Day', 'Labour Day'),
    ('Jumu\'atul-Wida', 'Jumu\'atul-Wida'),
    ('Laylat al-Qadr', 'Laylat al-Qadr'),
    ('Eid al-Fitr', 'Eid al-Fitr'),
    ('Nazrul Jayanti', 'Nazrul Jayanti'),
    ('Vesak', 'Vesak'),
    ('Eid al-Adha', 'Eid al-Adha'),
    ('Ashura', 'Ashura'),
    ('Krishna Janmashtami', 'Krishna Janmashtami'),
    ('Dussehra', 'Dussehra'),
    ('Vijayadashami', 'Vijayadashami'),
    ('Prophet\'s Birthday', 'Prophet\'s Birthday'),
    ('Victory day of Bangladesh', 'Victory day of Bangladesh'),
    ('Christmas Day', 'Christmas Day'),
)


class HolidayType(models.Model):
    type_title = models.CharField(_('holiday type title'), max_length=200, blank=False, null=True)

    def __str__(self):
        return self.type_title


class HourType(models.Model):
    title = models.CharField(_('title'), max_length=250, blank=False)
    description = models.TextField(_('description'), max_length=150, blank=True, null=True)
    hours_allocated = models.IntegerField(_('hours allocated'), default=0, blank=False, null=False)
    year = models.IntegerField(_('year'), choices=YEAR_CHOICES, default=datetime.now().year, blank=False)
    company = models.ForeignKey(Company, related_name="company", blank=False, null=False,
                                 on_delete=models.CASCADE)
    date_created = models.DateField(_('date created'), default=timezone.now)
    date_updated = models.DateField(_('date updated'), default=timezone.now)

    class Meta:
        db_table = 'hour_types'
        verbose_name = _('Work Type')
        verbose_name_plural = _('Work Types')

    def __str__(self):
        return self.title


class HolidayCalender(models.Model):
    Year = models.IntegerField(_('Year'), choices=YEAR_CHOICES, default=datetime.now().year, blank=True, null=True)
    Month = models.CharField(_('Month'), max_length=20, choices=MONTHS, default='Select', blank=True, null=True)
    holiday_type = models.ForeignKey(to='organizations.HolidayType', blank=False, null=False, on_delete=models.PROTECT,
                                     default='')
    holiday_title = models.TextField(_('holiday title'), blank=False, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    hours = models.IntegerField(_('Hours'), blank=True, null=True)
    

    class Meta:
        db_table = 'holiday_calender'
        verbose_name = _('Holiday calender')
        verbose_name_plural = _('Holiday calenders')

    def __str__(self):
        return self.Month


SLC = (
    ('Programmer I (0-2)', 'Programmer I (0-2)'),
    ('Programmer II (3-6)', 'Programmer II (3-6)'),
    ('Engineer I (0-2)', 'Engineer I (0-2)'),
    ('Technician', 'Technician'),
    ('Driver', 'Driver'),
)


class Slc(models.Model):
    employee = models.ForeignKey(to='users.CustomUser', blank=False, null=False, on_delete=models.CASCADE)
    slc = models.ForeignKey(to='organizations.Designation', blank=False, null=False, on_delete=models.CASCADE,
                            verbose_name="Standard Labor Code(SLC)")
    # designation = models.ForeignKey(Designation, blank=False, null=False, on_delete=models.PROTECT)
    monthly_rate = models.IntegerField(_('Monthly Rate'), blank=True, null=True)
    hourly_rate = models.IntegerField(_('Hourly Rate'), blank=True, null=True)
    planned_hours = models.IntegerField(_('Planned Hours'), blank=True, null=True)
    planned_value = models.IntegerField(_('Planned Value'), blank=True, null=True)
    budget = models.IntegerField(_('Budget'), blank=True, null=True)
    ep = models.IntegerField(_('Estimated Person'), blank=True, null=True)

    class Meta:
        db_table = 'slc'
        verbose_name = _('Role')
        verbose_name_plural = _('Role')

    # def save(self, *args, **kwargs):
    #     self.monthly_rate = md5.new(self.monthly_rate).hexdigest()
    #     self.hourly_rate = md5.new(self.hourly_rate).hexdigest()
    #     super(Slc, self).save(*args, **kwargs)

    def __str__(self):
        return self.employee.first_name + " " + self.employee.last_name


@receiver(post_save, sender=Slc)
def post_save_slc(sender, instance, **kwargs):
    try:
        slc = Slc.objects.get(id=instance.id)
        if slc is not None:
            obj = CustomUser.objects.get(id=slc.employee.id)
            obj.slc_details_id = slc.id
            obj.save()
    except ObjectDoesNotExist:
        pass

@receiver(post_save, sender=HolidayCalender)
def post_save_updated_days_hours(sender, instance, created, **kwargs):
    
    startDate = instance.start_date
    endDate = instance.end_date

    totalDays = endDate-startDate
    print("total days", totalDays.days+1)
    totalDays= totalDays.days+1

    totalHours = totalDays*8 
    print("total hours", totalHours)

    try:
        if created : 
            instance.hours=totalHours
            instance.save()
        # else :
        #     instance.hours=totalHours
        #     instance.save()

        # query = HolidayCalender.objects.get(id=instance.id)
        # print(query)
        # if query is not None:           
        #     query.hours = totalHours
        #     print(query.hours)
        #     query.save()
    except ObjectDoesNotExist:
        pass
