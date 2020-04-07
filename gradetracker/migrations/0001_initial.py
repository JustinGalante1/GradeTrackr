# Generated by Django 2.2.6 on 2020-04-05 07:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Finished_Course', models.BooleanField(default=False)),
                ('Verified_Class', models.BooleanField(default=False)),
                ('Include_In_GPA', models.BooleanField(default=True)),
                ('Professor_Email', models.EmailField(max_length=254, null=True)),
                ('Average_From_VAgrades', models.DecimalField(decimal_places=3, max_digits=4, null=True)),
                ('name', models.CharField(max_length=100)),
                ('number_Of_Credits', models.DecimalField(decimal_places=1, max_digits=2)),
                ('target_Grade', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='GradeCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('weightage', models.DecimalField(decimal_places=2, max_digits=4)),
                ('courseItBelongsTo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='gradetracker.Course')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('cumulativeCredits', models.DecimalField(decimal_places=1, max_digits=4, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SingularGradeItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gradePercentage', models.DecimalField(decimal_places=2, max_digits=5)),
                ('datetimeWhenInputted', models.DateTimeField(auto_now_add=True)),
                ('didGradeGoUp', models.BooleanField(null=True)),
                ('whichCoursesAvgGradeIsThis', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='courseAvgGrade', to='gradetracker.Course')),
                ('whichGradeCategorysAvgGradeIsThis', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='gradeCategory', to='gradetracker.GradeCategory')),
                ('whichStudentsCumulativeGPAisThis', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cumGPA', to='gradetracker.Student')),
                ('whichStudentsSemesterGPAisThis', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='semGPA', to='gradetracker.Student')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='student_It_Belongs_To',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='gradetracker.Student'),
        ),
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gradePercentage', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('notifyStudentOrNot', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=100)),
                ('dueDate', models.DateTimeField(null=True)),
                ('gradeCategoryItBelongsTo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='gradetracker.GradeCategory')),
            ],
        ),
    ]