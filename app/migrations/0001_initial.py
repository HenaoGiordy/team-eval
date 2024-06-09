# Generated by Django 5.0 on 2024-06-09 19:26

import django.contrib.auth.models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Calificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calificacion', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)])),
                ('descripcion', models.TextField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Criterio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.TextField(max_length=200)),
                ('peso', models.DecimalField(decimal_places=2, max_digits=2)),
            ],
        ),
        migrations.CreateModel(
            name='Curso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField(max_length=50)),
                ('codigo', models.TextField(max_length=20)),
                ('fecha_curso', models.DateField()),
                ('periodo', models.TextField(choices=[('I', 'I'), ('II', 'II')])),
                ('has_finished', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('ADMIN', 'ADMIN'), ('ESTUDIANTE', 'ESTUDIANTE'), ('PROFESOR', 'PROFESOR')], max_length=50)),
                ('username', models.CharField(error_messages={'blank': 'Este campo no puede estar vacío.', 'unique': 'Ya existe un usuario con ese código'}, help_text='El código de usuario es único y de debe ser un valor numérico.', max_length=20, unique=True, verbose_name='Codigo')),
                ('first_name', models.CharField(max_length=150, verbose_name='first name')),
                ('email', models.EmailField(max_length=254, verbose_name='email address')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Evaluacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=300)),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
                ('evaluados', models.SmallIntegerField(default=0)),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.curso')),
            ],
        ),
        migrations.CreateModel(
            name='PerfilEstudiante',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField()),
                ('cursos', models.ManyToManyField(to='app.curso')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Grupo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField(max_length=50)),
                ('proyecto_asignado', models.TextField(max_length=50)),
                ('has_evaluated', models.BooleanField(default=False)),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.curso')),
                ('estudiantes', models.ManyToManyField(to='app.perfilestudiante')),
            ],
        ),
        migrations.CreateModel(
            name='PerfilProfesor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='curso',
            name='profesor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.perfilprofesor'),
        ),
        migrations.CreateModel(
            name='Resultado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criterio_evaluado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.criterio')),
                ('evaluacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.evaluacion')),
                ('evaluado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evaluado', to='app.perfilestudiante')),
                ('evaluador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evaluador', to='app.perfilestudiante')),
                ('nota', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.calificacion')),
            ],
        ),
        migrations.CreateModel(
            name='Retroalimentracion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('retroalimentacion', models.CharField(max_length=500)),
                ('estudiante_retroalimentacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.perfilestudiante')),
                ('evaluacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.evaluacion')),
            ],
        ),
        migrations.CreateModel(
            name='Rubrica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField(max_length=50)),
                ('is_used', models.BooleanField(default=False)),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='evaluacion',
            name='rubrica',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.rubrica'),
        ),
        migrations.AddField(
            model_name='criterio',
            name='rubrica',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.rubrica'),
        ),
        migrations.AddField(
            model_name='calificacion',
            name='rubrica',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.rubrica'),
        ),
        migrations.AddConstraint(
            model_name='curso',
            constraint=models.UniqueConstraint(fields=('codigo', 'periodo'), name='unique_codigo_periodo'),
        ),
        migrations.AddConstraint(
            model_name='resultado',
            constraint=models.UniqueConstraint(fields=('evaluador', 'evaluado', 'criterio_evaluado', 'evaluacion'), name='unique_resultado'),
        ),
    ]
