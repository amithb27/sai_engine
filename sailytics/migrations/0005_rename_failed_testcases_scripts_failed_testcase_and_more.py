# Generated by Django 4.1.7 on 2023-07-29 12:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sailytics', '0004_rename_failed_testcase_scripts_failed_testcases_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='scripts',
            old_name='failed_testCases',
            new_name='failed_testCase',
        ),
        migrations.RenameField(
            model_name='scripts',
            old_name='passed_testCases',
            new_name='passed_testCase',
        ),
        migrations.RenameField(
            model_name='scripts',
            old_name='total_testCases',
            new_name='total_testCase',
        ),
        migrations.RenameField(
            model_name='stmbuild',
            old_name='failed_testCases',
            new_name='failed_testCase',
        ),
        migrations.RenameField(
            model_name='stmbuild',
            old_name='passed_testCases',
            new_name='passed_testCase',
        ),
        migrations.RenameField(
            model_name='stmbuild',
            old_name='total_testCases',
            new_name='total_testCase',
        ),
    ]
