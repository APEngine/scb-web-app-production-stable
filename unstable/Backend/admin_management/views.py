# IMPORTING LIBRARIES
# Standard library imports
from datetime import datetime
from typing import Any
import json

# Related third-party imports
from collections import Counter
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Value as V, CharField
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
from http import HTTPStatus
from django.core.exceptions import ObjectDoesNotExist 
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods
from collections import defaultdict
from django.db import transaction


# Local application/library specific imports
from .models import *
from .models import AuthUser, Usuarios, Horasdedicadastareas
from .helpers import (
    structure_project_task_data,
    admin_structure_project_task_data,
    define_status_to_string,
    convert_user_status_to_string,
    structure_report_data,
    structure_project_data,
    structure_user_data,
    structure_project_summary,
    structure_task_code_data,
    include_first_and_last_day_on_month,
    get_current_last_months,
    structure_user_info
)
from .form_classes import (
    ProjectForm,
    TaskForm,
    UserForm,
)

# BACKEND HTTP METHODS
def get_priorities_and_codes_for_tasks(request):
    try:
        tasks = Tareas.objects.filter(aprobada=0).values("codigotarea", "prioridad")
        backend_data = [structure_task_code_data(task) for task in tasks]
        return JsonResponse(backend_data, safe=False)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=HTTPStatus.BAD_REQUEST)
    except ObjectDoesNotExist:
        return JsonResponse(
            {"error": "No tasks found for the provided project code"},
            status=HTTPStatus.NOT_FOUND,
        )


@csrf_exempt
def create_new_project_task(request):
    data = json.loads(request.body)
    frontend_form = TaskForm(data)

    try:
        frontend_form.is_valid()
    except Exception as e:
        print(e, e)

    if frontend_form.is_valid():
        codigoproyecto = frontend_form.cleaned_data["projectCode"][0:5]
        codigotarea = frontend_form.cleaned_data["taskCodeInput"]
        programador = frontend_form.cleaned_data["responsable"][0:8]
        nombre = frontend_form.cleaned_data["taskName"]
        descripcion = frontend_form.cleaned_data["taskDescription"]
        horasproyectadas = frontend_form.cleaned_data["planHours"]
        aprobada = 0
        fechaaprobacion = None
        prioridad = frontend_form.cleaned_data["taskPriority"]

        # Creating a new Tareas instance
        task = Tareas(
            codigoproyecto=codigoproyecto,
            codigotarea=codigotarea,
            programador=programador,
            nombre=nombre,
            descripcion=descripcion,
            horasproyectadas=horasproyectadas,
            fechacreacion=timezone.now(),
            aprobada=aprobada,
            fechaaprobacion=fechaaprobacion,
            prioridad=prioridad,
        )

        # Saving the new task to the database
        try:
            task.save()
        except IntegrityError as e:
            return JsonResponse({"error": e}, status=400)

        return JsonResponse({"message": "Nueva tarea creada con éxito"}, status=201)

    else:
        return JsonResponse({"error": frontend_form.errors}, status=400)


@csrf_exempt
def delete_auth_user(request, userID):
    try:
        selected_user = AuthUser.objects.get(username=userID)
        selected_user.delete()
        return JsonResponse({"message": "Usuario eliminado exitosamente"}, status=200)
    except Exception as e:
        print(e)
        return JsonResponse(
            {"message": f"Problema al eliminar el usuario: {e}"}, status=400
        )


@csrf_exempt
def modify_auth_user_information(request):
    try:
        data = json.loads(request.body)
        user = AuthUser.objects.get(username=data["username"])
        user.first_name = data["firstName"]
        user.last_name = data["lastName"]
        user.email = data["email"]
        user.is_active = data["isActive"] in ["active"]
        user.is_staff = data["privileges"] in ["admin", "staff"]
        user.is_superuser = data["privileges"] in ["admin"]
        user.save()
        return JsonResponse(
            {"message": "Información de usuario modificada con éxito"}, status=200
        )
    except Exception as e:
        print(e)
        return JsonResponse(
            {"message": f"Problema al eliminar el usuario: {e}"}, status=400
        )


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
            return JsonResponse(
                {"error": "A user with this username or email already exists."},
                status=400,
            )

        return JsonResponse({"message": "Usuario creado con éxito"}, status=201)

    else:
        return JsonResponse({"message": f"ERROR: {frontend_form.errors}"}, status=400)


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
def get_short_user_list(request):
    try:
        users = AuthUser.objects.only("username", "first_name", "last_name")
        if not users:
            return JsonResponse({"error": "No users found"}, status=404)
        user_data = [structure_user_data(user) for user in users]
        return JsonResponse(user_data, safe=False)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["GET"])
def get_company_users(request):
    try:
        users = AuthUser.objects.values(
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_superuser",
            "is_active",
        )
        user_data = [structure_user_data(user) for user in users]
        return JsonResponse(user_data, safe=False)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=HTTPStatus.BAD_REQUEST)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "No users found"}, status=HTTPStatus.NOT_FOUND)


@require_http_methods(["GET"])
def get_users_username_and_fullname_list(request):
    """
    Definition:
        Fetches all users from the database and returns them as a JSON response.

    Parameters:
    request (HttpRequest): The Django HttpRequest object.

    Returns:
    JsonResponse: A JsonResponse object containing all users.
    """

    try:
        usuarios = AuthUser.objects.filter(is_active=True).values(
            "username", "first_name", "last_name"
        )
        temp_usuarios_list = list(usuarios)
        active_users = []
        for item in temp_usuarios_list:
            user_dict = {
                "idusuario": item["username"],
                "nombre": f"{item['first_name']} {item['last_name']}",
            }
            active_users.append(user_dict)
        return JsonResponse(active_users, safe=False)
    except ObjectDoesNotExist:
        return JsonResponse(
            {"error": "No active users found"}, status=HTTPStatus.NOT_FOUND
        )


def get_total_current_tasks_number(request):
    total_current_tasks = Tareas.objects.filter(aprobada=False).all().count()
    return JsonResponse({"total_current_tasks": total_current_tasks})


@require_http_methods(["GET"])
def get_projects_tasks_associated_with(request, project_code):
    try:
        task_codes = Tareas.objects.filter(codigoproyecto=project_code).values_list(
            "codigotarea", flat=True
        )
        if not task_codes:
            return JsonResponse(
                {"error": "No tasks found for this project code"}, status=404
            )
        project_object_dictionary = [
            {"task_code": task_code} for task_code in task_codes
        ]
        return JsonResponse(project_object_dictionary, safe=False)
    except Tareas.DoesNotExist:
        return JsonResponse({"error": "Project code does not exist"}, status=404)


@csrf_exempt
def modify_current_tasks_priority(request):
    print(request.body)
    try:
        data = json.loads(request.body)
        new_priorities_order = data.get("currentTasksAndPriorities")
        task_updated_content = data.get("formValues")

        for item in new_priorities_order:
            task_code = item.get("task_code")
            new_priority = item.get("priority")
            try:
                specified_task = Tareas.objects.get(codigotarea=task_code)
            except Tareas.DoesNotExist:
                return JsonResponse(
                    {"error": f"No se encontró la tarea con el código {task_code}"},
                    status=404,
                )
            specified_task.prioridad = new_priority
            specified_task.save()

        current_task = Tareas.objects.get(codigotarea=task_updated_content["taskCode"])
        current_task.programador = task_updated_content["userCode"][0:8]
        current_task.nombre = task_updated_content["taskName"]
        current_task.horasproyectadas = task_updated_content["planHours"]
        current_task.descripcion = task_updated_content["description"]

        current_task.save()
        return JsonResponse({"message": f"Tarea modificada con éxito"}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Solicitud mal formada"}, status=400)

    except Exception as e:
        print(e)
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def delete_specified_tasks(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        task_codes = data["taskCodes"]
        with transaction.atomic():
            for task_code in task_codes:
                task = Tareas.objects.get(codigotarea=task_code["taskCode"])
                priority = task.prioridad
                task.delete()

                sub_tasks = Horasdedicadastareas.objects.filter(codigotarea=task_code["taskCode"])
                sub_tasks.delete()

                # Update the priority of the remaining tasks
                Tareas.objects.filter(prioridad__gt=priority).update(
                    prioridad=F("prioridad") - 1
                )

        message = f"Las tareas seleccionadas {', '.join(map(str, task_codes))}, han sido eliminadas con éxito"
        return JsonResponse({"message": message}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"message": "Solicitud mal formada"}, status=400)
    
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)


@csrf_exempt
def approve_specified_tasks(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        task_codes = data["taskCodes"]
        parcial_status = data["parcialStatus"]
        with transaction.atomic():
            for task_code in task_codes:
                print(task_code["taskCode"])
                specified_sub_tasks = Horasdedicadastareas.objects.filter(
                    codigotarea=task_code["taskCode"]
                )
                print(specified_sub_tasks)
                for task in specified_sub_tasks:
                    task.aprobadas = 1
                    task.save()

                if parcial_status == 0:
                    specified_task = Tareas.objects.get(codigotarea=task_code["taskCode"])
                    priority = specified_task.prioridad

                    specified_task.aprobada = 1
                    specified_task.prioridad = 0
                    specified_task.fechaaprobacion = timezone.now()
                    specified_task.save()

                    # Update the priority of the remaining tasks
                    Tareas.objects.filter(prioridad__gt=priority).update(
                        prioridad=F("prioridad") - 1
                    )

        
        if parcial_status == 0:
            message = f"Las tareas seleccionadas {', '.join(map(str, task_codes))}, han sido aprobadas con éxito"
        else:
            message = f"Las sub-tareas seleccionadas asociadas a {', '.join(map(str, task_codes))} han sido aprobadas con éxitos"
        print("buen camino")
        return JsonResponse({"message": message}, status=200)

    except json.JSONDecodeError:
        print("excepcion json")
        return JsonResponse({"message": "Solicitud mal formada"}, status=400)
    
    except Exception as e:
        print("excepcion")
        print(e)
        return JsonResponse({"message": str(e)}, status=500)
    

@require_http_methods(["GET"])
def get_all_current_tasks_information(request) -> HttpResponse:
    tasks = Tareas.objects.filter(aprobada=False)

    details_all_tasks = Tareas.objects.filter(aprobada=False).values(
        "horasproyectadas",
    )

    tasks_info = tasks.values(
        "codigoproyecto",
        "codigotarea",
        "nombre",
        "programador",
        "prioridad",
        "horasproyectadas",
        "descripcion",
    )

    codigotarea_values = tasks.values_list("codigotarea", flat=True)
    sums_horas_dedicadas = (
        Horasdedicadastareas.objects.filter(codigotarea__in=codigotarea_values)
        .values("codigotarea")
        .filter(aprobadas=0)
        .annotate(total_horas=Sum("horasdedicadas"))
    )

    codigoproyecto_list = tasks.values_list("codigoproyecto", flat=True)

    codigoproyecto_name = Proyectos.objects.filter(
        codigoproyecto__in=codigoproyecto_list
    ).values("codigoproyecto", "nombre")

    tasks = []

    for task in tasks_info:
        full_name = (
            AuthUser.objects.filter(username=task["programador"])
            .annotate(full_name=Concat("first_name", V(" "), "last_name"))
            .values("full_name")[0]["full_name"]
        )
        username = AuthUser.objects.filter(username=task["programador"]).values(
            "username"
        )

        task_dict = {
            "codigoproyecto": task["codigoproyecto"],
            "proyecto_nombre": next(
                (
                    project["nombre"]
                    for project in codigoproyecto_name
                    if task["codigoproyecto"] == project["codigoproyecto"]
                ),
                None,
            ),
            "codigo_tarea": task["codigotarea"],
            "nombre": task["nombre"],
            "username": str(username[0]["username"]),
            "programador": full_name,
            "total_horas": next(
                (
                    sum_horas["total_horas"]
                    for sum_horas in sums_horas_dedicadas
                    if task["codigotarea"] == sum_horas["codigotarea"]
                ),
                None,
            ),
            "prioridad": task["prioridad"],
            "descripcion": task["descripcion"],
        }
        tasks.append(task_dict)

    data = [
        admin_structure_project_task_data(task, detail)
        for task, detail in zip(tasks, details_all_tasks)
    ]

    return JsonResponse(data, safe=False)


def get_user_information(request, user_code):
    user = AuthUser.objects.filter(username=user_code).values(
        "password",
        "is_superuser",
        "username",
        "first_name",
        "last_name",
        "email",
        "is_staff",
        "is_active",
    )

    backend_data = []
    for info in user:
        data_query = {
            "firstName": info["first_name"],
            "lastName": info["last_name"],
            "email": info["email"],
            "username": info["username"],
            "isStaff": info["is_staff"],
            "isActive": info["is_active"],
            "isSuperuser": info["is_superuser"],
        }
        backend_data.append(data_query)

    return JsonResponse(backend_data, safe=False)


@require_http_methods(["GET"])
def get_selected_task_information(request, task_code) -> HttpResponse:
    tasks = Tareas.objects.filter(aprobada=False, codigotarea=task_code)

    details_all_tasks = Tareas.objects.filter(
        aprobada=False, codigotarea=task_code
    ).values(
        "horasproyectadas",
    )

    tasks_info = tasks.values(
        "codigoproyecto",
        "codigotarea",
        "nombre",
        "programador",
        "prioridad",
        "descripcion",
        "horasproyectadas",
    )

    codigotarea_values = tasks.values_list("codigotarea", flat=True)

    sums_horas_dedicadas = (
        Horasdedicadastareas.objects.filter(codigotarea__in=codigotarea_values)
        .values("codigotarea")
        .annotate(total_horas=Sum("horasdedicadas"))
    )

    codigoproyecto_list = tasks.values_list("codigoproyecto", flat=True)

    codigoproyecto_name = Proyectos.objects.filter(
        codigoproyecto__in=codigoproyecto_list
    ).values("codigoproyecto", "nombre")

    tasks = []

    for task in tasks_info:
        full_name = (
            AuthUser.objects.filter(username=task["programador"])
            .annotate(full_name=Concat("first_name", V(" "), "last_name"))
            .values("full_name")[0]["full_name"]
        )
        username = AuthUser.objects.filter(username=task["programador"]).values(
            "username"
        )

        task_dict = {
            "codigoproyecto": task["codigoproyecto"],
            "proyecto_nombre": next(
                (
                    project["nombre"]
                    for project in codigoproyecto_name
                    if task["codigoproyecto"] == project["codigoproyecto"]
                ),
                None,
            ),
            "codigo_tarea": task["codigotarea"],
            "nombre": task["nombre"],
            "username": str(username[0]["username"]),
            "programador": full_name,
            "total_horas": next(
                (
                    sum_horas["total_horas"]
                    for sum_horas in sums_horas_dedicadas
                    if task["codigotarea"] == sum_horas["codigotarea"]
                ),
                None,
            ),
            "prioridad": task["prioridad"],
            "descripcion": task["descripcion"],
        }

        tasks.append(task_dict)

    data = [
        admin_structure_project_task_data(task, detail)
        for task, detail in zip(tasks, details_all_tasks)
    ]

    return JsonResponse(data, safe=False)


@require_http_methods(["GET"])
def get_last_months_information(request):
    months_list = ["Enero", 
                   "Febrero", 
                   "Marzo", 
                   "Abril", 
                   "Mayo", 
                   "Junio", 
                   "Julio", 
                   "Agosto", 
                   "Septiembre",
                   "Octubre", 
                   "Noviembre", 
                   "Diciembre"]
    
    months = get_current_last_months()
    
    aprobada = []
    for month in months:
        start_date, end_date = include_first_and_last_day_on_month(month)
        objects_with_dates = Tareas.objects.filter(fechaaprobacion__range=(start_date, end_date)).values("aprobada", "fechaaprobacion", "fechacreacion")
        count_aprobada = objects_with_dates.filter(aprobada=1).count()
        aprobada.append(count_aprobada)

    no_aprobada = []
    for month in months:
        start_date, end_date = include_first_and_last_day_on_month(month)
        objects_with_null = Tareas.objects.filter(fechaaprobacion__isnull=True, fechacreacion__range=(start_date, end_date)).values("fechacreacion")
        count_no_aprobada = objects_with_null.count()
        no_aprobada.append(count_no_aprobada)
        
    frontend_content = []
    for month in months:
        item = {"month": months_list[int(month[5:7]) - 1],
                "aprobada": aprobada[months.index(month)],
                "no_aprobada": no_aprobada[months.index(month)],
                "total_tareas": (aprobada[months.index(month)] + no_aprobada[months.index(month)])}
        frontend_content.append(item)
        
    return JsonResponse(frontend_content, safe=False)


@require_http_methods(["GET"])
def get_number_tasks_by_user(request):
    pie_chart_colors = ["#B22222", "#228B22", "#663399", "#FFA07A", "#7B68EE"]
    total_users = (
        AuthUser.objects.filter(is_active=True)
        .annotate(full_name=Concat("first_name", V(" "), "last_name"))
        .values("full_name", "username")
    )

    tasks = Tareas.objects.filter(aprobada=0).values("programador")
    task_counts = Counter(task["programador"] for task in tasks)

    users_and_tasks = [
        {
            "name": user["full_name"],
            "value": task_counts.get(user["username"], 0),
            "color": pie_chart_colors[i % len(pie_chart_colors)],
        }
        for i, user in enumerate(total_users)
    ]

    return JsonResponse(users_and_tasks, safe=False)


# Project Management Functions - Begin -
@csrf_exempt
def get_project_information_for_table_display(request):
    data = json.loads(request.body)
    load_status = data.get('showAllProjects')
    try:
        projects_information = []
        if load_status:
            total_projects_main_information = list(Proyectos.objects.all().values("codigoproyecto"))
        else:
            total_projects_main_information = list(Tareas.objects.filter(aprobada=0).values("codigoproyecto"))
        
        for project in total_projects_main_information:
            if project is not None:
                project_information = list(Proyectos.objects.filter(codigoproyecto=project["codigoproyecto"]).values())
                real_hours = Horasdedicadastareas.objects.filter(codigoproyecto=project["codigoproyecto"]).aggregate(Sum("horasdedicadas"))
                quoted_project_hours = Tareas.objects.filter(codigoproyecto=project["codigoproyecto"]).aggregate(Sum("horasproyectadas"))
                projects_information.append({
                    "projectCode": int(project_information[0]["codigoproyecto"]),
                    "projectName": project_information[0]["nombre"],
                    "projectType": project_information[0]["tipoproyecto"],
                    "projectDescription": project_information[0]["descripcion"],
                    "projectClientOwner": project_information[0]["codigocliente"],
                    "expandedInformation": {
                        "administrator": project_information[0]["administrador"],
                        "projectLeader": project_information[0]["programador"],
                        "quotedHours": quoted_project_hours['horasproyectadas__sum'] or 0,
                        "realHours": real_hours['horasdedicadas__sum'] or 0,
                        "dateCreation": project_information[0]["fechacreacion"]}
                })
        return JsonResponse(projects_information, safe=False)
            
    except Exception as e:
        print(e)
        
@csrf_exempt
def get_all_available_projects_code(request):
    current_year = str(datetime.now().year)[2:]
    try:
        total_projects = Proyectos.objects.filter(codigoproyecto__startswith=current_year).values("codigoproyecto")
        unavailable_codes = [project['codigoproyecto'] for project in total_projects]
        return JsonResponse(unavailable_codes, safe=False)
    except Exception as e:
        print(f"error: {e}")


@csrf_exempt
def create_new_project(request):
    data = json.loads(request.body)
    frontend_form = ProjectForm(data)
    print(data)
    try:
        frontend_form.is_valid()
    except Exception as e:
        print(f"error: {e}")

    if frontend_form.is_valid():        
        project_type = frontend_form.cleaned_data["projectType"]
        project_code = frontend_form.cleaned_data["projectCode"]
        project_name = frontend_form.cleaned_data["projectName"]
        project_description = frontend_form.cleaned_data["projectDescription"]
        project_client = frontend_form.cleaned_data["associatedClient"]
        project_leader = frontend_form.cleaned_data["projectLeader"]
        project_quoted_hours = frontend_form.cleaned_data["quotedHours"]

        # Creating a new Proyectos instance
        project = Proyectos(
            tipoproyecto=project_type,
            codigoproyecto=project_code,
            administrador=18006870,
            codigocliente=project_client,
            nombre=project_name,
            descripcion=project_description,
            programador = project_leader,
            horasproyectadas = project_quoted_hours,
            fechacreacion=timezone.now(),
        )

        # Saving the new project to the database
        try:
            project.save()
        except IntegrityError as e:
            return JsonResponse({"message": f"Error. {e}"}, status=400)

        return JsonResponse({"message": "Nuevo proyecto creado con éxito"}, status=201)

    else:
        return JsonResponse({"error": frontend_form.errors}, status=400)

@csrf_exempt
def modify_selected_project(request):
    try:
        data = json.loads(request.body)
        project = Proyectos.objects.get(codigoproyecto=data["projectCode"])
        project.nombre = data["projectName"]
        project.descripcion = data["projectDescription"]
        project.programador = data["projectLeader"]
        project.horasproyectadas = data["quotedHours"]
        project.codigocliente = data["projectClientOwner"]
        project.save()
        return JsonResponse(
            {"message": "Información de proyecto modificada con éxito"}, status=200
        )
    except Exception as e:
        print(e)
        return JsonResponse(
            {"message": f"Problema al modificar la información del proyecto: {e}"}, status=400
        )

@csrf_exempt
def get_selected_project_information(request, selected_project_code):
    try:
        project = Proyectos.objects.filter(codigoproyecto=selected_project_code).values(
            "codigoproyecto",
            "codigocliente",
            "tipoproyecto",
            "programador",
            "administrador",
            "nombre",
            "descripcion",
            "programador",
            "horasproyectadas",
            "fechacreacion",
        )
        backend_data = []
        for item in project:
            data_query = {
                "projectType": item["tipoproyecto"],
                "projectCode": item["codigoproyecto"],
                "projectName": item["nombre"],
                "projectDescription": item["descripcion"],
                "projectClientOwner": item["codigocliente"],
                "projectLeader": item["programador"],
                "quotedHours": item["horasproyectadas"],
                "creationDate": item["fechacreacion"],
            }
            backend_data.append(data_query)

        return JsonResponse(backend_data, safe=False)
    
    except Exception as e:
        print(e)
        return JsonResponse(
            {"message": f"Problema al solicitar la información del proyecto: {e}"}, status=400
        )

# Project Management Functions - Finish -