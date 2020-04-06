# CIP - mini-BRS

mini BRS is a tool that provides Service Now data backup facility via programmatic work flows scheduled and monitored
by Apache Airflow. mini BRS uses Airflow in back end as work flow management tool

mini BRS provides you work flows (DAGs) that help getting Service Now data exported regularly. You can
use existing DAGs or can create your own custom DAGs, mini BRS provides you a scalable platform which helps you with the
ingestion of Service Now data to any cloud or local network storage.

**Table of Contents**

* [Requirements](#requirements)
* [Getting started](#getting-started)
* [User Interface](#user-interface)
* [How to Use](#how-to-use)
* [Hooks & Operators](#hooks-&-operators)
* [Who Maintains Mini BRS](#who-maintains-mini-brs)


## Requirements

Mini BRS is tested with:

### Master version

* Python versions: 3.6.9
* Postgres DB: 10.12
* MySQL DB: 8.0
* Sqlite - latest stable (it is used mainly for development purpose)

Mini BRS is tested on

* OS Ubuntu 18.04 - minimum 1 GiB memory & 8 GiB storage.

## Getting started

**Installation**

1. clone the repository using git

```bash
~$ git clone https://gitlab.com/shahbaz.ali/mini-brs.git
```

## Things to keep handy !

>mini BRS has an installer script associated with it that helps you in getting right things installed on your system. 
we encourage use of installer for installing mini BRS. The installer is interactive and will require information from 
user side to get things configured rightly. please make sure you have following information in hand, so that you don't 
get stuck during installation process.
>* Do you want to install mini BRS as a service on your server or you just require it to be started manually ?
>* mini BRS requires database for its functioning, make sure you have following info in hand, database host ip,
username, password, port, database name.
>* If you want to have email alerting, make sure you have SMTP server details like smtp_host, smtp_port, email address and
password in hand. if you want to use Gmail, Outlook or any other email provider make sure you generate app password for 
that email address. In order to know more how to generate app password for you email address checkout this link
[create and use app passwords](https://support.google.com/accounts/answer/185833?hl=en)  



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

## How to Use
Mini BRS use Apache Airflow as a work flow management platform, if you are not aware of basic concepts of Airflow please
checkout the [documentation](https://airflow.apache.org/docs/stable/concepts.html)  

### What Mini BRS Can Do ?
* It can be used to backup you Service Now data
* It can be used to ingest historical data to cloud storage's
* Can be used to orchestrate your custom work flows for Service Now


### Connections
Before running any work flows (DAG's) make sure you specify requisite connections to the external services required for
functioning of work flows

connection's can be found via **Admin** tab in the navigation bar, Click on Admin tab and select **Connections** from the
drop down menu, you will be redirected to airflow connections page, Airflow allows you to store your external connection
details in the meta database via this page. few connections are of specific importance to mini BRS and you as a user is
required to configure these connections based on your specific needs. Let's have a look at few of the connections that
we need to be sure of.  

#### servicenow_default:
```servicenow_default``` is the connection entry in the meta database which will hold your service now instance credentials.
This connection is where you would store your service now instance url and login credentials. If you edit this connection
by clicking on the edit connection icon, you will have form with fields like Conn Id, Conn Type, Host etc. please do not 
change the Conn Id value. Add your service now instance url to Host field of the form you need to add the url with 'https'
option added e.g if you instance is dev1234.service-now.com save it as https://dev1234.service-now.com in the 'Host' field
of the form, Also you need to add service now user name to 'Login' field and password to 'Password' field of the form.

#### sftp_default:
```sftp_connection``` If you want to ingest your service now instance data to an SFTP account, you can add the SFTP connection
details in this Connection entry. Add sftp account name in the `Login` field and sftp account password in the `Password`
field of the form, nothing else needs to be changed.

#### s3_default:
```s3_default``` If you want to ingest your service now instance data to Amazon S3 account, you need to have 'access_key_id' 
and 'secret_key_id' for your s3 storage. Add `access_key_id` to `Login` and `secret_key_id` to `Password` field of the 
`s3_default` connection 

#### dropbox_default:
`dropbox_default` mini BRS provides you an option to ingest your service now instance data to `Dropbox` account for this
you need to generate `access_token` for your dropbox account and add that `access_token` to the `Password` field of the
connection. In order to generate `access_token` for you account please check out the following [link](#)

### Variables
Mini BRS uses Airflow Variable as a single point to configure Service Now work flows. Once you have installed Mini BRS and 
added service now and storage connection details to the there respective connection ids, you can configure your work flows 
via configuration variables provided by mini BRS. you can find configuration variables via Airflow UI, goto Admin link in nav bar, 
click Variables options you will see few variables already defined. these variables are needed to be present for Mini BRS functioning
![](images/variables.png)

**config**: ```config``` variable provides you options to generate work flows. it uses JSON format to store values. 

```json
{
  "tables": ["incident","problem","sc_request"], 
  "start_date": "1da", 
  "frequency": "hourly", 
  "threshold": 10000, 
  "export_format": "xml", 
  "storage_type": "dropbox", 
  "email": ""
}
```

Options

 - tables : ```tables[]``` is an array where you can add the Service Now table names as comma separated values from which
 you want to ingest data to the storage. please ensure the values inside the table should be valid Service Now table names
 
 - start_date : ```start_date``` provides you a way to get historical data from your Service Now instance. its takes values
 of format ```xda``` where ```x``` is an integer value and specifies the number of days to go back in time to get fetch data
 
 - frequency : ```frequency``` refers the schedule interval of the work flow. its can take value such as ```half-hourly```,
 ```hourly```, ```daily``` etc. 
 
 - threshold : ```threshold``` is used to specify the threshold of records fetched from the Service Now instance. by default 
 its placed at its maximum value of 10000, placing a value greater than 10000 is not going to do any good, if the threshold 
 of data records for a specific run exceeds threshold no data will be fetched for that period
 
 - export_type: ```export_type``` is used to specify the format of data to be stored in the storage, default is ```xml```
 
 - storage_type: ```storage_type``` is used to specify the type of storage to used for ingesting data, currently mini BRS
  has three storage's supported AmazonS3, DropBox, SFTP the credentials of these storage's are to be stored in 
  Airflow Connections in their specific connection_ids.
  
 - email: ```email``` If you have configured SMTP server details during installation or you have manually set them in
 ```airflow.cfg``` file  then you can specify the email_address here to which the failure alerts should be sent.
 
 
 The other two variables ```dag_creation_dates``` and ```r_config``` are meant for internal usage, there presence is
 necessary for normal functioning of Mini BRS


## Hooks & Operators
Current version of mini BRS contains Hooks and Operators designed for Service Now platform. Following Operators and Hooks
are the part of current release and in future various other operators and hooks will be released to support cloud platforms

**Hook's**
*  servicenow_hook

**Operator's**
* servicenow_to_sftp_transfer_operator
* servicenow_to_s3_transfer_operator
* servicenow_to_dropbox_transfer_operator


## Who Maintains Mini BRS
Mini BRS is the work of the open source team of Cloud Innovation Partners (CIP), and CIP team is 
responsible for reviewing and merging PRs as well as steering conversation around new feature requests. 