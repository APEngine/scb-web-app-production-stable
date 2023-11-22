# IMPORTING LIBRARIES
# from django.db import connection
from typing import Any
from django import http
from django.http.response import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import json
from .models import *
from django.db import connection
from django.views.decorators.http import require_http_methods


# Functions - - - -
def create_backend_data(data):
    return {
        "codigoProyecto": data[0],
        "nombreProyecto": data[1],
        "nombreTarea": data[2],
        "nombreUsuario": data[3],
        "horasReales": data[4],
        "prioridad": data[5],
        "detalles": [
            {
                "codigoTarea": data[6],
                "nombreTarea": data[7],
                "descripcionTarea": data[8],
                "horasProyectadas": data[9],
                "creacionProyecto": data[10],
            }
        ],
    }


def define_status_to_string(status_int) -> str:
    if status_int == 0:
        return "Pendiente"
    elif status_int == 1:
        return "Aprobada"
    else:
        return "Error, comuniquese con Desarrolladores"


def create_report_list_vs_hours(data) -> dict:
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


def short_create_backend_data(data, code, name):
    return {code: data[0], name: data[1]}


# Backend HTTP Methods - - - -
@require_http_methods(["GET"])
def Generate_detailed_report(
    request,
    report_type: int,
    user_id: int,
    project_code: int,
    date_from,
    date_to,
    project_status: int,
) -> HttpResponse:
    cursor = connection.cursor()
    
    if (report_type == 2):
        if (project_code == "Todos"):
            if (project_status == 2):
                query = f"""
                        SELECT 
                        h.CodigoProyecto, p.Nombre, t.Nombre, h.descripcion, 
                        u.nombre, h.HorasDedicadas, t.Aprobada, h.fechacreacion
                        FROM tareas t, proyectos p, horasdedicadastareas h, usuarios u
                        WHERE
                        u.idusuario LIKE {user_id} AND
                        u.idusuario LIKE t.programador AND
                        t.codigotarea LIKE h.CodigoTarea AND
                        h.Codigoproyecto LIKE p.CodigoProyecto AND
                        DATE(h.fechacreacion) BETWEEN '{date_from}' AND '{date_to}'
                        """
            else:
                query = f"""
                        SELECT 
                        h.CodigoProyecto, p.Nombre, t.Nombre, h.descripcion, 
                        u.nombre, h.HorasDedicadas, t.Aprobada, h.fechacreacion
                        FROM tareas t, proyectos p, horasdedicadastareas h, usuarios u
                        WHERE
                        t.aprobada LIKE {project_status} AND
                        u.idusuario LIKE {user_id} AND
                        u.idusuario LIKE t.programador AND
                        t.codigotarea LIKE h.CodigoTarea AND
                        h.Codigoproyecto LIKE p.CodigoProyecto AND
                        DATE(h.fechacreacion) BETWEEN '{date_from}' AND '{date_to}'
                        """

        elif (project_code != "Todos"):
            if (project_status == 2):
                query = f"""
                        SELECT 
                        h.CodigoProyecto, p.Nombre, t.Nombre, h.descripcion, 
                        u.nombre, h.HorasDedicadas, t.Aprobada, h.fechacreacion
                        FROM tareas t, proyectos p, horasdedicadastareas h, usuarios u
                        WHERE
                        u.idusuario LIKE {user_id} AND
                        t.programador LIKE {user_id} AND
                        t.codigotarea LIKE h.CodigoTarea AND
                        h.Codigoproyecto LIKE {project_code} AND
                        p.CodigoProyecto LIKE {project_code} AND
                        DATE(h.fechacreacion) BETWEEN '{date_from}' AND '{date_to}'
                    """
            else:
                query = f"""
                        SELECT 
                        h.CodigoProyecto, p.Nombre, t.Nombre, h.descripcion, 
                        u.nombre, h.HorasDedicadas, t.Aprobada, h.fechacreacion
                        FROM tareas t, proyectos p, horasdedicadastareas h, usuarios u
                        WHERE
                        u.idusuario LIKE {user_id} AND
                        t.programador LIKE {user_id} AND
                        t.aprobada LIKE {project_status} AND
                        t.codigotarea LIKE h.CodigoTarea AND
                        h.Codigoproyecto LIKE {project_code} AND
                        p.CodigoProyecto LIKE {project_code} AND
                        DATE(h.fechacreacion) BETWEEN '{date_from}' AND '{date_to}'
                    """
                

    cursor.execute(query)
    reportProjects = list(cursor.fetchall())
    backend_data = []
    for element in reportProjects:
        backend_data.append(create_report_list_vs_hours(element))

    json_data = json.dumps(backend_data, default=str)
    return HttpResponse(json_data, content_type="application/json")


@require_http_methods(["GET"])
def Get_all_selected_user_projects_short(request, user_id) -> HttpResponse:
    cursor = connection.cursor()
    if (user_id == "Tod"):
        query = f"""SELECT 
                    p.CodigoProyecto, p.Nombre 
                    FROM proyectos p, tareas t, usuarios u
                    WHERE
                    t.programador LIKE u.idusuario AND 
                    p.CodigoProyecto LIKE t.CodigoProyecto"""
    else:
        query = f"""SELECT 
                    p.CodigoProyecto, p.Nombre 
                    FROM proyectos p, tareas t, usuarios u
                    WHERE 
                    t.programador LIKE {user_id}
                    AND u.IDUsuario LIKE {user_id} 
                    AND p.CodigoProyecto LIKE t.CodigoProyecto"""
    cursor.execute(query)
    scbProjects = list(cursor.fetchall())
    backend_data = []
    for element in scbProjects:
        backend_data.append(
            short_create_backend_data(element, "codigoProyecto", "nombreProyecto")
        )

    json_data = json.dumps(backend_data, default=str)
    return HttpResponse(json_data, content_type="application/json")


@require_http_methods(["GET"])
def Get_every_user_project(request, user_id) -> HttpResponse:
    cursor = connection.cursor()
    if (user_id == "Todos"):
        main_user_tasks_query = f"""
                                SELECT 
                                t.CodigoProyecto, p.Nombre, t.Nombre,
                                u.Nombre, (SELECT SUM(h.HorasDedicadas)
                                                    FROM horasdedicadastareas h
                                                    WHERE h.Aprobadas LIKE 0 
                                                    AND h.CodigoTarea LIKE t.CodigoTarea
                                                    GROUP BY h.CodigoTarea
                                                    LIMIT 1), 
                                t.Prioridad
                                FROM tareas t, usuarios u, proyectos p
                                WHERE
                                t.Aprobada LIKE 0 AND
                                t.programador LIKE u.idusuario AND 
                                p.CodigoProyecto LIKE t.CodigoProyecto
                                """
        cursor.execute(main_user_tasks_query)
        main_user_tasks = list(cursor.fetchall())

        details_user_tasks_query = f"""
                                SELECT 
                                t.CodigoTarea, t.Nombre, 
                                t.Descripcion, t.HorasProyectadas, 
                                p.fechacreacion
                                FROM tareas t, proyectos p, usuarios u
                                WHERE
                                t.Aprobada LIKE 0 AND
                                t.programador LIKE u.idusuario AND 
                                p.CodigoProyecto LIKE t.CodigoProyecto
                                """
    
    else:
        main_user_tasks_query = f"""
                                SELECT 
                                t.CodigoProyecto, p.Nombre, t.Nombre,
                                u.Nombre, (SELECT SUM(h.HorasDedicadas)
                                                    FROM horasdedicadastareas h
                                                    WHERE h.Aprobadas LIKE 0 
                                                    AND h.CodigoTarea LIKE t.CodigoTarea
                                                    GROUP BY h.CodigoTarea
                                                    LIMIT 1), 
                                t.Prioridad
                                FROM tareas t, usuarios u, proyectos p
                                WHERE
                                t.Aprobada LIKE 0 
                                AND t.programador LIKE {user_id}
                                AND u.IDUsuario LIKE {user_id} 
                                AND p.CodigoProyecto LIKE t.CodigoProyecto
                                """
        cursor.execute(main_user_tasks_query)
        main_user_tasks = list(cursor.fetchall())

        details_user_tasks_query = f"""
                                SELECT 
                                t.CodigoTarea, t.Nombre, 
                                t.Descripcion, t.HorasProyectadas, 
                                p.fechacreacion
                                FROM tareas t, proyectos p
                                WHERE
                                t.Aprobada LIKE 0 
                                AND t.programador LIKE {user_id} 
                                AND p.CodigoProyecto LIKE t.CodigoProyecto
                                """

    cursor.execute(details_user_tasks_query)
    details_user_tasks = list(cursor.fetchall())

    prepare_data = []
    for i in range(len(main_user_tasks)):
        prepare_data.append(main_user_tasks[i] + details_user_tasks[i])

    backend_data = []
    for element in prepare_data:
        backend_data.append(create_backend_data(element))

    json_data = json.dumps(backend_data, default=str)

    return HttpResponse(json_data, content_type="application/json")

@require_http_methods(["GET"])
def Get_all_db_users(request) -> HttpResponse:
    cursor = connection.cursor()
    main_user_query = "SELECT idusuario, nombre FROM usuarios"
    cursor.execute(main_user_query)

    backend_response = list(cursor.fetchall())

    backend_data = []
    for element in backend_response:
        backend_data.append(
            short_create_backend_data(element, "codigoUsuario", "nombreUsuario")
        )

    json_data = json.dumps(backend_data, default=str)
    return HttpResponse(json_data, content_type="application/json")


@require_http_methods(["GET"])
def Main_user_task(request, user_id) -> HttpResponse:
    cursor = connection.cursor()
    if (user_id == "Todos"):
        main_user_tasks_query = f"""
                                SELECT 
                                t.CodigoProyecto, p.Nombre, t.Nombre,
                                u.Nombre, (SELECT SUM(h.HorasDedicadas)
                                                    FROM horasdedicadastareas h
                                                    WHERE h.Aprobadas LIKE 0 
                                                    AND h.CodigoTarea LIKE t.CodigoTarea
                                                    GROUP BY h.CodigoTarea
                                                    LIMIT 1), 
                                t.Prioridad
                                FROM tareas t, usuarios u, proyectos p
                                WHERE
                                t.Aprobada LIKE 0 AND
                                t.programador LIKE u.idusuario AND 
                                p.CodigoProyecto LIKE t.CodigoProyecto
                                """
        cursor.execute(main_user_tasks_query)
        main_user_tasks = list(cursor.fetchall())

        details_user_tasks_query = f"""
                                SELECT 
                                t.CodigoTarea, t.Nombre, 
                                t.Descripcion, t.HorasProyectadas, 
                                p.fechacreacion
                                FROM tareas t, proyectos p, usuarios u
                                WHERE
                                t.Aprobada LIKE 0 AND
                                t.programador LIKE u.idusuario AND 
                                p.CodigoProyecto LIKE t.CodigoProyecto
                                """
    else:
        main_user_tasks_query = f"""
                                SELECT 
                                t.CodigoProyecto, p.Nombre, t.Nombre,
                                u.Nombre, (SELECT SUM(h.HorasDedicadas)
                                                    FROM horasdedicadastareas h
                                                    WHERE h.Aprobadas LIKE 0 
                                                    AND h.CodigoTarea LIKE t.CodigoTarea
                                                    GROUP BY h.CodigoTarea
                                                    LIMIT 1), 
                                t.Prioridad
                                FROM tareas t, usuarios u, proyectos p
                                WHERE
                                t.Aprobada LIKE 0 
                                AND t.programador LIKE {user_id}
                                AND u.IDUsuario LIKE {user_id} 
                                AND p.CodigoProyecto LIKE t.CodigoProyecto
                                """
        cursor.execute(main_user_tasks_query)
        main_user_tasks = list(cursor.fetchall())

        details_user_tasks_query = f"""
                                SELECT 
                                t.CodigoTarea, t.Nombre, 
                                t.Descripcion, t.HorasProyectadas, 
                                p.fechacreacion
                                FROM tareas t, proyectos p
                                WHERE
                                t.Aprobada LIKE 0 
                                AND t.programador LIKE {user_id} 
                                AND p.CodigoProyecto LIKE t.CodigoProyecto
                                """
    
    cursor.execute(details_user_tasks_query)
    details_user_tasks = list(cursor.fetchall())
    print("details_user_tasks")
    print(details_user_tasks)
    print(len(details_user_tasks))
    print("main_user_tasks")
    print(main_user_tasks)
    print(len(main_user_tasks))

    prepare_data = []
    for i in range(len(main_user_tasks)):
        prepare_data.append(main_user_tasks[i] + details_user_tasks[i])

    backend_data = []
    for element in prepare_data:
        backend_data.append(create_backend_data(element))

    json_data = json.dumps(backend_data, default=str)

    return HttpResponse(json_data, content_type="application/json")


class UserTasks(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, project_code, task_code) -> JsonResponse:
        tasks = list(
            Horasdedicadastareas.objects.filter(codigoproyecto=project_code)
            .filter(codigotarea=task_code)
            .filter(aprobadas=0)
            .values("id", "descripcion", "horasdedicadas", "fechacreacion")
        )
        if len(tasks) > 0:
            data = {"message": "Success", "projects": tasks}
        else:
            data = {"message": "Projects not found..."}

        return JsonResponse(data)

    def post(self, request, project_code, task_code) -> JsonResponse:
        json_data = json.loads(request.body)
        Horasdedicadastareas.objects.create(
            codigoproyecto=project_code,
            codigotarea=task_code,
            descripcion=json_data["descripcion"],
            horasdedicadas=json_data["horas-dedicadas"],
            fechacreacion=json_data["fecha-creacion"],
            aprobadas=0,
        )

        data = {"message": "Success"}

        return JsonResponse(data)

    def put(self, request, project_code, task_code, id) -> JsonResponse:
        json_data = json.loads(request.body)
        task = list(
            Horasdedicadastareas.objects.filter(codigoproyecto=project_code)
            .filter(codigotarea=task_code)
            .filter(id=id)
            .values()
        )
        if len(task) > 0:
            task = Horasdedicadastareas.objects.get(id=id)
            task.descripcion = json_data["descripcion"]
            task.horasdedicadas = json_data["horas-dedicadas"]
            task.save()
            data = {"message": "Succes"}
        else:
            data = {"message": "Project not found..."}

        return JsonResponse(data)

    def delete(self, request, project_code, task_code, id) -> JsonResponse:
        task = list(
            Horasdedicadastareas.objects.filter(codigoproyecto=project_code)
            .filter(codigotarea=task_code)
            .filter(id=id)
            .values()
        )
        if len(task) > 0:
            Horasdedicadastareas.objects.filter(codigoproyecto=project_code).filter(
                codigotarea=task_code
            ).filter(id=id).delete()
            data = {"message": "Succes"}
        else:
            data = {"message": "Project not found..."}

        return JsonResponse(data)
