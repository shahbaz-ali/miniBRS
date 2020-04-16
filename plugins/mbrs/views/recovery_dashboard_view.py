#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   http://cloudinp.com

"""
This module contains ModelView class, and add-on functions for view customization
These ModelView class are used by airflow plugin manager to render the custom mini BRS
views

    Example :
        RecoveryDashboard maps to FailedDags in airflow UI

"""
import json
import datetime as dt
import airflow
from flask_admin import expose
from flask import Markup, request
from flask_admin.contrib.sqla import ModelView
from flask_admin.actions import action
from wtforms import validators
from airflow.utils import timezone
from airflow.utils.state import State
from airflow.utils.db import provide_session
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.models.variable import Variable
from sqlalchemy import func
from plugins.mbrs.modals.recovery_modals import FailedDagRun, Reason

airflow.load_login()

current_user = airflow.login.current_user


def parse_datetime_f(value):
    """
    Flask Admin Helper function
    :param value:
    :return:
    """
    if not isinstance(value, dt.datetime):
        return value

    return timezone.make_aware(value)


def datetime_f(view, context, model, name):
    """
    Flask Admin Helper function
    Purpose : used to parse the `execution_date`
    :param view:
    :param context:
    :param model:
    :param name:
    :return:
    """

    attr = getattr(model, name)
    datetime = attr.isoformat() if attr else ''
    if timezone.utcnow().isoformat()[:4] == datetime[:4]:
        datetime = datetime[5:]
    return Markup("<nobr>{}</nobr>").format(datetime)


def state_f(view, context, model, name):
    """
    Flask Admin Helper function
    Purpose : used to set the state color
    :param view:
    :param context:
    :param model:
    :param name:
    :return:
    """
    state = model.state
    color = State.color(model.state)
    return Markup(
        '<span class="label" style="background-color:{color};">'
        '{state}</span>').format(**locals())


def reason_f(view, context, model, name):
    """
    Flask Admin Helper function
    Purpose : used to show `view_details` in the Flask Admin list_view
    :param view:
    :param context:
    :param model:
    :param name:
    :return:
    """

    markupstring = "<a href='http://{}/admin/task_fail_reason/{}${}'>view details</a>"\
        .format(request.host, str(model.execution_date)[:19], model.dag_id)
    return Markup(markupstring)


class RecoveryDashboard(ModelView):

    can_edit = False
    can_create = False
    can_view_details = False
    list_template = 'airflow/model_list.html'
    edit_template = 'airflow/model_edit.html'
    create_template = 'airflow/model_create.html'
    column_display_actions = True
    page_size = 10
    verbose_name_plural = "Failed DAG Runs"
    column_default_sort = ('execution_date', True)
    form_choices = {
        '_state': [
            ('success', 'success'),
            ('running', 'running'),
            ('failed', 'failed'),
            ('recovery_executed', 'recovery_executed'),
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
        'state', 'dag_id', 'execution_date', 'run_id', 'external_trigger', 'failure_reason')
    column_filters = ('state', 'dag_id')
    column_searchable_list = ('dag_id', 'state', 'run_id')

    column_formatters = dict(
        execution_date=datetime_f,
        state=state_f,
        failure_reason=reason_f
    )

    @action('trigger_dag',
            'Trigger DAG',
            'Are you sure you want to re-run this dag, you can run this dag only once, '
            'make sure all dependencies are met')
    @provide_session
    def trigger_dag(self, ids, session=None):
        """
        Flask Admin `action` method
        Purpose : used to trigger the selected Failed DAG
        :param ids:
        :param session:
        :return:
        """

        rows = session.query(FailedDagRun).filter(FailedDagRun.id.in_(ids)).all()

        try:
            r_config = Variable.get(key='r_config')
            r_obj = json.loads(r_config)

            for id_ in rows:
                if r_obj.__contains__(id_.dag_id):
                    if not (r_obj[id_.dag_id]).__contains__(str(id_.execution_date)[:19]):
                        r_obj[id_.dag_id].append(str(id_.execution_date)[:19])
                    else:
                        pass
                else:
                    r_obj[id_.dag_id] = [str(id_.execution_date)[:19]]

            Variable.set(key='r_config', value=json.dumps(r_obj))

            for id_ in ids:

                execution_date = session.query(FailedDagRun)\
                    .filter(FailedDagRun.id == id_)\
                    .one()\
                    .execution_date

                dag_id = session.query(FailedDagRun)\
                    .filter(FailedDagRun.id == id_)\
                    .one()\
                    .dag_id

                session.query(FailedDagRun).filter(FailedDagRun.id == id_).update(
                    {'state': 'recovery_executed'}, synchronize_session='fetch')

                Variable.delete(key="{}${}".format(str(execution_date)[:19], dag_id))

        except KeyError as e:
            LoggingMixin().log.warn(e.__str__())
            Variable.set(key='r_config', value='{}')
            RecoveryDashboard.create_r_config(ids, session)

    @staticmethod
    def create_r_config(ids, session):
        """
        This method is used to create and populate `r_config` variable  
        :param ids:
        :param session:
        :return:
        """

        rows = session.query(FailedDagRun).filter(FailedDagRun.id.in_(ids)).all()

        r_obj = {}

        for row in rows:
            if r_obj.__contains__(row.dag_id):
                if not (r_obj[row.dag_id]).__contains__(row.execution_date):
                    r_obj[row.dag_id].append(str(row.execution_date))
            else:
                r_obj[row.dag_id] = [str(row.execution_date)[:19]]

        Variable.set(key='r_config', value=json.dumps(r_obj))

        for id_ in ids:
            execution_date = session.query(FailedDagRun)\
                .filter(FailedDagRun.id == id_)\
                .one()\
                .execution_date

            dag_id = session.query(FailedDagRun)\
                .filter(FailedDagRun.id == id_)\
                .one()\
                .dag_id

            session.query(FailedDagRun).filter(FailedDagRun.id == id_).update(
                {'state': 'recovery_executed'}, synchronize_session='fetch')

            Variable.delete(key="{}${}".format(str(execution_date)[:19], dag_id))

    def is_accessible(self):
        return current_user.is_authenticated

    def get_query(self):
        """
            Default filters for model
            """

        return super(RecoveryDashboard, self).get_query()\
            .filter(FailedDagRun.get_state(FailedDagRun) == 'failed')

    def get_count_query(self):

        self.session.query(func.count('*'))\
            .select_from(FailedDagRun)\
            .filter(FailedDagRun.get_state(FailedDagRun) == 'failed')


class TaskInstanceFailureVariable(ModelView):
    can_edit = False
    can_create = False
    list_template = 'airflow/model_list.html'
    edit_template = 'airflow/model_edit.html'
    create_template = 'airflow/model_create.html'
    column_display_actions = True
    page_size = 10
    verbose_name_plural = "Task Instances"
    column_list = (
        'key', 'val')
    column_labels = {
        'val': 'Value'
    }

    def is_visible(self):
        return False

    @expose('/<string:id_>', methods=['GET'])
    def __index__(self, id_):
        self.param_id = id_
        return super().index_view()

    def get_query(self):
        return super(TaskInstanceFailureVariable, self).get_query()\
            .filter(Reason.key == str(self.param_id))
