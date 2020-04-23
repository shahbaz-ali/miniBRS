# How miniBRS Works

This article assumes that you have **`miniBRS`** up and running on your machine and now you want to start using it, by scheduling
few DAGs. Before moving ahead in this article, please make sure you already have checked out the [Settings](settings.md)
article, As we are going to use concepts and settings defined there, In explaining **`incident`** use case. Without any further ado
Let's get started.  

## Incident Backup Use Case

Here we shall explain to you, How you can register your Service Now instance and a storage platform such as Amazon S3 in **`miniBRS`** 
and change the configuration settings provided as per your requirement. We shall use a step by step process to explain this use case.

1. **Register Instance:** The current version of **`miniBRS`** is designed to serve one **`Service Now`** instance at a 
    time. This means, a single instance of **`miniBRS`** must be dedicated to a single instance of **`Service Now`**. All workflows provided by **`miniBRS`** assume that the **`Service Now`** instance that is to be used by the system is registered with **`servicenow_default`** connection id. So, you must override the values in the connection id 
    **`servicenow_default`**. This connection id has dummy values at the installation time which needs to be overridden by user-specific values. In case this connection id is not present due to some reason, The system will throw an exception
    **`ServiceNowConnectionNotFoundException`**
    
    <br/>
    
2. **Register Storage:** Registering storage in **`miniBRS`** is similar to registering your service now instance. 
    Once you have decided which storage to use for your data ingestion, Specify the storage_type in the **`config`** 
    variable. **`storage_type`** attribute of **`config`** variable takes values such as `"sftp", "s3", "dropbox", "mysql", "postgres", "mssql"`. 
    
    Once you have specified the type now you need to provide the details of the storage in its specific connection id.
    For each supported storage platform **`miniBRS`** has a default connection id specific to it in the Connections table. 
    e.g If you want to use SFTP as your storage site, you need to provide details in **`sftp_default`** connection, similarly,
    for Amazon S3 storage you can place your **`s3_access_key_id`** and **`s3_secret_key_id`** respectively in the **`Login`**
    and **`Password`** fields of the **`s3_default`** connection id also for **`s3_region_name`** and **`s3_bucket_name`**
    you can use **`Extras`** field to specify your values. Please refer to [Settings](settings.md#connections) page for
    details about the connections available.
    
        Important Note:
         
        Once you specify your storage type to be used in 
        `storage_type` attribute of `config` variable, 
        The system expects the credentials of that 
        storage type in its specific connection id, 
        If the connection id for the storage is not
        present system will throw storage exception 
        specific to that storage e.g 
        `SFTPConnectionNotFoundException`, 
        `S3ConnectionNotFound Exception` etc
    <br/>
      
3. **Set config values:** So, you have registered your service now instance and storage with **`miniBRS`**, Now you want to start generating workflows. To generate workflows you need to set the values in the **`config`** variable.
    Please check the details of each attribute provided in **`config`** variable at [Settings](settings.md#variables) page
    
    Decide which table you need to fetch data from and add the table name in the **`tables`** list, Also decide how many days ago system should fetch data from your instance and set the value of **`start_date`** to the number of days in past.
    
    Decide how often you need to fetch the records and set the value to **`frequency`** attribute of the **`config`** variable.
    If you want to have email alerts, set the value of the **`email`** attribute the recipient email address, make sure you use email option only after you have configured email server for the system.
    
    
Once you complete all the steps mentioned above, **`miniBRS`** will start reading the configuration and generate the workflows
for you. You must wait about **2 minutes** to get your changes reflected in the UI. You can check the generated workflows
from the DAGs UI of the webserver.

<br/>  
