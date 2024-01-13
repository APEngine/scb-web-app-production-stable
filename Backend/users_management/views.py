# IMPORTING LIBRARIES
# Standard library imports
from datetime import datetime
from typing import Any
import json
from django.utils import timezone
import datetime

# Related third-party imports
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core import serializers
from django.db import IntegrityError, connection
from django.db.models import Sum
from django.db.models import Q, F, Value as V
from django.db.models.functions import Concat
from django.http import HttpResponse, JsonResponse, Http404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password

# Local application/library specific imports
from .models import *
from .models import AuthUser, Usuarios, Horasdedicadastareas


# FUNCTIONS 
def structure_project_task_data(previewData, detailedData) -> dict:
    
    """
    Definition:
        This function structures the project and task data into a dictionary.

    Args:
        previewData (dict): The project data.
        detailedData (dict): The task data.

    Returns:
        dict: The structured data.
    """
    
    return {
        "codigoProyecto": previewData["codigoproyecto"],
        "nombreProyecto": previewData["proyecto_nombre"],
        "nombreTarea": previewData["nombre"],
        "nombreUsuario": previewData["programador"],
        "horasReales": previewData["total_horas"],
        "prioridad": previewData["prioridad"],
        "detalles": [
            {
                "codigoTarea": detailedData["codigotarea"],
                "nombreTarea": detailedData["nombre"],
                "descripcionTarea": detailedData["descripcion"],
                "horasProyectadas": detailedData["horasproyectadas"],
                "creacionProyecto": detailedData["fechacreacion"],
            }
        ],
    }

def admin_structure_project_task_data(previewData, detailedData) -> dict:
    
    """
    Definition:
        This function structures the project and task data into a dictionary.

    Args:
        previewData (dict): The project data.
        detailedData (dict): The task data.

    Returns:
        dict: The structured data.
    """
    print(detailedData)
    return {
        "projectCode": previewData["codigoproyecto"],
        "projectName": previewData["proyecto_nombre"],
        "taskCode": previewData["codigo_tarea"],
        "taskName": previewData["nombre"],
        "userCode": previewData["username"],
        "username": previewData["programador"],
        "planHours": detailedData["horasproyectadas"],
        "realUserHours": previewData["total_horas"],
        "deadLine": "",
        "priority": previewData["prioridad"],
    }

def define_status_to_string(status_int) -> str:
    
    """
    Definition:
        This function converts a status integer into a status string.

    Args:
        status_int (int): The status integer. 0 represents "Pendiente", 1 represents "Aprobada".

    Returns:
        str: The status string.
    """
    
    if status_int == 0:
        return "Pendiente"
    elif status_int == 1:
        return "Aprobada"
    else:
        return "Error, comuniquese con Desarrolladores"


def convert_user_status_to_string(is_staff: bool, is_superuser: bool) -> str:
    if is_staff == True and is_superuser == True:
        return "Administrador"
    elif is_staff == True and is_superuser == False:
        return "Miembro del Staff"
    elif is_staff == False and is_superuser == False:
        return "Sin Privilegios"
        


def structure_report_data(data) -> dict:
    
    """
    Definition:
        This function structures the report data into a dictionary.

    Args:
        data (list): The report data.

    Returns:
        dict: The structured report data.
    """
    
    return {
        "codigoProyecto": data[0],
        "nombreProyecto": data[1],
        "nombreTarea": data[2],
        "descripcion": data[3],
        "responsable": data[4],
        "horasReales": data[5],
        "estado": define_status_to_string(data[6]),
        "ultimaActualizacion": data[7],
    }


def structure_project_data(data, code, name) -> dict:
    
    """
    Definition:
        This function structures the project data into a dictionary.

    Args:
        data (dict): The project data.
        code (str): The key to use for the project code in the returned dictionary.
        name (str): The key to use for the project name in the returned dictionary.

    Returns:
        dict: The structured project data.
    """
    
    return {code: data["codigoproyecto"], name: data["nombre"]}


def structure_user_data(data) -> dict:
    
    """
    Definition:
        This function structures the user data into a dictionary.

    Args:
        data (dict): The user data. It should have the keys "idusuario", "nombre", "email", and "tipousuario".

    Returns:
        dict: The structured user data. The keys are "user", "firstName", "lastName", "email", and "privilegies".
    """
    
    return {"user": data["username"],
            "firstName": data["first_name"], 
            "lastName": data["last_name"],
            "email": data["email"],
            "privilegies": convert_user_status_to_string(data["is_staff"], data["is_superuser"]),
            "active": "Activo" if data["is_active"] else "Inactivo"
            }

def structure_project_summary(data, name1, name2, title1, title2) -> dict:
    
    """
    Definition:
        This function structures the project data into a dictionary.

    Args:
        data (dict): The project data. It should have the keys specified by name1 and name2.
        name1 (str): The key in data for the first piece of project data.
        name2 (str): The key in data for the second piece of project data.
        title1 (str): The key to use for the first piece of project data in the returned dictionary.
        title2 (str): The key to use for the second piece of project data in the returned dictionary.

    Returns:
        dict: The structured project data. The keys are title1 and title2.
    """
    
    return {title1: data[name1],
            title2: data[name2]}
    
from django import forms
from django.core.validators import EmailValidator, MinLengthValidator, MaxLengthValidator
from django.contrib.auth.password_validation import validate_password

class UserForm(forms.Form):
    username = forms.CharField(
        max_length=15, 
        validators=[
            MinLengthValidator(5), 
            MaxLengthValidator(15)
            ]
    )  
    password = forms.CharField(
        validators=[validate_password]
    )  
    firstName = forms.CharField(
        max_length=30,
        validators=[
            MinLengthValidator(5), 
            MaxLengthValidator(30)
            ]
    )
    lastName = forms.CharField(
        max_length=100, 
        validators=[
            MinLengthValidator(5), 
            MaxLengthValidator(100)
            ]
    )
    email = forms.EmailField(
        validators=[
            EmailValidator()
            ]
    )  # Use EmailField for automatic email validation
    privileges = forms.CharField(required=True)
    isActive = forms.CharField(required=True)

def structure_task_code_data(data):
    return {
        "task_code": data["codigotarea"][-3:],
        "priority": data["prioridad"]
    }
    

# BACKEND HTTP METHODS 
def get_priority_and_code_task(request, project_code):
    try:
        datas = Tareas.objects.filter(codigoproyecto=project_code).values("codigotarea", "prioridad")
        backend_data = [structure_task_code_data(data) for data in datas]
        return JsonResponse(backend_data, safe=False)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)



@csrf_exempt
# @login_required
# @permission_required("auth.add_user", raise_exception=True)
def create_auth_user(request):
    
    """
    Definition:
        Creates a new AuthUser instance and saves it to the database.

        This function extracts user data from the request body, validates and hashes the password, 
        and then creates a new AuthUser instance with the provided data. If the username or email 
        already exists in the database, an error message is returned.

    Args:
        request (HttpRequest): The Django HttpRequest object. The request body should contain 
        a JSON object with the following keys: "username", "password", "first_name", "last_name", 
        "email", "is_staff", "is_active", "is_superuser".

    Returns:
        HttpResponse: A JsonResponse indicating whether the user was created successfully or 
        an error message if the user could not be created.

    Raises:
        ValidationError: If the provided password is not valid.
        IntegrityError: If a user with the provided username or email already exists.
    """
    
    data = json.loads(request.body)
    frontend_form = UserForm(data)
    
    if frontend_form.is_valid():
        # Extracting validated data
        username = frontend_form.cleaned_data["username"]
        password = frontend_form.cleaned_data["password"]
        first_name = frontend_form.cleaned_data["firstName"]
        last_name = frontend_form.cleaned_data["lastName"]
        email = frontend_form.cleaned_data["email"]
        is_active = frontend_form.cleaned_data["isActive"] in ["active"]
        is_staff = frontend_form.cleaned_data["privileges"] in ["admin", "staff"]
        is_superuser = frontend_form.cleaned_data["privileges"] in ["admin"]
        
        # Hash the password
        hashed_password = make_password(password)

        # Create a new AuthUser instance
        user = AuthUser(
            username=username,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_staff=is_staff,
            is_active=is_active,
            is_superuser=is_superuser,
            date_joined=timezone.now(),
        )

        # Save the new user to the database
        try:
            user.save()
        except IntegrityError as e:
            return JsonResponse({"error": "A user with this username or email already exists."}, status=400)

        return JsonResponse({"message": "User created successfully"}, status=201)
    
    else:
        return JsonResponse({"error": frontend_form.errors}, status=400)
  
   


def change_password(request):
    """
    Definition:
        Changes the password of an existing AuthUser instance.

        This function extracts user data from the request body, validates the old and new passwords, 
        and then updates the password of the AuthUser instance. If the old password is incorrect, 
        an error message is returned.

    Args:
        request (HttpRequest): The Django HttpRequest object. The request body should contain 
        a JSON object with the following keys: "username", "old_password", "new_password".

    Returns:
        HttpResponse: A JsonResponse indicating whether the password was changed successfully or 
        an error message if the password could not be changed.

    Raises:
        ValidationError: If the provided new password is not valid.
    """
    
    data = json.loads(request.body)
    username = data.get("username")
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    # Get the user
    try:
        user = AuthUser.objects.get(username=username)
    except AuthUser.DoesNotExist:
        return JsonResponse({"error": "User does not exist."}, status=400)

    # Check the old password
    if not check_password(old_password, user.password):
        return JsonResponse({"error": "Old password is incorrect."}, status=400)

    # Validate the new password
    try:
        validate_password(new_password)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)

    # Hash and set the new password
    user.password = make_password(new_password)
    user.save()

    return JsonResponse({"message": "Password changed successfully"}, status=200)

@require_http_methods(["GET"])
def get_company_users(request):
    """
    Definition:
        This view function handles the GET request to fetch all users in the company.

    Args:
        request (HttpRequest): The request object.

    Returns:
        JsonResponse: The response object with the users data in JSON format.
    """
    try:
        users = AuthUser.objects.values("username", "first_name", "last_name", "email", "is_staff", "is_superuser", "is_active")
        backend_data = [structure_user_data(user) for user in users]
        return JsonResponse(backend_data, safe=False)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)  
 

@require_http_methods(["GET"])
def get_current_tasks(request):
    
    """
    Definition:
        Fetches and returns tasks created within a specific date range.

        This function queries the Horasdedicadastareas model for tasks that were created 
        between "2023-11-01" and "2023-11-16". It then transforms the resulting 
        tasks into a list of dictionaries, where each dictionary contains the 
        "codigotarea" and "descripcion" of a task.

    Args:
        request (HttpRequest): The Django HttpRequest object.

    Returns:
        HttpResponse: A JsonResponse containing a list of tasks, or an error 
        message if a ValidationError was raised during the query.

    Raises:
        ValidationError: If the query parameters are not valid.
    """
    
    try:
        start_date = datetime.strptime("2023-11-01", "%Y-%m-%d").date()
        end_date = datetime.strptime("2023-11-16", "%Y-%m-%d").date()
        tasks = Horasdedicadastareas.objects.filter(fechacreacion__date__range=(start_date, end_date)).values("codigotarea", "descripcion")
        backend_data = [structure_project_summary(task, "codigotarea", "descripcion", "codigoTarea", "nombreTarea") for task in tasks]
        return JsonResponse(backend_data, safe=False)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    
   
@require_http_methods(["GET"])
def get_current_projects(request) -> HttpResponse:   
    """
    Definition:
        Fetches and returns projects created within a specific date range.

        This function queries the Proyectos model for projects that were created 
        between "2023-11-01" and "2023-11-16". It then transforms the resulting 
        projects into a list of dictionaries, where each dictionary contains the 
        "codigoProyecto" and "nombreProyecto" of a project.

    Args:
        request (HttpRequest): The Django HttpRequest object.

    Returns:
        HttpResponse: A JsonResponse containing a list of projects, or an error 
        message if a ValidationError was raised during the query.

    Raises:
        ValidationError: If the query parameters are not valid.
    """ 
    try:
        start_date = datetime.strptime("2023-11-01", "%Y-%m-%d").date()
        end_date = datetime.strptime("2023-11-16", "%Y-%m-%d").date()
        projects = Proyectos.objects.filter(fechacreacion__date__range=(start_date, end_date)).values("codigoproyecto", "nombre")
        backend_data = [structure_project_summary(project, "codigoproyecto", "nombre", "codigoProyecto", "nombreProyecto") for project in projects]
        return JsonResponse(backend_data, safe=False)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    
   
@require_http_methods(["GET"])
def generate_detailed_report(request, report_type, user_id, project_code, date_from, date_to, project_status: int):
    
    """
    Definition:
        Generates a detailed report based on the provided parameters.

    Parameters:
        request (HttpRequest): The Django HttpRequest object. (NOT USED)
        report_type (int): The type of report to generate.
        user_id (int): The ID of the user for whom to generate the report.
        project_code (str): The code of the project for which to generate the report.
        date_from (date): The start date for the report.
        date_to (date): The end date for the report.
        project_status (int): The status of the project for which to generate the report.

    Returns:
        HttpResponse: The Django HttpResponse object with the generated report.
    """
    
    if report_type == 2:
        # Get the Projects (Proyectos) and Tasks (tareas) associated with the user_id
        proyectos = Tareas.objects.filter(
            programador=user_id
        ).values("codigoproyecto")
        tareas = Tareas.objects.filter(
            programador=user_id
        ).values("codigotarea")
        
        # Get all necessary fields from Horasdedicadastareas
        horasdedicadastareas_values = Horasdedicadastareas.objects.filter(
                codigoproyecto__in=proyectos,
                fechacreacion__date__range=(
                    date_from, 
                    date_to
                )
            )

        # Apply additional filters based on report_type, project_code, and project_status
        if project_code != "Todos":
            horasdedicadastareas_values = horasdedicadastareas_values.filter(codigoproyecto=project_code)

        if project_status == 0:
            estado_horas = Tareas.objects.filter(codigoproyecto__in=proyectos, 
                                                 codigotarea__in=tareas, 
                                                 aprobada=False).values(
                                                     "codigoproyecto",
                                                     "codigotarea",
                                                     "aprobada"
                                                     )
        elif project_status == 1:
            estado_horas = Tareas.objects.filter(codigoproyecto__in=proyectos,
                                                 codigotarea__in=tareas, 
                                                 aprobada=True).values(
                                                    "codigoproyecto", 
                                                    "codigotarea", 
                                                    "aprobada"
                                                    )
        elif project_status == 2:
            estado_horas = Tareas.objects.filter(codigoproyecto__in=proyectos, 
                                                 codigotarea__in=tareas).values(
                                                    "codigoproyecto", 
                                                    "codigotarea", 
                                                    "aprobada"
                                                    )
        
             
        # Convert estado_horas to a set of tuples (codigoproyecto, codigotarea)
        estado_horas_set = set(
            (
            item["codigoproyecto"], 
            item["codigotarea"]
            ) for item in estado_horas)

        # Filter horasdedicadastareas_values based on estado_horas_set
        filtered_horasdedicadastareas_values = horasdedicadastareas_values.filter(
            codigoproyecto__in=[item[0] for item in estado_horas_set],
            codigotarea__in=[item[1] for item in estado_horas_set]
        )
        filtered_horasdedicadastareas_values= filtered_horasdedicadastareas_values.values(
            "codigoproyecto",
            "codigotarea",
            "descripcion",
            "horasdedicadas",
            "fechacreacion"
        )
        
        # Append project_status to each dictionary in horasdedicadastareas_values where codigoproyecto and codigotarea match
        for horas in filtered_horasdedicadastareas_values:
            for estado in estado_horas:
                if horas["codigoproyecto"] == estado["codigoproyecto"] and horas["codigotarea"] == estado["codigotarea"]:
                    horas["aprobada"] = estado["aprobada"]
                    break      
        
        # Create a list to store the data
        data = []
        
        # Iterate over the horasdedicadastareas_values QuerySet
        for item in filtered_horasdedicadastareas_values:
            # Get the corresponding Proyecto and Tarea
            proyecto = Proyectos.objects.get(codigoproyecto=item["codigoproyecto"]).nombre
            tarea = Tareas.objects.get(codigotarea=item["codigotarea"]).nombre

            # Get the full name of the AuthUser
            responsable = AuthUser.objects.filter(username=user_id).annotate(
                full_name=Concat("first_name", V(" "), "last_name")
            ).values("full_name")
            responsable = list(responsable)[0]["full_name"] if responsable else None

            # Create a dictionary with the desired structure
            item_data = {
                "codigoProyecto": item["codigoproyecto"],
                "nombreProyecto": proyecto,
                "nombreTarea": tarea,
                "descripcion": item["descripcion"],
                "responsable": responsable,
                "horasReales": item["horasdedicadas"],
                "estado": "Aprobada" if item["aprobada"] else "Pendiente",
                "ultimaActualizacion": item["fechacreacion"].strftime("%Y-%m-%d %H:%M:%S"),
            }

            # Add the dictionary to the data list
            data.append(item_data)
        
        # Convert the data list to JSON
        json_data = json.dumps(data)
        
    return HttpResponse(json_data, content_type="application/json")


@require_http_methods(["GET"])
def Get_all_selected_user_projects_short(request, user_id) -> HttpResponse:
    
    """
    Definition:
        This view function handles the GET request to fetch all projects for a specific user or all users.

    Args:
        request (HttpRequest): The request object.
        user_id (str): The user id. If it's "Tod", projects for all users are returned.

    Returns:
        HttpResponse: The response object with the projects data in JSON format.
    """
    
    if (user_id == "Tod"):
        
        # Get all projects from all users
        project_details_general = Proyectos.objects.values(
            "codigoproyecto", 
            "nombre"
        )
        
        # Transforming data into a list of dictionaries for Frontend
        backend_data = [structure_project_data(
            element, 
            "codigoProyecto", 
            "nombreProyecto"
        ) for element in project_details_general]
        
    else:
        
        # Get all projects from a specific user with match 'user_id'
        project_detailes_individual = Tareas.objects.filter(
            programador=user_id
        ).values(
            "codigoproyecto"
        )
            
        project_detailes_individual_info = [t["codigoproyecto"] for t in project_detailes_individual]
        
        user_projects = Proyectos.objects.filter(
                codigoproyecto__in=project_detailes_individual_info
            ).values(
                "codigoproyecto",
                "nombre"
            )
        user_projects_list = list(user_projects)
        
        # Transforming data into a list of dictionaries for Frontend
        backend_data = [structure_project_data(
            element, 
            "codigoProyecto", 
            "nombreProyecto"
        ) for element in user_projects_list]
        
    json_data = json.dumps(backend_data, default=str)
    
    return HttpResponse(json_data, content_type="application/json") 


@require_http_methods(["GET"])
def get_all_db_users(request):
    
    """
    Definition:
        Fetches all users from the database and returns them as a JSON response.

    Parameters:
    request (HttpRequest): The Django HttpRequest object.

    Returns:
    JsonResponse: A JsonResponse object containing all users.
    """
    
    # Fetch all Usuario objects
    usuarios = AuthUser.objects.filter(is_active=True).values("username", "first_name", "last_name")


    # Convert QuerySet to list of dictionaries
    temp_usuarios_list = list(usuarios)
    
    user_list = []
    for item in temp_usuarios_list:
        user_dict = {
            "idusuario": item["username"],
            "nombre": f"{item['first_name']} {item['last_name']}"
        }
        user_list.append(user_dict)
        

    # Return JsonResponse
    return JsonResponse(user_list, safe=False)


def count_elements(request):
    total_current_tasks = Tareas.objects.filter(aprobada=False).all().count()
    return JsonResponse({"total_current_tasks": total_current_tasks})  


@require_http_methods(["GET"])
def get_all_current_tasks(request) -> HttpResponse:

    tasks = Tareas.objects.filter(
        aprobada=False
    )
    
    details_all_tasks = Tareas.objects.filter(
            aprobada=False
        ).values(
            "horasproyectadas",
    )
   
    tasks_info = tasks.values(
        "codigoproyecto", 
        "codigotarea", 
        "nombre", 
        "programador", 
        "prioridad",
        "horasproyectadas"
    )
    
    codigotarea_values = tasks.values_list(
        "codigotarea", 
        flat=True
    )

    sums_horas_dedicadas = Horasdedicadastareas.objects.filter(
            codigotarea__in=codigotarea_values
        ).values(
            "codigotarea"
        ).annotate(
            total_horas=Sum("horasdedicadas")
        )
    
    codigoproyecto_list = tasks.values_list(
        "codigoproyecto", 
        flat=True
    )
    
    codigoproyecto_name = Proyectos.objects.filter(
            codigoproyecto__in=codigoproyecto_list
        ).values(
            "codigoproyecto", 
            "nombre"
        )

    tasks = []

    for task in tasks_info:
        full_name = AuthUser.objects.filter(
                username=task["programador"]
            ).annotate(
                full_name=Concat("first_name", V(" "), "last_name")
            ).values("full_name")[0]["full_name"]
        username = AuthUser.objects.filter(username=task["programador"]).values("username")
        
        task_dict = {
                "codigoproyecto": task["codigoproyecto"],
                "proyecto_nombre": next((project["nombre"] for project in codigoproyecto_name if task["codigoproyecto"] == project["codigoproyecto"]), None),
                "codigo_tarea": task["codigotarea"], 
                "nombre": task["nombre"],
                "username": str(username[0]["username"]),
                "programador": full_name,
                "total_horas": next((sum_horas["total_horas"] for sum_horas in sums_horas_dedicadas if task["codigotarea"] == sum_horas["codigotarea"]), None),
                "prioridad": task["prioridad"],
            }
        print(task_dict)
        tasks.append(task_dict)
    
    data = [admin_structure_project_task_data(task, detail) for task, detail in zip(tasks,details_all_tasks)]
    
    return JsonResponse(data, safe=False)


def structure_user_info(data):
    return {
        "firstName": data["first_name"],
        "lastName": data["last_name"],
        "email": data["email"],
        "username": data["username"],
        "isStaff": data["is_staff"],
        "isActive": data["is_active"],
        "isSuperuer": data["is_superuser"]
    }


def get_user_info(request, user_code):
    user = AuthUser.objects.filter(username=user_code).values("password", "is_superuser", "username", "first_name", "last_name", "email" ,"is_staff", "is_active")
    
    backend_data = []
    for info in user:
        data_query = {
            "firstName": info["first_name"],
            "lastName": info["last_name"],
            "email": info["email"],
            "username": info["username"],
            "isStaff": info["is_staff"],
            "isActive": info["is_active"],
            "isSuperuser": info["is_superuser"]
        }
        backend_data.append(data_query)
        
    return JsonResponse(backend_data, safe=False)
    

@require_http_methods(["GET"])
def get_selected_task_info(request, task_code) -> HttpResponse:

    tasks = Tareas.objects.filter(
        aprobada=False,
        codigotarea = task_code
    )
    
    details_all_tasks = Tareas.objects.filter(
            aprobada=False,
            codigotarea = task_code
        ).values(
            "horasproyectadas",
    )
   
    tasks_info = tasks.values(
        "codigoproyecto", 
        "codigotarea", 
        "nombre", 
        "programador", 
        "prioridad",
        "horasproyectadas"
    )
    
    codigotarea_values = tasks.values_list(
        "codigotarea", 
        flat=True
    )

    sums_horas_dedicadas = Horasdedicadastareas.objects.filter(
            codigotarea__in=codigotarea_values
        ).values(
            "codigotarea"
        ).annotate(
            total_horas=Sum("horasdedicadas")
        )
    
    codigoproyecto_list = tasks.values_list(
        "codigoproyecto", 
        flat=True
    )
    
    codigoproyecto_name = Proyectos.objects.filter(
            codigoproyecto__in=codigoproyecto_list
        ).values(
            "codigoproyecto", 
            "nombre"
        )

    tasks = []

    for task in tasks_info:
        full_name = AuthUser.objects.filter(
                username=task["programador"]
            ).annotate(
                full_name=Concat("first_name", V(" "), "last_name")
            ).values("full_name")[0]["full_name"]
        username = AuthUser.objects.filter(username=task["programador"]).values("username")
        
        task_dict = {
                "codigoproyecto": task["codigoproyecto"],
                "proyecto_nombre": next((project["nombre"] for project in codigoproyecto_name if task["codigoproyecto"] == project["codigoproyecto"]), None),
                "codigo_tarea": task["codigotarea"],
                "nombre": task["nombre"],
                "username": str(username[0]["username"]),
                "programador": full_name,
                "total_horas": next((sum_horas["total_horas"] for sum_horas in sums_horas_dedicadas if task["codigotarea"] == sum_horas["codigotarea"]), None),
                "prioridad": task["prioridad"],
            }

        tasks.append(task_dict)
    
    data = [admin_structure_project_task_data(task, detail) for task, detail in zip(tasks,details_all_tasks)]
    
    return JsonResponse(data, safe=False)




@require_http_methods(["GET"])
def main_user_task(request, user_id) -> HttpResponse:

    """
    Definition:
        This view function handles the GET request to fetch tasks for a specific user or all users.
    
    Args:
        request (HttpRequest): The request object.
        user_id (str): The user id. If it's "Todos", tasks for all users are returned.

    Returns:
        HttpResponse: The response object with the tasks data in JSON format.
    """

    if user_id == "Todos":
        tasks = Tareas.objects.filter(
            aprobada=False
        )
        details_all_tasks = Tareas.objects.filter(
                aprobada=False
            ).values(
                "codigotarea", 
                "nombre", 
                "descripcion", 
                "horasproyectadas",
                "fechacreacion"
        )
    else:
        tasks = Tareas.objects.filter(
            programador=user_id, 
            aprobada=False
        )
        details_all_tasks = Tareas.objects.filter(
                programador=user_id, 
                aprobada=False
            ).values(
                "codigotarea", 
                "nombre", 
                "descripcion", 
                "horasproyectadas",
                "fechacreacion"
        )

    tasks_info = tasks.values(
        "codigoproyecto", 
        "codigotarea", 
        "nombre", 
        "programador", 
        "prioridad"
    )
    codigotarea_values = tasks.values_list(
        "codigotarea", 
        flat=True
    )

    sums_horas_dedicadas = Horasdedicadastareas.objects.filter(
            codigotarea__in=codigotarea_values
        ).values(
            "codigotarea"
        ).filter(
            aprobadas=0
        ).annotate(
            total_horas=Sum("horasdedicadas")
        )
    
    codigoproyecto_list = tasks.values_list(
        "codigoproyecto", 
        flat=True
    )
    
    codigoproyecto_name = Proyectos.objects.filter(
            codigoproyecto__in=codigoproyecto_list
        ).values(
            "codigoproyecto", 
            "nombre"
        )

    tasks = []

    for task in tasks_info:
        username = AuthUser.objects.filter(
                username=task["programador"]
            ).annotate(
                full_name=Concat("first_name", V(" "), "last_name")
            ).values("full_name")[0]["full_name"]
        
        task_dict = {
                "codigoproyecto": task["codigoproyecto"],
                "proyecto_nombre": next((project["nombre"] for project in codigoproyecto_name if task["codigoproyecto"] == project["codigoproyecto"]), None),
                "nombre": task["nombre"],
                "programador": username,
                "total_horas": next((sum_horas["total_horas"] for sum_horas in sums_horas_dedicadas if task["codigotarea"] == sum_horas["codigotarea"]), None),
                "prioridad": task["prioridad"],
            }

        tasks.append(task_dict)
    
    data = [structure_project_task_data(task, detail) for task, detail in zip(tasks,details_all_tasks)]
    
    return JsonResponse(data, safe=False)
    
    
from rest_framework.views import APIView
@method_decorator(csrf_exempt, name="dispatch")
class UserTasks(APIView):
    
    def get_task(self, project_code, task_code, id):
        try:
            return Horasdedicadastareas.objects.get(codigoproyecto=project_code, codigotarea=task_code, id=id)
        except Horasdedicadastareas.DoesNotExist:
            raise Http404("Lo sentimos, pero esta tarea no parece existir en la base de datos")
        
    def get(self, request, project_code, task_code):
        tasks = list(Horasdedicadastareas.objects.filter(codigoproyecto=project_code, codigotarea=task_code, aprobadas=0).values("id", "descripcion", "horasdedicadas", "fechacreacion"))
        data = {"message": "Success", "projects": tasks} if tasks else {"message": "Projects not found"}
        return JsonResponse(data)
    
    def post(self, request, project_code, task_code):
        json_data = json.loads(request.body)
        descripcion = json_data.get("descripcion")
        horas_dedicadas = json_data.get("horas-dedicadas")
        fecha_creacion = json_data.get("fecha-creacion")
        fecha_creacion_date = datetime.datetime.strptime(fecha_creacion, "%Y-%m-%d").date()

        # Combine the date with a time to get a datetime
        fecha_creacion_naive = datetime.datetime.combine(fecha_creacion_date, datetime.time())

        # Make the datetime timezone-aware
        fecha_creacion_aware = timezone.make_aware(fecha_creacion_naive)

        if not all([descripcion, horas_dedicadas, fecha_creacion]):
            return Response({"message": "Missing required data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            Horasdedicadastareas.objects.create(
                codigoproyecto=project_code, 
                codigotarea=task_code, 
                descripcion=descripcion, 
                horasdedicadas=horas_dedicadas, 
                fechacreacion=fecha_creacion_aware, 
                aprobadas=0
            )
        except ValidationError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Su nueva entrada ha sido creada con éxito"}, status=status.HTTP_201_CREATED)
    
    def put(self, request, project_code, task_code, id):
        json_data = json.loads(request.body)
        task = self.get_task(project_code, task_code, id)
        task.descripcion = json_data["descripcion"]
        task.horasdedicadas = json_data["horas-dedicadas"]
        task.save()
        return JsonResponse({"message": "La entrada seleccionada ha sido modificada con éxito"})
    
    def delete(self, request, project_code, task_code, id):
        try:
            task = Horasdedicadastareas.objects.get(codigoproyecto=project_code, codigotarea=task_code, id=id)
            task.delete()
        except Horasdedicadastareas.DoesNotExist:
            raise Http404("Task not found")

        return JsonResponse({"message": "La entrada seleccionada ha sido eliminada con éxito"})
