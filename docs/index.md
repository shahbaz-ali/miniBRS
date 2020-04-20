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

* ###[Installation](installation.md)
    - [Requirements](installation.md#requirements)
    - [Things to keep handy !](installation.md#things-to-keep-handy-!)
    - [Getting started](installation.md#getting-started)
<br/>    
* ###[User Interface](user_interface.md)
    - [How to Use](user_intserface.md#how-to-use)
    - [What miniBRS can do](user_interface.md#what-mini-brs-can-do-)
    - [Connections](user_interface.md#connections)
    - [Variables](user_interface.md#variables)
<br />
* ###[Hooks & Operators](hooks_and_operators.md)
* ###[License](LICENSE.md)
* ###[About](about.md)
    - [Who Maintains mini-BRS](about.md#who-maintains-mini-brs)
    - [Cloud Innovation Partners](about.md#cloud-innovation-partners)

---