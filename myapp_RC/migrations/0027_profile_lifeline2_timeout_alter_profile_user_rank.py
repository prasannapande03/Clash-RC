# Generated by Django 4.0.5 on 2023-05-12 03:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp_RC', '0026_rename_lifelin2_secondattempt_profile_lifeline2_secondattempt'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='lifeline2_timeout',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user_rank',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
