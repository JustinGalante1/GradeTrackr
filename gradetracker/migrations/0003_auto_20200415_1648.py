# Generated by Django 3.0.3 on 2020-04-15 23:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gradetracker', '0002_student_cumulativecredits'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='cumulativeCredits',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=4),
        ),
    ]