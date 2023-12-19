# IMPORTING LIBRARIES & MODULES
from django.urls import path
from .views import (
    main_user_task,
    Get_all_selected_user_projects_short,
    generate_detailed_report,
    UserTasks,
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
        "reports/detalied/<int:report_type>/<int:user_id>/<project_code>/<date:date_from>/<date:date_to>/<int:project_status>",
        generate_detailed_report,
        name="report--get-user-projects",
    ),
    path('tasks/<int:project_code>/<int:task_code>', UserTasks.as_view(), name='user_tasks'),
    path('tasks/<int:project_code>/<int:task_code>/<int:id>', UserTasks.as_view(), name='user_task_detail'),

]
