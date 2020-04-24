<pre>
           _       _       ____  ____  ____
 _ __ ___ (_)_ __ (_)     | __ )|  _ \/ ___|
| '_ ` _ \| | '_ \| |_____|  _ \| |_) \___ \
| | | | | | | | | | |_____| |_) |  _ < ___) |
|_| |_| |_|_|_| |_|_|     |____/|_| \_\____/   version 1.0
</pre>


[![Build Status](https://travis-ci.org/Cloud-Innovation-Partners/miniBRS.svg?branch=v1-0-dev)](https://travis-ci.org/Cloud-Innovation-Partners/miniBRS) ![license](https://img.shields.io/badge/license-Apache2-blue) ![Github docs](https://img.shields.io/badge/docs-passing-green) ![python](https://img.shields.io/badge/python-3.6-blue)

mini-BRS is a tool that provides data backup facility via programmatic workflows scheduled and monitored by Apache Airflow. It uses Airflow in back end as workflow management tool.

It provides workflows (DAGs) that helps in getting SaaS data exported regularly. You can use existing DAGs or can create your own custom DAGs, mini-BRS provides you a scalable platform which helps you with the ingestion of SaaS data to any cloud or local network storage.

# Documentation
Full documentation is available at https://minibrs.readthedocs.io/ .

---

# Table of Contents

**First Steps**

* **[Installation](docs/installation.md)**
    - [Prerequisites](docs/installation.md#prerequisites)
    - [Installation](docs/installation.md#installation)
    - [Manual Installation](docs/installation.md#manual-installation)
    - [References](docs/installation.md#references)
* **[Upgrade](docs/upgrade.md)**

**Getting Started**

* **[Settings](docs/settings.md)**
    - [Concepts](docs/settings.md#concepts)
    - [How to Use](docs/settings.md#how-to-use)
    - [Connections](docs/settings.md#connections)
    - [Variables](docs/settings.md#variables)
    - [Notifications](docs/settings.md#notifications)
* **[How It Works](docs/how_it_works.md)**
    - [Incident Backup Use Case](docs/how_it_works.md#incident-backup-use-case)

**Advanced Features**

* **[Hooks & Operators](docs/hooks_and_operators.md)**
    - [Hooks](docs/hooks_and_operators.md#hooks)
    - [Operators](docs/hooks_and_operators.md#operators)
* **[Recovery & Logs](docs/logs.md)**
    - [Recovery](docs/logs.md)
    - [Failed DAGs](docs/logs.md#failed-dags)
    - [Logs](docs/logs.md#logs)

**About**

* **[Who Maintains mini-BRS](docs/about.md#who-maintains-mini-brs)**
* **[License](docs/LICENSE.md)**
