Installing miniBRS
==================

miniBRS can be installed either using an Installer script or manually. Using the Installer is the most easiest 
and straightforward way to install and configure miniBRS. If you are using Ubuntu 18.04 you can install using Installer
script, For any other OS you would have to do the installation and configuration manually.

---

Prerequisites
-------------

** Database **

You need a database on your database server. If you don’t have a database yet, you can use SQLite database 
which is default database of Airflow. This will give you an opportunity to test miniBRS even before your database administrator 
creates a database for you. `Just note, that SQLite is not suitable for production environment`.


mini-BRS is tested with

* Postgres DB: 10.12
* MySQL DB: 8.0
* Sqlite - latest stable (it is used mainly for testing purpose)


** Email Server **

You would need an `Email Server` in case you want email alerts for your workflows, 
Make sure you have SMTP server details like `smtp_host`, `smtp_port`, `email address` and `password` in handy.
If you don't have an Email Server, you can use Gmail, Outlook or any other email provider make sure you generate 
`app password` for your email address. In order to know how to generate `app password` for your Gmail account, refer
[here](https://support.google.com/accounts/answer/185833?hl=en)  

---

Installation
------------


** Using Installer Script**

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

1. Installer will prompt you for type of installation you need, you can either install mini-BRS as a ubuntu service or you can let the installer create a python virtual environment for you.

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

---

Manual Installation
-------------------
> **Prerequisite:** Linux OS, Although any Linux distro would work we prefer Debian distros e.q Ubuntu, Debian etc.  

>For **Red Hat** Linux the process of installation would remain same with slight changes specific to the use of corresponding package manager

>**Windows:** If you are a windows user and you want to run Apache Airflow on windows platform, you would need extra housekeeping, For windows platform, you would need a Virtual Machine simulator like *VirtualBox* / *VMware* for running Linux on Windows or if you are using Windows 10 then you can use the **Windows Sub System For Linux** to have your airflow installed. In any case, the internet is yours go and find it :wink:  

Steps
---
It's good to have your ``workspace`` defined when you are working on multiple projects. 
we would start by defining a workspace for airflow projects and then create new airflow projects inside this workspace. 
Every project will be an independent installation with a python virtual environment configured for itself, with this we will be able to maintain separation of concern. 
without further ado let's get started...

---
* create a workspace in your ``home`` directory, simply create a *folder* named ``airflow_workspace``, it's this folder which is going to hold our airflow projects. In Linux simply issue the following command in you ``bash terminal`` with current working directory (``cwd``) as your ``home`` directory.

```bash
~$ mkdir airflow_workspace
```

---

* Now, you have your workspace defined, let's now fetch the project from the ``GitHub`` repository. In order to fetch ``miniBRS`` project from GitHub, you need to have ``git`` installed in your machine. To check if ``git`` is installed, run the below command in your terminal

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

Once ``git`` is installed, you can fetch the project from the GitHub repo using below command.

make sure your ``cwd`` is your workspace i.e ``airflow_workspace``

```bash
~$ git clone https://github.com/Cloud-Innovation-Partners/miniBRS.git
```
---

* Now, change your directory to ``miniBRS`` and enter the following command to create a virtual environment.

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

---

* Before installing the dependencies you need to activate your virtual environment and also set a ``PATH`` variable with the name ``AIRFLOW_HOME`` it's necessary for your ``airflow`` to find the project files. Let's do it one by one .

* with ``miniBRS`` as your ``cwd`` hit the below command in terminal

```bash
~$ pwd
```
This will give you an output something like this

```
/home/<user_name>/airflow_workspace/miniBRS
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
export AIRFLOW_HOME=/home/<user_name>/airflow_workspace/miniBRS
```

press CTRL+X and y, to close the editor

* You are ready to activate your virtual environment. enter the following command to activate it

```bash
~$ source .env/lib/activate
```

---

* To install project dependencies, we prefer installation using ``requirements.txt`` file. In ``airflow-tdms`` project folder you have a file ``requirement.txt`` which has all the project dependencies list in it. enter the following command to install ``airflow`` and other dependent packages

```bash
~$ pip3 install -r requirement.txt
```

---

* Once all the dependencies are installed, its time to initialize your ``airflow`` meta-database

```bash
~$ airflow initdb
```
---

* Once you have initialized your airflow db, you can start airflow webserver and scheduler

```bash
~$ airflow webserver
```


```bash
~$ airflow scheduler
```









