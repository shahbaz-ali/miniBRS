# User Manual

<pre>
           _       _       ____  ____  ____
 _ __ ___ (_)_ __ (_)     | __ )|  _ \/ ___|
| '_ ` _ \| | '_ \| |_____|  _ \| |_) \___ \
| | | | | | | | | | |_____| |_) |  _ < ___) |
|_| |_| |_|_|_| |_|_|     |____/|_| \_\____/   version 1.0
</pre>


[![Build Status](https://travis-ci.org/Cloud-Innovation-Partners/miniBRS.svg?branch=v1-0-dev)](https://travis-ci.org/Cloud-Innovation-Partners/miniBRS) ![license](https://img.shields.io/badge/license-Apache2-blue) ![Github docs](https://img.shields.io/badge/docs-passing-green) ![python](https://img.shields.io/badge/python-3.6-blue)

mini-BRS is a tool that provides data backup facility via programmatic workflows scheduled and monitored
by Apache Airflow. It uses Airflow in back end as workflow management tool.

It provides workflows (DAGs) that helps in getting SaaS data exported regularly. You can use existing DAGs or can create your own custom DAGs, mini-BRS provides you a scalable platform which helps you with the
ingestion of SaaS data to any cloud or local network storage.

---

#Table of Contents

**First Steps**

* **[Installation](installation.md)**
    - [Prerequisites](installation.md#prerequisites)
    - [Installation](installation.md#installation)
    - [Manual Installation](installation.md#manual-installation)
    - [References](installation.md#references)
* **[Upgrade](upgrade.md)**

**Getting Started**

* **[Settings](settings.md)**
    - [Concepts](settings.md#concepts)
    - [How to Use](settings.md#how-to-use)
    - [Connections](settings.md#connections)
    - [Variables](settings.md#variables)
    - [Notifications](settings.md#notifications)
* **[How It Works](how_it_works.md)**
    - [Incident Backup Use Case](how_it_works.md#incident-backup-use-case)

**Advanced Features**

* **[Hooks & Operators](hooks_and_operators.md)**
    - [Hooks](hooks_and_operators.md#hooks)
    - [Operators](hooks_and_operators.md#operators)
* **[Recovery & Logs](logs.md)**
    - [Recovery](logs.md)
    - [Failed DAGs](logs.md#failed-dags)
    - [Logs](logs.md#logs)

**About**

* **[Who Maintains mini-BRS](about.md#who-maintains-mini-brs)**
* **[License](LICENSE.md)**

---