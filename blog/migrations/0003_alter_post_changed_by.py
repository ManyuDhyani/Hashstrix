# Generated by Django 3.2 on 2021-05-03 11:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20210503_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='changed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='blog.postchangeuser'),
        ),
    ]
