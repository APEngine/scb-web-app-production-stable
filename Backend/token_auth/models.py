from django.db import models

class Usuarios(models.Model):
    idusuario = models.CharField(db_column='IDUsuario', max_length=16)  # Field name made lowercase.
    email = models.CharField(max_length=100, blank=True, null=True)
    clave = models.CharField(max_length=32)
    fechacreacion = models.DateTimeField(blank=True, null=True)
    nombre = models.CharField(db_column='Nombre', max_length=255)  # Field name made lowercase.
    tipousuario = models.CharField(db_column='TipoUsuario', max_length=8)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'usuarios'