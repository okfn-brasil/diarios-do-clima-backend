# Generated by Django 4.0.3 on 2022-07-20 00:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='alert_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
