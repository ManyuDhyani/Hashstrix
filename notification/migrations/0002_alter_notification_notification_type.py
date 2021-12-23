# Generated by Django 3.2 on 2021-05-26 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.IntegerField(choices=[(1, 'Like'), (2, 'Comment'), (3, 'Follow'), (4, 'Reply')]),
        ),
    ]
