# IMPORTING LIBRARIES
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar

def get_current_last_months():
    """
    This function returns the names of the current month and the four previous months, along with the year.

    It uses the datetime and dateutil.relativedelta modules to calculate the dates.

    Returns:
        list: A list of strings where each string is a month number and year. The first string is the current month and year, 
        the second string is the previous month and year, and so on up to the fourth previous month and year.
    """
    now = datetime.now()
    months = [(now - relativedelta(months=i)).strftime('%Y-%m-01') for i in range(4)]

    return months

def include_first_and_last_day_on_month(date: str):
    
    # Parse your date string to a datetime object
    date_obj = datetime.strptime(date, '%Y-%m-%d')

    # Get the first and last day of the month
    first_day = date_obj.replace(day=1)
    last_day = date_obj.replace(day=calendar.monthrange(date_obj.year, date_obj.month)[1])

    return [first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')]