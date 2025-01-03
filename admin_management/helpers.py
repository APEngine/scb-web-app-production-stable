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
    months = [(now - relativedelta(months=i)).strftime('%Y-%m') for i in range(4)]  

    return months

from datetime import datetime
import calendar

def include_first_and_last_day_on_month(date: str):
    # Append '-01' to the date string to make it 'YYYY-MM-DD'
    date += '-01'

    # Parse your date string to a datetime object
    date_obj = datetime.strptime(date, '%Y-%m-%d')

    # Get the first and last day of the month
    first_day = date_obj.replace(day=1)
    last_day = date_obj.replace(day=calendar.monthrange(date_obj.year, date_obj.month)[1])

    return [first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')]



# HELP FUNCTIONS
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

    return {
        "projectCode": previewData["codigoproyecto"],
        "projectName": previewData["proyecto_nombre"],
        "taskCode": previewData["codigo_tarea"],
        "taskName": previewData["nombre"],
        "description": previewData["descripcion"],
        "userCode": previewData["username"],
        "username": previewData["programador"],
        "planHours": detailedData["horasproyectadas"],
        "realUserHours": previewData["total_horas"],
        "deadLine": "",
        "priority": previewData["prioridad"],
        "projectType": int(previewData["tipo_proyecto"]),
            
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

    return {
        "user": data["username"],
        "firstName": data["first_name"],
        "lastName": data["last_name"],
        "email": data["email"],
        "privilegies": convert_user_status_to_string(
            data["is_staff"], data["is_superuser"]
        ),
        "active": "Activo" if data["is_active"] else "Inactivo",
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

    return {title1: data[name1], title2: data[name2]}

def structure_task_code_data(data):
    return {"task_code": data["codigotarea"], "priority": data["prioridad"]}

def structure_user_info(data):
    return {
        "firstName": data["first_name"],
        "lastName": data["last_name"],
        "email": data["email"],
        "username": data["username"],
        "isStaff": data["is_staff"],
        "isActive": data["is_active"],
        "isSuperuer": data["is_superuser"],
    }