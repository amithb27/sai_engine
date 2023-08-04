# Generated by Django 4.1.7 on 2023-07-29 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sailytics', '0003_rename_testcase_scripts_rename_build_stmbuild'),
    ]

    operations = [
        migrations.RenameField(
            model_name='scripts',
            old_name='failed_testCase',
            new_name='failed_testCases',
        ),
        migrations.RenameField(
            model_name='scripts',
            old_name='passed_testCase',
            new_name='passed_testCases',
        ),
        migrations.RenameField(
            model_name='scripts',
            old_name='total_testCase',
            new_name='total_testCases',
        ),
        migrations.RenameField(
            model_name='stmbuild',
            old_name='failed_testCase',
            new_name='failed_testCases',
        ),
        migrations.RenameField(
            model_name='stmbuild',
            old_name='passed_testCase',
            new_name='pass_percentage',
        ),
        migrations.RenameField(
            model_name='stmbuild',
            old_name='total_testCase',
            new_name='passed_testCases',
        ),
        migrations.AddField(
            model_name='stmbuild',
            name='total_testCases',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]