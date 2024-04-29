# Generated by Django 4.2.11 on 2024-04-25 08:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import quiz_app.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('full_name', models.CharField(max_length=120)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', quiz_app.models.CustomUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='QuizQuestion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('question', models.TextField(blank=True, max_length=3000, null=True)),
                ('option_a', models.CharField(blank=True, max_length=250, null=True)),
                ('option_b', models.CharField(blank=True, max_length=250, null=True)),
                ('option_c', models.CharField(blank=True, max_length=250, null=True)),
                ('option_d', models.CharField(blank=True, max_length=250, null=True)),
                ('correct_option', models.CharField(blank=True, max_length=120, null=True)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz_app.quiz')),
            ],
        ),
        migrations.CreateModel(
            name='QuizForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_photo', models.FileField(blank=True, null=True, upload_to='user_photos/', validators=[quiz_app.models.validate_file_extension])),
                ('full_name', models.CharField(max_length=120)),
                ('dob', models.DateField()),
                ('age', models.IntegerField()),
                ('father_name', models.CharField(max_length=120)),
                ('phone_number', models.IntegerField()),
                ('alter_phone_number', models.IntegerField()),
                ('email', models.EmailField(max_length=254)),
                ('qualifications', models.CharField(max_length=200)),
                ('occupation_or_profession', models.CharField(max_length=200)),
                ('address', models.CharField(max_length=550)),
                ('city', models.CharField(max_length=120)),
                ('district', models.CharField(max_length=120)),
                ('pincode', models.IntegerField()),
                ('state', models.CharField(max_length=120)),
                ('aadhar_card', models.FileField(blank=True, null=True, upload_to='aadhar/', validators=[quiz_app.models.validate_file_extension])),
                ('payment_done', models.BooleanField(default=False)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]