# IMPORTING LIBRARIES & MODULES
from django.urls import path
from .views import (
    main_user_task,
    Get_all_selected_user_projects_short,
    generate_detailed_report,
    UserTasks,
    retrieve_information_from_code,
    retrieve_two_weeks_dedication
)
from django.urls import path, register_converter
from users_management.converter import DateConverter

# DATE CONVERTER FUNCTION
register_converter(DateConverter, "date")

# DEFINING API SAMBA URL PATTERNS
urlpatterns = [
    path(
        "mainTasks/<user_id>", 
        main_user_task, 
        name="main-user-tasks"
    ),
    path(
        "reports/<user_id>/short-list",
        Get_all_selected_user_projects_short,
        name="report--get-all-projects",
    ),
    path(
        "reports/<user_id>", 
         main_user_task, 
         name="report--get-user-projects"
    ),
    path(
        "generate-report",
        generate_detailed_report,
        name="report--get-user-projects",
    ),
    path('tasks/<int:project_code>/<int:task_code>', UserTasks.as_view(), name='user_tasks'),
    path('tasks/<int:project_code>/<int:task_code>/<int:id>', UserTasks.as_view(), name='user_task_detail'),
    path('tasks/<int:project_code>/<int:task_code>/information', retrieve_information_from_code, name='user_task_detail_date'),
    path('tasks/reports/worked-hours/<int:user_code>', retrieve_two_weeks_dedication, name='user_task_detail_date'),

]
