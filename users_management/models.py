from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField(blank=False, null=False)
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)

class Clientes(models.Model):
    id = models.IntegerField(primary_key=True)
    codigo_cliente = models.IntegerField(db_column='codigoCliente', unique=True)  # Field name made lowercase.
    nombre_cliente = models.CharField(db_column='nombreCliente', max_length=100)  # Field name made lowercase.
    direccion = models.CharField(max_length=200)
    email_contacto = models.CharField(db_column='emailContacto', max_length=150)  # Field name made lowercase.
    telefono_contacto = models.CharField(db_column='telefonoContacto', max_length=60)  # Field name made lowercase.
    sitio_web = models.CharField(db_column='sitioWeb', max_length=200)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'clientes'

class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Proyectos(models.Model):
    codigoproyecto = models.CharField(db_column='CodigoProyecto', max_length=10, primary_key=True)
    codigocliente = models.CharField(db_column='codigoCliente', max_length=8, blank=True, null=True)
    tipoproyecto = models.CharField(db_column='TipoProyecto', max_length=5)
    programador = models.CharField(db_column='Programador', max_length=8, blank=True, null=True)
    administrador = models.CharField(db_column='Administrador', max_length=8)
    nombre = models.CharField(db_column='Nombre', max_length=100)
    descripcion = models.CharField(db_column='Descripcion', max_length=250, blank=True, null=True)
    horasproyectadas = models.IntegerField(db_column='HorasProyectadas', blank=True, null=True)
    fechacreacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'proyectos'


class Tareas(models.Model):
    codigoproyecto = models.ForeignKey(Proyectos, on_delete=models.CASCADE, db_column='CodigoProyecto')
    codigotarea = models.CharField(db_column='CodigoTarea', max_length=10, primary_key=True)
    programador = models.CharField(db_column='Programador', max_length=8)
    nombre = models.CharField(db_column='Nombre', max_length=100)
    descripcion = models.CharField(db_column='Descripcion', max_length=250, blank=True, null=True)
    horasproyectadas = models.FloatField(db_column='HorasProyectadas', blank=True, null=True)
    fechacreacion = models.DateTimeField()
    aprobada = models.IntegerField(db_column='Aprobada', blank=True, null=True)
    fechaaprobacion = models.DateTimeField(blank=True, null=True)
    prioridad = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tareas'



class Tipousuarios(models.Model):
    idtipousuario = models.IntegerField(db_column='idTipoUsuario')
    tipo = models.CharField(db_column='Tipo', max_length=15)
    descripcion = models.CharField(db_column='Descripcion', max_length=50)

    class Meta:
        managed = True
        db_table = 'users_management_tipousuarios'


class Usuarios(models.Model):
    idusuario = models.CharField(db_column='IDUsuario', max_length=16)
    email = models.CharField(max_length=100, blank=True, null=True)
    clave = models.CharField(max_length=32)
    fechacreacion = models.DateTimeField(blank=True, null=True)
    nombre = models.CharField(db_column='Nombre', max_length=255)
    tipousuario = models.CharField(db_column='TipoUsuario', max_length=8)

    class Meta:
        managed = True
        db_table = 'users_management_usuarios'

class Horasdedicadastareas(models.Model):
    codigoproyecto = models.ForeignKey(Proyectos, on_delete=models.CASCADE, db_column='CodigoProyecto')
    codigotarea = models.ForeignKey(Tareas, on_delete=models.CASCADE, db_column='CodigoTarea')
    descripcion = models.CharField(db_column='Descripcion', max_length=250, blank=True, null=True)
    horasdedicadas = models.FloatField(db_column='HorasDedicadas', blank=True, null=True)
    fechacreacion = models.DateTimeField()
    aprobadas = models.IntegerField(db_column='Aprobadas', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'horasdedicadastareas'