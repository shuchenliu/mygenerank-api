""" A series of tasks relating to reporting status to Admins. """
import os, uuid
from collections import Counter
from datetime import datetime, timedelta

from celery import shared_task, chord, group
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from generank.api import models
from generank.compute.contextmanagers import record
from generank.compute.models import TaskStatus


def _get_stats_for_tasks(tasks):
    counts = Counter([task.identifier for task in tasks])
    affected_users = [task.user for task in tasks if task.user is not None]
    return {
        'counts': {
            **{'all': len(tasks)},
            **counts
        },
        'users_affected': {
            'count': len(affected_users),
            'ids': [user.id for user in affected_users]
        }
    }


def _sort_tasks_into_groups(all_tasks):
    failed = [t for t in all_tasks if t.status.lower() == 'failed']
    succeeded = [t for t in all_tasks if t.status.lower() != 'failed']

    return [
        ('all', all_tasks),
        ('failed', failed),
        ('succeeded', succeeded)
    ]


def _get_daily_tasks():
    now = timezone.now()
    yesterday = now - timedelta(hours=24)
    return yesterday, now, TaskStatus.objects.filter(start_date__gt=yesterday)


def _send_email_to_admins(stats):
    admins = [email for _, email in settings.ADMINS if email is not None]
    html = render_to_string('admin-daily-report.html', stats)
    subject = render_to_string('admin-daily-report.subject.txt', stats).strip()
    send_mail(subject, '', settings.EMAIL_HOST_USER,
        admins, fail_silently=False, html_message=html)


@shared_task
def get_daily_task_stats():
    with record('tasks.compute.admin.get_daily_task_stats'):
        start, end, tasks = _get_daily_tasks()
        groups = _sort_tasks_into_groups(tasks)
        stats = {
            name: _get_stats_for_tasks(tasks)
            for name, tasks in groups
        }
        return start, end, stats


@shared_task
def get_daily_report():
    with record('tasks.compute.admin.get_daily_report'):
        start, end, task_stats = get_daily_task_stats()
        return {
            'start_date': start,
            'end_date': end,
            'tasks': task_stats
        }


@shared_task
def send_daily_report_to_admins():
    with record('tasks.compute.admin.send_daily_report_to_admins'):
        report = get_daily_report()
        _send_email_to_admins(report)
