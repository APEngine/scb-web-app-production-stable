# IMPORTING LIBRARIES
# Standard library imports
from django.urls import path
# Importing views from the current directory (admin-management)
from .views import (
    test_connection,
    # Users Management Functions
    create_auth_user,
    delete_auth_user,
    modify_auth_user_information,
    get_user_information,
    #
    get_priorities_and_codes_for_tasks,
    change_password,
    get_company_users,
    get_users_username_and_fullname_list,
    get_total_current_tasks_number,
    get_all_current_tasks_information,
    get_projects_tasks_associated_with,
    # Tasks Management Functions Associated To
    create_new_project_task,
    delete_specified_tasks,
    approve_specified_tasks,
    modify_current_tasks_priority,
    get_selected_task_information,
    #
    get_last_months_information,
    get_number_tasks_by_user,
    # Projects Management Functions Associated To
    get_project_information_for_table_display,
    get_all_available_projects_code,
    modify_selected_project,
    get_selected_project_information,
    create_new_project,
    # Clients Management Functions Associated To
    get_client_information_for_table_display,
    get_all_available_clients_code,
    create_new_client,
    get_short_client_list,
    get_client_information_for_modification,
    modify_selected_client
)

# APP'S NAME RELATED TO URLS
# Importing views from the current directory
app_name = "admin_management"

# URL PATTERNS
# Importing views from the current directory
urlpatterns = [
    # Endpoint for testing database connection
    path(
        "database-status/test-connection",
        test_connection,
        name="test_connection"
    ),
    
    # URL for getting all clients information 
    # Endpoint for getting a short list of clients 
    path(
        "clients/information-and-related/modify",
        modify_selected_client,
        name="modify_selected_client"
    ),
    # Endpoint for getting a short list of clients 
    path(
        "clients/information-and-related/client-information",
        get_client_information_for_modification,
        name="get_client_information_for_modification"
    ),
    # Endpoint for getting a short list of clients 
    path(
        "clients/information-and-related/client-list",
        get_short_client_list,
        name="get_short_client_list"
    ),
    # Endpoint for creating a new client 
    path(
        "clients/information-and-related/new-client",
        create_new_client,
        name="create_new_client"
    ),
    # Endpoint for getting a count of all available client codes 
    path(
        "clients/information-and-related/codes-count",
        get_all_available_clients_code,
        name="get_all_available_clients_code"
    ),
    # Endpoint for displaying client information in a table 
    path(
        "clients/information-and-related/display-clients-information",
        get_client_information_for_table_display,
        name="get_client_information_for_table_display"
    ),
    
    # URL for getting all projects information
    # 
    path(
        "projects/information-and-related/selected-project-information/<str:selected_project_code>",
        get_selected_project_information,
        name="get_selected_project_information"
    ),
    # 
    path(
        "projects/modification/modify-current-project-information",
        modify_selected_project,
        name="modify_selected_project"
    ),
    # 
    path(
        "projects/information-and-related/current-project-information",
        get_project_information_for_table_display,
        name="get_project_information_for_table_display"
    ),
    # 
    path(
        "projects/information-and-related/new-project",
        create_new_project,
        name="create_new_project"
    ),
    # 
    path(
        "projects/information-and-related/codes-count",
        get_all_available_projects_code,
        name="get_all_available_projects_code"
    ),
    
    # Other Things
    # 
    path(
        "projects/information-and-related/statistics/users-and-tasks",
        get_number_tasks_by_user,
        name="get_number_tasks_by_user"
    ),
    # 
    path(
        "projects/information-and-related/statistics",
        get_last_months_information,
        name="last-months-information"
    ),
    # URL for modifying user information
    path(
        "modify-user",
        modify_auth_user_information,
        name="modify_auth_user_information"
    ),
    # URL for deleting a user, expects a user ID as a parameter
    path(
        "delete-user/<int:userID>",
        delete_auth_user,
        name="delete_auth_user"
    ),
    # URL for deleting a specific task, expects a task code as a parameter
    path(
        "projects/creation-and-modification/task/delete",
        delete_specified_tasks,
        name="delete_specified_task"
    ),
    # URL for approving a specific task, expects a task code and a partial status as parameters
    path(
        "projects/creation-and-modification/task/approve",
        approve_specified_tasks,
        name="approve_specified_tasks"
    ),
    # URL for creating a new project task
    path(
        "projects/creation-and-modification/new-task",
        create_new_project_task,
        name="create_new_project_task"
    ),
    # URL for getting tasks associated with a project, expects a project code as a parameter
    path(
        "projects/creation-and-modification/tasks-info/<int:project_code>",
        get_projects_tasks_associated_with,
        name="get_projects_tasks_associated_with"
    ),
    # Endpoint to modify the priority of a task
    path(
        "projects/creation-and-modification/task/modify-priority", 
        modify_current_tasks_priority, 
        name="modify_current_tasks_priority"
    ),
    # Endpoint to get priorities and codes for tasks in a specific project
    path(
        "projects/information-and-related/priorities-and-codes",
        get_priorities_and_codes_for_tasks,
        name="get_priorities_and_codes_for_tasks",
    ),
    # Endpoint to get the total number of current tasks
    path(
        "projects/information-and-related/tasks/current-total-number",
        get_total_current_tasks_number,
        name="current_tasks_total_number",
    ),
    # Endpoint to get all information related to current tasks
    path(
        "projects/information-and-related/tasks/current/all/information",
        get_all_current_tasks_information,
        name="get_all_current_tasks_information",
    ),
    # Endpoint to get information of a selected task
    path(
        "projects/information-and-related/tasks/<task_code>/information",
        get_selected_task_information,
        name="get_selected_task_information",
    ),
    # Endpoint to create a new user
    path(
        "create-user", 
        create_auth_user, 
        name="create_user"
    ),
    # Endpoint to change the password of a user
    path(
        "change-password", 
        change_password,
        name="change_password"
    ),
    # Endpoint to get all users in the company
    path(
        "company-users", 
        get_company_users, 
        name="get_company_users"
    ),
    # Endpoint to get a list of usernames and full names of all users
    path(
        "company-users/information-and-related/usernames-and-fullnames-list",
        get_users_username_and_fullname_list,
        name="usernames_and_fullnames_list",
    ),
    # Endpoint to get information of a specific user
    path(
        "company-users/information-and-related/<int:user_code>/information",
        get_user_information,
        name="get_user_information",
    ),
]
