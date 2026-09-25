# Migrate an on-premises PostgreSQL database to Aurora PostgreSQL

**Source:** https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/migrate-an-on-premises-postgresql-database-to-aurora-postgresql.html

**Landing file:** news/article_02_migrate-an-on-premises-postgresql-database-to-aurora-postgresql.json

**Crawled:** 2026-09-25T10:20:10

---

_Baji Shaik and Jitender Kumar, Amazon Web Services_
## Summary
Amazon Aurora PostgreSQL-Compatible Edition combines the performance and availability of high-end commercial databases with the simplicity and cost-effectiveness of open-source databases. Aurora provides these benefits by scaling storage across three Availability Zones in the same AWS Region, and supports up to 15 read replica instances for scaling out read workloads and providing high availability within a single Region. By using an Aurora global database, you can replicate PostgreSQL databases in up to five Regions for remote read access and disaster recovery in the event of a Region failure. This pattern describes the steps for migrating an on-premises PostgreSQL source database to an Aurora PostgreSQL-Compatible database. The pattern includes two migration options: using AWS Data Migration Service (AWS DMS) or using native PostgreSQL tools (such as [pg_dump](https://www.postgresql.org/docs/current/app-pgdump.html), [pg_restore](https://www.postgresql.org/docs/current/app-pgrestore.html), and [psql](https://www.postgresql.org/docs/current/app-psql.html)) or third-party tools. 
The steps described in this pattern also apply to target PostgreSQL databases on Amazon Relational Database Service (Amazon RDS) and Amazon Elastic Compute Cloud (Amazon EC2) instances.
## Prerequisites and limitations
**Prerequisites**
  * An active AWS account
  * A PostgreSQL source database in an on-premises data center
  * [An Aurora PostgreSQL-Compatible DB instance](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_GettingStartedAurora.CreatingConnecting.AuroraPostgreSQL.html) or an [Amazon RDS for PostgreSQL DB instance](https://aws.amazon.com/getting-started/hands-on/create-connect-postgresql-db/)


**Limitations**
  * Database size limits are 64 TB for Amazon RDS for PostgreSQL and 128 TB for Aurora PostgreSQL-Compatible.
  * If you’re using the AWS DMS migration option, review [AWS DMS limitations on using a PostgreSQL database as a source](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.PostgreSQL.html#CHAP_Source.PostgreSQL.Limitations).


**Product versions**
  * For PostgreSQL major and minor version support in Amazon RDS, see [Amazon RDS for PostgreSQL updates](https://docs.aws.amazon.com/AmazonRDS/latest/PostgreSQLReleaseNotes/postgresql-versions.html) in the Amazon RDS documentation.
  * For PostgreSQL support in Aurora, see [Amazon Aurora PostgreSQL updates](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraPostgreSQLReleaseNotes/AuroraPostgreSQL.Updates.html) in the Aurora documentation.
  * If you’re using the AWS DMS migration option, see[ supported PostgreSQL versions](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.PostgreSQL.html) in the AWS DMS documentation.


## Architecture
**Source technology stack**
  * On-premises PostgreSQL database


**Target technology stack**
  * Aurora PostgreSQL-Compatible DB instance


**Source architecture**
![Source architecture for on-premises PostgreSQL database](https://docs.aws.amazon.com/images/prescriptive-guidance/latest/patterns/images/pattern-img/82114165-8102-44a2-8b12-485ac9eb8989/images/a8621ad3-781b-45a9-86a8-d0b0ec5c79ea.png)
**Target architecture**
![Target architecture for PostgreSQL database on Amazon Aurora](https://docs.aws.amazon.com/images/prescriptive-guidance/latest/patterns/images/pattern-img/82114165-8102-44a2-8b12-485ac9eb8989/images/fc2ec0cb-7b9b-4cc0-b70c-40e47c2f4c45.png)
**Data migration architecture**
_Using AWS DMS_
![Migrating an on-premises PostgreSQL database to Aurora by using AWS DMS](https://docs.aws.amazon.com/images/prescriptive-guidance/latest/patterns/images/pattern-img/82114165-8102-44a2-8b12-485ac9eb8989/images/5336adb4-e9eb-47d0-a5b5-d149261b1638.png)
_Using native PostgreSQL tools_
![Migrating an on-premises PostgreSQL database to Aurora by using pg_dump and pg_restore](https://docs.aws.amazon.com/images/prescriptive-guidance/latest/patterns/images/pattern-img/82114165-8102-44a2-8b12-485ac9eb8989/images/3c6fb533-45ff-443e-bfb1-97e60cbdd583.png)
## Tools
  * [AWS Database Migration Service (AWS DMS)](https://docs.aws.amazon.com/dms/latest/userguide/Welcome.html) helps you migrate data stores into the AWS Cloud or between combinations of cloud and on-premises configurations. This service supports different sources and target databases. For information about how to validate the PostgreSQL source and target database versions and editions supported for use with AWS DMS, see [Using a PostgreSQL database as an AWS DMS source](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.PostgreSQL.html). We recommend that you use the latest version of AWS DMS for the most comprehensive version and feature support.
  * Native PostgreSQL tools include [pg_dump](https://www.postgresql.org/docs/current/app-pgdump.html), [pg_restore](https://www.postgresql.org/docs/current/app-pgrestore.html), and [psql](https://www.postgresql.org/docs/current/app-psql.html).


## Epics  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Validate the source and target database versions.  | If you are using AWS DMS, make sure that you’re using a [supported version of PostgreSQL](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.PostgreSQL.html).   | DBA  |  
| Identify the storage type and capacity requirements.  | 
  1. Calculate the storage allocated for the source database instance.
  2. Gather the historical growth metrics for the source database instance.
  3. Anticipate the future growth forecast for the target database instance.
  4. Allocate storage by calculating the total number of read and write IOPS on the source database. A General Purpose SSD (`gp2`) volume provides 3 IOPS for each 1 GB of storage.

 | DBA, Systems administrator  |  
| Choose the proper instance type, capacity, storage features, and network features.  |  Determine the compute requirements of the target database instance. Review known performance issues that might need additional attention. Consider the following factors to determine the appropriate instance type:
  * CPU utilization of the source database instance
  * IOPS (read and write operations) for the source database instance
  * Memory footprint on the source database instance

For more information, see [Aurora DB instance classes](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Concepts.DBInstanceClass.html) in the Aurora documentation.  | DBA, Systems administrator  |  
| Identify the network access security requirements for the source and target databases.  | Determine the appropriate security groups that would enable the application to talk to the database.  | DBA, Systems administrator  |  
| Identify the application migration strategy.  | 
  * Determine the migration cutover strategy based on the complexity of your application. 
  * Determine the recovery time objective (RTO) and recovery point objective (RPO) for the application, and plan for the cutover accordingly.

 | DBA, App owner, Systems administrator  |  
## Analyze the migration  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Validate the source and target database versions.  | If you are using AWS DMS, make sure that you’re using a [supported version of PostgreSQL](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.PostgreSQL.html).   | DBA  |  
| Identify the storage type and capacity requirements.  | 
  1. Calculate the storage allocated for the source database instance.
  2. Gather the historical growth metrics for the source database instance.
  3. Anticipate the future growth forecast for the target database instance.
  4. Allocate storage by calculating the total number of read and write IOPS on the source database. A General Purpose SSD (`gp2`) volume provides 3 IOPS for each 1 GB of storage.

 | DBA, Systems administrator  |  
| Choose the proper instance type, capacity, storage features, and network features.  |  Determine the compute requirements of the target database instance. Review known performance issues that might need additional attention. Consider the following factors to determine the appropriate instance type:
  * CPU utilization of the source database instance
  * IOPS (read and write operations) for the source database instance
  * Memory footprint on the source database instance

For more information, see [Aurora DB instance classes](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Concepts.DBInstanceClass.html) in the Aurora documentation.  | DBA, Systems administrator  |  
| Identify the network access security requirements for the source and target databases.  | Determine the appropriate security groups that would enable the application to talk to the database.  | DBA, Systems administrator  |  
| Identify the application migration strategy.  | 
  * Determine the migration cutover strategy based on the complexity of your application. 
  * Determine the recovery time objective (RTO) and recovery point objective (RPO) for the application, and plan for the cutover accordingly.

 | DBA, App owner, Systems administrator  |  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Create a VPC.  | Create a new virtual private cloud (VPC) for the target database instance.  | Systems administrator  |  
| Create security groups.  | Create a security group within the VPC (as determined in the previous epic) to allow inbound connections to the database instance.   | Systems administrator  |  
| Configure and start the Aurora DB cluster.  | Create the target database instance with the new VPC and security group and start the instance.  | Systems administrator  |  
## Configure the infrastructure  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Create a VPC.  | Create a new virtual private cloud (VPC) for the target database instance.  | Systems administrator  |  
| Create security groups.  | Create a security group within the VPC (as determined in the previous epic) to allow inbound connections to the database instance.   | Systems administrator  |  
| Configure and start the Aurora DB cluster.  | Create the target database instance with the new VPC and security group and start the instance.  | Systems administrator  |  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Complete pre-migration steps.  | 
  1. Clean up the data in the source database.
  2. [Create a replication instance](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_ReplicationInstance.Creating.html).
  3. [Create source and target endpoints](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Endpoints.Creating.html).
  4. Identify the number of available tables and objects to be migrated.

 | DBA  |  
| Complete migration steps.  | 
  1. Drop foreign key constraints and triggers on the target database.
  2. Drop secondary indexes on the target database.
  3. Use a [full-load task](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Tasks.CustomizingTasks.TaskSettings.FullLoad.html) to migrate data from the source to the target database.
  4. Enable foreign keys.
  5. If you’re using [flash-cut migration](https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-database-migration/cut-over.html) and your application requires minimal downtime, enable [change data capture](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Appendix.SQLServer.CommonDBATasks.CDC.html) (CDC) to replicate ongoing changes
  6. Enable triggers.
  7. Update sequences.
  8. Validate the source and target data.

 | DBA  |  
| Validate data.  | To ensure that your data was migrated accurately from the source to the target, follow the [data validation steps](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Validating.html) in the AWS DMS documentation.  | DBA  |  
## Migrate data ‒ option 1 (using AWS DMS)  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Complete pre-migration steps.  | 
  1. Clean up the data in the source database.
  2. [Create a replication instance](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_ReplicationInstance.Creating.html).
  3. [Create source and target endpoints](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Endpoints.Creating.html).
  4. Identify the number of available tables and objects to be migrated.

 | DBA  |  
| Complete migration steps.  | 
  1. Drop foreign key constraints and triggers on the target database.
  2. Drop secondary indexes on the target database.
  3. Use a [full-load task](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Tasks.CustomizingTasks.TaskSettings.FullLoad.html) to migrate data from the source to the target database.
  4. Enable foreign keys.
  5. If you’re using [flash-cut migration](https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-database-migration/cut-over.html) and your application requires minimal downtime, enable [change data capture](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Appendix.SQLServer.CommonDBATasks.CDC.html) (CDC) to replicate ongoing changes
  6. Enable triggers.
  7. Update sequences.
  8. Validate the source and target data.

 | DBA  |  
| Validate data.  | To ensure that your data was migrated accurately from the source to the target, follow the [data validation steps](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Validating.html) in the AWS DMS documentation.  | DBA  |  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Prepare the source database.  | 
  1. Create a directory to store pg_dump backup if it doesn’t already exist.
  2. Create a migration user that has permissions to run pg_dump on database objects.
  3. Connect to the EC2 instance and run pg_dump backup.

For more information, see the [pg_dump](https://www.postgresql.org/docs/current/app-pgdump.html) documentation and the [walkthrough](https://docs.aws.amazon.com/dms/latest/sbs/chap-manageddatabases.postgresql-rds-postgresql-full-load-pd_dump.html) in the AWS DMS documentation.  | DBA  |  
| Prepare the target database.  | 
  1. Create a migration user that has permissions to use pg_restore on database objects.
  2. Import the database dump by using pg_restore.

For more information, see the [pg_restore](https://www.postgresql.org/docs/current/app-pgrestore.html) documentation and the [walkthrough](https://docs.aws.amazon.com/dms/latest/sbs/chap-manageddatabases.postgresql-rds-postgresql-full-load-pd_dump.html) in the AWS DMS documentation.  | DBA  |  
| Validate data.  | 
  1. Compare the database object counts between the source and the target databases.
  2. Resolve any discrepancies found between object counts.

 | DBA  |  
## Migrate data ‒ option 2 (using pg_dump and pg_restore)  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Prepare the source database.  | 
  1. Create a directory to store pg_dump backup if it doesn’t already exist.
  2. Create a migration user that has permissions to run pg_dump on database objects.
  3. Connect to the EC2 instance and run pg_dump backup.

For more information, see the [pg_dump](https://www.postgresql.org/docs/current/app-pgdump.html) documentation and the [walkthrough](https://docs.aws.amazon.com/dms/latest/sbs/chap-manageddatabases.postgresql-rds-postgresql-full-load-pd_dump.html) in the AWS DMS documentation.  | DBA  |  
| Prepare the target database.  | 
  1. Create a migration user that has permissions to use pg_restore on database objects.
  2. Import the database dump by using pg_restore.

For more information, see the [pg_restore](https://www.postgresql.org/docs/current/app-pgrestore.html) documentation and the [walkthrough](https://docs.aws.amazon.com/dms/latest/sbs/chap-manageddatabases.postgresql-rds-postgresql-full-load-pd_dump.html) in the AWS DMS documentation.  | DBA  |  
| Validate data.  | 
  1. Compare the database object counts between the source and the target databases.
  2. Resolve any discrepancies found between object counts.

 | DBA  |  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Follow the application migration strategy.  | Implement the application migration strategy that you created in the first epic.  | DBA, App owner, Systems administrator  |  
## Migrate the application  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Follow the application migration strategy.  | Implement the application migration strategy that you created in the first epic.  | DBA, App owner, Systems administrator  |  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Switch the application clients over to the new infrastructure.  | 
  1. Stop all application services and client connections that point to the on-premises PostgreSQL database.
  2. [Run the AWS DMS tasks](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Tasks.html).
  3. Set up a rollback task (reverse CDC from Aurora PostgreSQL-Compatible to the on-premises PostgreSQL database) if needed.
  4. [Validate data](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Validating.html).
  5. Start the application services on the new target by [configuring Amazon Route 53](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-configuring.html) to the new Aurora PostgreSQL-Compatible DB instance.
  6. Add [Amazon CloudWatch](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/monitoring-cloudwatch.html) and [Performance Insights](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_PerfInsights.html) monitoring on your new Aurora PostgreSQL-Compatible DB instance.

 | DBA, App owner, Systems administrator  |  
| If you need to roll back the migration.  | 
  1. Stop all application services that point to the Aurora PostgreSQL-Compatible database.
  2. Roll back the changes to the source on-premises PostgreSQL database by using the AWS DMS task you created in the previous story.
  3. Stop the AWS DMS tasks running from the on-premises PostgreSQL database to the Aurora PostgreSQL-Compatible database.
  4. Configure the application so that it points back to the source on-premises PostgreSQL database.
  5. Confirm that all rollback deployment is complete.

 | DBA, App owner  |  
## Cut over to the target database  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Switch the application clients over to the new infrastructure.  | 
  1. Stop all application services and client connections that point to the on-premises PostgreSQL database.
  2. [Run the AWS DMS tasks](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Tasks.html).
  3. Set up a rollback task (reverse CDC from Aurora PostgreSQL-Compatible to the on-premises PostgreSQL database) if needed.
  4. [Validate data](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Validating.html).
  5. Start the application services on the new target by [configuring Amazon Route 53](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-configuring.html) to the new Aurora PostgreSQL-Compatible DB instance.
  6. Add [Amazon CloudWatch](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/monitoring-cloudwatch.html) and [Performance Insights](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_PerfInsights.html) monitoring on your new Aurora PostgreSQL-Compatible DB instance.

 | DBA, App owner, Systems administrator  |  
| If you need to roll back the migration.  | 
  1. Stop all application services that point to the Aurora PostgreSQL-Compatible database.
  2. Roll back the changes to the source on-premises PostgreSQL database by using the AWS DMS task you created in the previous story.
  3. Stop the AWS DMS tasks running from the on-premises PostgreSQL database to the Aurora PostgreSQL-Compatible database.
  4. Configure the application so that it points back to the source on-premises PostgreSQL database.
  5. Confirm that all rollback deployment is complete.

 | DBA, App owner  |  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Shut down resources.  | Shut down the temporary AWS resources.  | DBA, Systems administrator  |  
| Validate documents.  | Review and validate the project documents.  | DBA, App owner, Systems administrator  |  
| Gather metrics.  | Gather metrics around time to migrate, percent of manual versus tool cost savings, and so on.  | DBA, App owner, Systems administrator  |  
| Close the project.  | Close the project and provide any feedback.  | DBA, App owner, Systems administrator  |  
## Close the project  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Shut down resources.  | Shut down the temporary AWS resources.  | DBA, Systems administrator  |  
| Validate documents.  | Review and validate the project documents.  | DBA, App owner, Systems administrator  |  
| Gather metrics.  | Gather metrics around time to migrate, percent of manual versus tool cost savings, and so on.  | DBA, App owner, Systems administrator  |  
| Close the project.  | Close the project and provide any feedback.  | DBA, App owner, Systems administrator  |  
## Related resources
**References**
  * [AWS Data Migration Service](https://aws.amazon.com/dms/)
  * [VPCs and Amazon Aurora](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_VPC.html)
  * [Amazon Aurora pricing](https://aws.amazon.com/rds/aurora/pricing/)
  * [Using a PostgreSQL database as an AWS DMS source](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.PostgreSQL.html)
  * [How to create an AWS DMS replication instance](https://aws.amazon.com/premiumsupport/knowledge-center/create-aws-dms-replication-instance/)
  * [How to create source and target endpoints using AWS DMS](https://aws.amazon.com/premiumsupport/knowledge-center/create-source-target-endpoints-aws-dms/)


**Additional resources**
  * [Getting Started with AWS DMS](https://aws.amazon.com/dms/getting-started/)
  * [Data migration step-by-step walkthroughs](https://docs.aws.amazon.com/dms/latest/sbs/DMS-SBS-Welcome.html)
  * [Amazon Aurora resources](https://aws.amazon.com/rds/aurora/getting-started/)
