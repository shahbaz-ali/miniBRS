#   vf_leap
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : Shahbaz Ali

from flask_admin import BaseView,expose
from flask_admin.contrib.sqla import ModelView
from plugins.vf_leap.modals.recovery_modals import DagRunModel
from wtforms import validators
from airflow.utils import timezone
import datetime as dt


def parse_datetime_f(value):
    if not isinstance(value, dt.datetime):
        return value

    return timezone.make_aware(value)



class RecoveryDashboard(ModelView):

    can_edit = False
    can_create = False
    page_size = 10
    verbose_name_plural = "Failed DAG Runs"
    column_default_sort = ('execution_date', True)
    form_choices = {
        '_state': [
            ('success', 'success'),
            ('running', 'running'),
            ('failed', 'failed'),
        ],
    }
    form_args = {
        'dag_id': {
            'validators': [
                validators.DataRequired(),
            ]
        },
        'execution_date': {
            'filters': [
                parse_datetime_f,
            ]
        }
    }


    column_list = (
        'state', 'dag_id', 'execution_date', 'run_id', 'external_trigger', 'Reason')

    def get_query(self):
        """
            Default filters for model
            """
        return super(RecoveryDashboard, self).get_query().filter(DagRunModel.get_state(DagRunModel) == 'failed')


