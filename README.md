# CIP - mini-BRS

mini BRS is platform that provides Service Now data backup facility via programmatic work flows scheduled and monitored
by Apache Airflow. mini BRS uses Airflow in back end as work flow management tool

mini BRS provides you bunch of work flows (DAGs) that help you in getting your Service Now data needs satisfied. You can
use existing DAGs or can create your own custom DAGs, mini BRS provides you a scalable platform which helps you with the
ingestion of Service Now data to any cloud or local network storage.

**Table of Contents**

* [Requirements](#requirements)
* [Getting started](#getting-started)
* [User Interface](#user-interface)
* [Hooks & Operators](#hooks-&-operators)
* [Service Now DAGs](#service-now-dags)
* [Who Maintains Mini BRS ?](#who-maintains-mini-brs-?)


## Requirements

Mini BRS is tested with:

### Master version

* Python versions: 3.6
* Postgres DB: 9.6, 10
* MySQL DB: 5.7
* Sqlite - latest stable (it is used mainly for development purpose)

Mini BRS is tested on

* OS Ubuntu 18.04 - minimum 1 GiB memory & 8 GiB storage.

## Getting started

**Installation**

1. clone the repository using git

```bash
~$ git clone https://gitlab.com/shahbaz.ali/mini-brs.git
```

2. execute ```install``` script inside the project folder using ```sudo``` command

```bash
~$ sudo ./install
```

Installation script will take care of your needs, it will start downloading the dependencies and requirements for the
project. During installation you will need to provide various info. let's go through it one by one

1. Installer will prompt you for type of installation, you can install mini BRS as a ubuntu service or you can let the
installer create a python virtual environment for you. you can select your specific option

2. Next installer will ask you for the type of database to be used as a meta-database for Airflow, mini BRS is tested
for SQLite, MySQL and Postgres. you can choose the type of database and provide the specific database credentials during 
installation

3. Mini BRS has failure alerting via email, you can provide the SMTP server to be used for sending failure notification
if you work flows fails. You can choose to skip this step if you don't want email alerts on failure

4. You will be prompted for creating your Airflow UI login credentials, by default username is ```admin``` you can keep 
default username and add a password to it.

Once installation is over, if you have chosen to install mini BRS as service than after installation you will have two
system services installed one for ```airflow-webserver``` and other for ```airflow-scheduler``` active and running on
your machine. You can check the status of the service by

```bash
~$ sudo service airflow-websever status
``` 


```bash
~$ sudo service airflow-scheduler status
``` 

If you have installed mini BRS as a python virtual environment then you will be having a folder named ```.env``` created
in ```mini-brs``` folder. This folder is the python virtual environment and you can use following command you activate 

>make sure your current working directory is ```mini-brs``` 

```bash
~$ source .env/bin/activate
``` 
Once you activate you virtual environment you can start Airflow webserver and scheduler 


```bash
~$ airflow webserver
``` 


```bash
~$ airflow scheduler
``` 

## User Interface

Apache Airflow provides a great UI for monitoring of you DAGs

* **DAGs**: mini-BRS overview of DAGs

![](images/mbrs_dags.png)

* **Graph View**: generated Service Now DAG's dependencies and their current status for a specific run.

![](images/mbrs_graph_view.png)


## Hooks & Operators
Current version of mini BRS contains Hooks and Operators designed for Service Now platform. Following Operators and Hooks
are the part of current release and in future various other operators and hooks will be released to support cloud platforms

**Hook's**
*  servicenow_hook

**Operator's**
* servicenow_to_sftp_transfer_operator
* servicenow_to_s3_transfer_operator
* servicenow_to_dropbox_transfer_operator

## Who Maintains Mini BRS ?
Mini BRS is the work of the open source team of Cloud Innovation Partners (CIP), but the core committers/maintainers are
responsible for reviewing and merging PRs as well as steering conversation around new feature requests. 
If you would like to become a maintainer, please review the Mini BRS committer requirements.