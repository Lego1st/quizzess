# Generated by Django 2.1.2 on 2018-11-07 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilestatistic',
            name='course',
            field=models.CharField(choices=[('Logic', 'Logic'), ('Probability', 'Probability'), ('Calculus', 'Calculus'), ('Geometry fundamental', 'Geometry fundamental'), ('Computer science', 'Computer science')], max_length=100),
        ),
    ]
