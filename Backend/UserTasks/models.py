# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
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
    is_superuser = models.IntegerField()
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


class Horasdedicadastareas(models.Model):
    codigoproyecto = models.CharField(db_column='CodigoProyecto', max_length=10)  # Field name made lowercase.
    codigotarea = models.CharField(db_column='CodigoTarea', max_length=10, blank=True, null=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=250, blank=True, null=True)  # Field name made lowercase.
    horasdedicadas = models.FloatField(db_column='HorasDedicadas', blank=True, null=True)  # Field name made lowercase.
    fechacreacion = models.DateTimeField()
    aprobadas = models.IntegerField(db_column='Aprobadas', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'horasdedicadastareas'


class Proyectos(models.Model):
    codigoproyecto = models.CharField(db_column='CodigoProyecto', max_length=10)  # Field name made lowercase.
    codigocliente = models.CharField(db_column='codigoCliente', max_length=8, blank=True, null=True)  # Field name made lowercase.
    tipoproyecto = models.CharField(db_column='TipoProyecto', max_length=5)  # Field name made lowercase.
    programador = models.CharField(db_column='Programador', max_length=8, blank=True, null=True)  # Field name made lowercase.
    administrador = models.CharField(db_column='Administrador', max_length=8)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=100)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=250, blank=True, null=True)  # Field name made lowercase.
    horasproyectadas = models.IntegerField(db_column='HorasProyectadas', blank=True, null=True)  # Field name made lowercase.
    fechacreacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'proyectos'


class Tareas(models.Model):
    codigoproyecto = models.CharField(db_column='CodigoProyecto', max_length=10)  # Field name made lowercase.
    codigotarea = models.CharField(db_column='CodigoTarea', max_length=10)  # Field name made lowercase.
    programador = models.CharField(db_column='Programador', max_length=8)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=100)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=250, blank=True, null=True)  # Field name made lowercase.
    horasproyectadas = models.FloatField(db_column='HorasProyectadas', blank=True, null=True)  # Field name made lowercase.
    fechacreacion = models.DateTimeField()
    aprobada = models.IntegerField(db_column='Aprobada', blank=True, null=True)  # Field name made lowercase.
    fechaaprobacion = models.DateTimeField(blank=True, null=True)
    prioridad = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tareas'


class Tipoproyectos(models.Model):
    nomeclatura = models.CharField(db_column='Nomeclatura', max_length=10)  # Field name made lowercase.
    idnomeclatura = models.IntegerField(db_column='idNomeclatura')  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'tipoproyectos'
        unique_together = (('id', 'idnomeclatura'),)


class Tipousuarios(models.Model):
    idtipousuario = models.IntegerField(db_column='idTipoUsuario')  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=15)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'tipousuarios'


class Usuarios(models.Model):
    idusuario = models.CharField(db_column='IDUsuario', max_length=16)  # Field name made lowercase.
    email = models.CharField(max_length=100, blank=True, null=True)
    clave = models.CharField(max_length=32)
    fechacreacion = models.DateTimeField(blank=True, null=True)
    nombre = models.CharField(db_column='Nombre', max_length=255)  # Field name made lowercase.
    tipousuario = models.CharField(db_column='TipoUsuario', max_length=8)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'usuarios'
