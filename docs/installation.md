# Getting Started With Apache Airflow

Installation of airflow is simple, you can find installation details for airflow on the official website [airflow.apache.org](https://airflow.apache.org/docs/stable/start.html) here we shall describe the installation steps for getting ready your development environment specifically for mini-BRS, later we shall describe the process of installation of airflow for mini-BRS on servers.


## Requirements

mini-BRS is tested with:

### Master version

* Python versions: 3.6.9
* Postgres DB: 10.12
* MySQL DB: 8.0
* Sqlite - latest stable (it is used mainly for development purpose)

mini-BRS is tested on

* OS Ubuntu 18.04 - minimum 1 GiB memory & 8 GiB storage.

## Things to keep handy !

mini-BRS has an installer script associated with it that helps you in getting right things installed on your system. 
We encourage use of installer for installing mini-BRS. The installer is interactive as it requires user information to get things configured rightly. Please make sure you have following information in hand, so that you don't 
get stuck during installation process.
* Do you want to install mini-BRS as a service on your server or you just require it to be started manually ?
* mini-BRS requires database for its functioning, for this purpose you need to keep the, database *host ip*,
*username*, *password*, *port*, *database name* in hand.
* If you want to have email alerts, make sure you have SMTP server details like *smtp_host*, *smtp_port*, *email address* and *password* in handy. If you want to use Gmail, Outlook or any other email provider make sure you generate `app password` for that email address. In order to know how to generate `app password` for your email address, refer
[create and use app passwords](https://support.google.com/accounts/answer/185833?hl=en)  

## Getting started

**Installation**

1. clone the repository using git

```bash
~$ git clone https://github.com/Cloud-Innovation-Partners/miniBRS.git
```

2. execute ```install``` script inside the project folder using ```sudo``` command

```bash
~$ sudo ./install
```

Installation script will take care of your needs, it will start downloading the dependencies and requirements for the
project. During installation you will need to provide various information such as,

1. Installer will prompt you for type of installation to you need, you can either install mini-BRS as a ubuntu service or you can let the installer create a python virtual environment for you.

2. Next installer will ask you for the type of database to be used as a meta-database for Airflow, mini-BRS is tested
for SQLite, MySQL and Postgres. You can choose the type of database and provide the specific database credentials during 
installation.

3. mini-BRS provide failure alerts option via email, you can provide the SMTP server to be used for sending failure notifications, incase, workflows fail. You can choose to skip this step, If you don't want email alerts.

4. You will be prompted to create your Airflow UI login credentials, by default username is ```admin``` you can keep the default username and add a password to it.

Once installation is over, if you have chosen to install mini-BRS as service than after installation you will have two
system services installed one for ```airflow-webserver``` and other for ```airflow-scheduler``` active and running on
your machine. You can check the status of the service by

```bash
~$ sudo service airflow-websever status
``` 


```bash
~$ sudo service airflow-scheduler status
``` 

If you have installed mini-BRS as a python virtual environment then you will be having a folder named ```.env``` created
in ```mini-brs``` folder. This folder is the python virtual environment and you can use following command to activate it

>make sure your current working directory is ```mini-brs``` 

```bash
~$ source .env/bin/activate
``` 
Once you activate your virtual environment you can start Airflow webserver and scheduler 


```bash
~$ airflow webserver
``` 


```bash
~$ airflow scheduler
``` 



### Getting Started For Development

> **Prerequisite:** Linux OS, Although any Linux distro would work we prefer Debian distros e.q Ubuntu, Debian etc.  

>For **Red Hat** Linux the process of installation would remain same with slight changes specific to the use of corresponding package manager

>**Windows:** If you are a windows user and you want to run Apache Airflow on windows platform, you would need extra housekeeping, For windows platform, you would need a Virtual Machine simulator like *VirtualBox* / *VMware* for running Linux on Windows or if you are using Windows 10 then you can use the **Windows Sub System For Linux** to have your airflow installed. In any case, the internet is yours go and find it :wink:  

### Steps

It's good to have your ``workspace`` defined when you are working on multiple projects. we would start by defining a workspace for airflow projects and then create new airflow projects inside this workspace. Every project will be an independent installation with a python virtual environment configured for itself, with this we will be able to maintain separation of concern. without further ado let's get started...

1.  create a workspace in your ``home`` directory, simply create a *folder* named ``airflow_workspace``, it's this folder which is going to hold our airflow projects. In Linux simply issue the following command in you ``bash terminal`` with current working directory (``cwd``) as your ``home`` directory.

```bash
~$ mkdir airflow_workspace
```

2. Now, you have your workspace defined, let's now fetch the project from the ``GitLab`` repository. In order to fetch ``mini-BRS`` project from GitLab, you need to have ``git`` installed in your machine. To check if ``git`` is installed, run the below command in your terminal

```bash
~$ git version
```

The output should be something like this :

```bash
git version 2.17.0
```

The version number may differ depending on your machine and time of installation. If the output display's version number that means you have ``git`` installed.

In case, ``git`` is not installed. you can install it by the following command

```bash
~$ sudo apt-get install git
```

Once ``git`` is installed, you can fetch the project from the GitLab repo using below command.

make sure your ``cwd`` is your workspace i.e ``airflow_workspace``

```bash
~$ git clone https://gitlab.com/shahbaz.ali/vf-leap.git
```

3. Now, change your directory to ``mini-BRS`` and enter the following command to create a virtual environment.

>make sure you are using python3.x and not python2.7

```bash
~$ python -m venv .env
```

or 

```bash
~$ python -m virtualenv .env
```

In case, python throws no module ``virtualenv`` found, you need to install the ``virtualenv`` package, to install ``virtualenv`` package use below command

```bash
~$ pip install virtualenv
```
or

```bash
~$ pip3 install virtualenv
```

Now, you have a virtual environment ready for installing the project dependencies :sunglasses: 

4. Before installing the dependencies you need to activate your virtual environment and also set a ``PATH`` variable with the name ``AIRFLOW_HOME`` it's necessary for your ``airflow`` to find the project files. Let's do it one by one .

* with ``mini-BRS`` as your ``cwd`` hit the below command in terminal

```bash
~$ pwd
```
This will give you an output something like this

```
/home/shahbaz/airflow_workspace/mini-BRS
```

copy this output as we need it to set our ``PATH`` variable

* Now use the following command to open an editor

```bash
~$ nano .env/bin/activate
```
This will open a bash script, scroll to the end of the file and paste the following lines at the end of the file

>**make sure you change the value to your specific path that was generated earlier
```bash

#This is for AIRFLOW usage
export AIRFLOW_HOME=/home/shahbaz/airflow_workspace/mini-BRS
```

press CTRL+X and y, to close the editor

* You are ready to activate your virtual environment. enter the following command to activate it

```bash
~$ source .env/lib/activate
```

5. To install project dependencies, we prefer installation using ``requirements.txt`` file. In ``airflow-tdms`` project folder you have a file ``requirement.txt`` which has all the project dependencies list in it. enter the following command to install ``airflow`` and other dependent packages

```bash
~$ pip3 install -r requirement.txt
```
6. Once all the dependencies are installed, its time to initialize your ``airflow`` meta-database

```bash
~$ airflow initdb
```

7. Once you have initialized your airflow db, you can start airflow webserver and scheduler

```bash
~$ airflow webserver
```


```bash
~$ airflow scheduler
```









