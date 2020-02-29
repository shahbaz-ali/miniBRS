#   vf_leap
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : Shahbaz Ali

from flask_admin import expose
from flask import Markup
from flask_admin.contrib.sqla import ModelView
from flask_admin.actions import action
from plugins.vf_leap.modals.recovery_modals import FailedDagRun, Reason
from wtforms import validators
from airflow.utils import timezone
from airflow.utils.state import State
from airflow.utils.db import provide_session
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.models.variable import Variable
import json
import datetime as dt


def parse_datetime_f(value):
    if not isinstance(value, dt.datetime):
        return value

    return timezone.make_aware(value)

def datetime_f(v, c, m, p):
    attr = getattr(m, p)
    dttm = attr.isoformat() if attr else ''
    if timezone.utcnow().isoformat()[:4] == dttm[:4]:
        dttm = dttm[5:]
    return Markup("<nobr>{}</nobr>").format(dttm)

def state_f(v, c, m, p):
    state = m.state
    color = State.color(m.state)
    return Markup(
        '<span class="label" style="background-color:{color};">'
        '{state}</span>').format(**locals())

def reason_f(v, c, m, p):
    markupstring = "<a href='http://localhost:8080/admin/task_fail_reason/{}${}'>view details</a>".format(str(m.execution_date)[:19],m.dag_id)
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
            ('recovery_executed','recovery_executed'),
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
    column_filters = ('state','dag_id')
    column_searchable_list = ('dag_id', 'state', 'run_id')

    column_formatters = dict(
        execution_date=datetime_f,
        state=state_f,
        failure_reason = reason_f
    )

    @action('trigger_dag','Trigger DAG','Are you sure you want to re-run this dag, you can run this dag only once, make sure all dependencies are met')
    @provide_session

    def trigger_dag(self,ids,session=None):

        rows = session.query(FailedDagRun).filter(FailedDagRun.id.in_(ids)).all()

        try:
            r_config = Variable.get(key='r_config')
            r_obj = json.loads(r_config)

            for d in rows:
                if r_obj.__contains__(d.dag_id):
                    if not (r_obj[d.dag_id]).__contains__(str(d.execution_date)[:19]):
                        r_obj[d.dag_id].append(str(d.execution_date)[:19])
                    else:
                        pass
                else:
                    r_obj[d.dag_id] = [str(d.execution_date)[:19]]

            Variable.set(key='r_config',value=json.dumps(r_obj))
        except KeyError as e:
            LoggingMixin().log.warn(e.__str__())
            Variable.set(key='r_config',value='{}')
            self.create_r_config(ids,session)



    def create_r_config(self,ids,session):

        rows = session.query(FailedDagRun).filter(FailedDagRun.id.in_(ids)).all()

        r_obj = {}

        for d in rows:
            # if r_obj.__contains__(d.dag_id):
            #     if not (r_obj[d.dag_id]).__contains__(d.execution_date):
            #         r_obj[d.dag_id].append(str(d.execution_date))
            # else:
            r_obj[d.dag_id] = [str(d.execution_date)[:19]]

        Variable.set(key='r_config', value=json.dumps(r_obj))



    def get_query(self):
        """
            Default filters for model
            """
        return super(RecoveryDashboard, self).get_query().filter(FailedDagRun.get_state(FailedDagRun) == 'failed' )



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
        'val' : 'Value'
    }


    def is_visible(self):
        return False

    @expose('/<string:id>',methods=['GET'])
    def __index__(self,id):
        self.param_id = id
        return super().index_view()

    def get_query(self):
        x = super(TaskInstanceFailureVariable, self).get_query().filter(Reason.key == str(self.param_id))
        print(x)
        return x


