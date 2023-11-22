# IMPORTING LIBRARIES & MODULES
from django.urls import path
from .views import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.urls import path, register_converter
from UserTasks.converter import DateConverter

# DATE CONVERTER FUNCTION
register_converter(DateConverter, 'date')

# DEFINING API SAMBA URL PATTERNS
urlpatterns = [
    path('authority/all-users', 
        Get_all_db_users, 
        name='get-every-user'),
    
    path('mainTasks/<user_id>', 
        Main_user_task, 
        name='main-user-tasks'),
    
    path('reports/<user_id>/short-list', 
        Get_all_selected_user_projects_short, 
        name='report--get-all-projects'),
    
    path('reports/<user_id>', 
        Get_every_user_project, 
        name='report--get-user-projects'),
    
    path('reports/detalied/<int:report_type>/<int:user_id>/<project_code>/<date:date_from>/<date:date_to>/<int:project_status>', 
        Generate_detailed_report, 
        name='report--get-user-projects'),
            
    path('tasks/<int:project_code>/<int:task_code>', 
        UserTasks.as_view(), 
        name='specific-project-subTasks'),
        
    path('tasks/<int:project_code>/<int:task_code>/<int:id>', 
        UserTasks.as_view(), 
        name='modify-subTask'),
        
    path('tasks/<int:project_code>/<int:task_code>/delete/<int:id>', 
        UserTasks.as_view(), 
        name='delete-subTask'),
]