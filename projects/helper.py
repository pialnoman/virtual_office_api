from datetime import datetime, date, timedelta
import pandas as pd

from organizations.models import DmaCalender
from organizations.serializers import DmaCalenderSerializer


def unique(list1):
    # initialize a null list
    unique_list = []

    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    # print list
    return unique_list


months = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December'
}


def monthly_hours_in_fraction_for_start_month(start_date):
    day = int(start_date.strftime('%d'))
    print('diff', date.today().year)
    monthly_hours = int(DmaCalenderSerializer(DmaCalender.objects.get(Company_id=1,Year=date.today().year)).data[months[int(start_date.strftime('%m'))]]) * 8

    if day <= 7:
        return monthly_hours
    elif day in range(8,15):
        return monthly_hours * 0.75
    elif day in range(15,22):
        return monthly_hours * 0.5
    elif day in range(22,32):
        return monthly_hours* 0.25


def monthly_hours_in_fraction_for_end_month(start_date):
    day = int(start_date.strftime('%d'))
    print('diff', date.today().year)
    monthly_hours = int(DmaCalenderSerializer(DmaCalender.objects.get(Company_id=1,Year=date.today().year)).data[months[int(start_date.strftime('%m'))]]) * 8

    if day <= 7:
        return monthly_hours* 0.25
    elif day in range(8,15):
        return monthly_hours * 0.5
    elif day in range(15,22):
        return monthly_hours * 0.75
    elif day in range(22,32):
        return monthly_hours


def same_month_hours(start_date, end_date):
    diff = (end_date-start_date).days
    print('diff',date.today().year)
    monthly_hours = int(DmaCalenderSerializer(DmaCalender.objects.get(Company_id=1,Year=date.today().year)).data[months[int(start_date.strftime('%m'))]]) * 8
    if diff <= 7:
        return monthly_hours * 0.25
    elif diff in range(8, 15):
        return monthly_hours * 0.5
    elif diff in range(15, 22):
        return monthly_hours * 0.75
    elif diff in range(22, 32):
        return monthly_hours


def calculate_hours_from_date_to_date(from_date, to_date):
    total_hours = 0
    selected_months = []
    start_date = datetime.strptime(from_date,'%Y-%m-%d').date()
    end_date = datetime.strptime(to_date,'%Y-%m-%d').date()

    for single_date in pd.date_range(start_date, end_date):
        selected_months.append(int(single_date.strftime("%m")))

    selected_months = unique(selected_months)

    # case for more than 2 months in project start and end period
    if len(selected_months) >= 2:
        total_hours += monthly_hours_in_fraction_for_start_month(start_date)
        total_hours += monthly_hours_in_fraction_for_end_month(end_date)
        for month in selected_months[1:len(selected_months)-1]:
            total_hours += int(DmaCalenderSerializer(DmaCalender.objects.get(Company_id=1,Year=date.today().year)).data[months[month]]) * 8
    elif len(selected_months) == 1:
        total_hours = same_month_hours(start_date,end_date)

    return total_hours
