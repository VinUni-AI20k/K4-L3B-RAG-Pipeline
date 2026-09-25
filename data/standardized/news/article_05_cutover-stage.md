# Cutover stage

**Source:** https://docs.aws.amazon.com/prescriptive-guidance/latest/best-practices-migration-cutover/cutover-stage.html

**Landing file:** news/article_05_cutover-stage.json

**Crawled:** 2026-09-25T10:20:14

---

When you migrate components that store data, you need to consider if data consistency is a key requirement. If it is, then you may need to lock the source environment (such as a database lock) prior to starting the cutover process. Locking the database can ensure that no new transactions are made to the source environment. However, locking may require a larger downtime window.
Cutover generally involves the following phases: 
  * **Ingestion freeze** – Freeze the ingestion of on-premises applications and data into the database. This ensures that the on-premises version of the application doesn't receive any new transactions or data during the cutover.
  * **Backup** – Take the final backup of the on-premises system. If necessary, you can use this backup for the rollback in the event of an emergency.
  * **Data sync** – Complete a final data sync between the on-premises and target (cloud) environments.
  * **Routing changes** – Route users to the cloud environment (for example, updating DNS records or changing load balancer targets).
  * **Testing** – Test and validate that everything is working prior to marking the migration as complete.


## Cutover approach
There are two cutover approaches to consider: an all-at-once approach or a phased approach. The key to choosing the best cutover approach is to understand your business requirements and technical constraints. This section provides an overview of both approaches.
### All-at-once approach
If you take the all-at-once approach, then you cut over the entire solution with a flip of a switch. For example, you can do this by updating the DNS or changing a load balancer. Then, all users and live traffic are immediately using the new system. This approach can be useful in scenarios where you can't bring new systems online due to a potential host-name conflict, license issues, or domain authentication constraints. Because time is critical, the key emphasis is on when or who will call for a failback. We recommend that your plans for an all-at-once approach include extensive performance testing and, where applicable, regression testing, so that you can validate both functional and non-functional features of the application.
### Phased approach (canary deployments)
The phased approach involves a gradual cutover over a defined period of time. This approach includes continuous monitoring and checks to validate if the current system can sustain the load and if each system component is functioning as expected. A phased approach can help reduce the risk of potential cutover issues because you can adjust system performance based on feedback. It's also easier to roll back any changes if you identify critical issues.
### Choosing the right approach
To choose the right approach, identify the following:
  * Dependent applications and services that are part of the same move group
  * Common data sources that can be used between on-premises and migrated applications
  * Applications and infrastructure that can redirect partial loads to different endpoints


If you have an application that can't tolerate increased latency between the data source and the application servers, this is a clear indicator that an all-at-once approach is required. In this scenario, you can cut over all the application resources (servers and databases) together to avoid impacting performance.
In a phased cutover, you split a percentage of the servers and services that constitute an application from the whole and cut over to AWS while the remaining servers and services remain on-premises. Then, you route client traffic to both environments based on load balancing or DNS policy. The phased cutover helps you minimize user impact so that the fewest number of users are affected by the cutover. If you can identify an impact, then you can adjust the percentages of servers and services accordingly. However, a phased cutover approach relies on the ability of your underlying applications to support the approach. We recommend that you ask yourself the following questions:
  * Does the application have multiple tiers (front end, back end, database) made up of resilient pairs or groups of servers that can be split?
  * Is the application accessed through a load balancer and does the load balancer support routing traffic to the AWS network and on-premises network?
  * Can application servers migrated to AWS tolerate latency to a database or other backend dependency. If the database is cut over to AWS, can servers or services remaining on-premises continue to function and perform as required?


The ability to send a percentage of your users to newly migrated servers in AWS while maintaining your existing on-premises capacity has a key advantage over an all-at-once approach when it comes to rollback capability. Because you have a mix of migrated and existing servers that serve the application with a load spread between them, it is both fast and simple to revert back in the event of issues. In most cases, all that's required is a change to a load balancer, DNS rule, or policy. The phased cutover approach also lets you gradually increase load on AWS, which enables application teams to evaluate the performance of the application and make required updates or changes before the full load is transferred.
Choosing whether it's best to cut over an application or stack of dependent applications all at once, or whether to use an incremental approach where servers and services are cut over in stages is unlikely to be a one-size-fits-all decision. We commonly see customers adopt the following approaches:
  * Development and test environments that can tolerate some downtime will benefit from the simplicity and lower level of effort in cutting over with the all-at-once approach.
  * In contrast, the phased approach is more complex and time consuming but typically provides a lower downtime requirement and faster rollback options. For this reason, the phased approach is most commonly adopted for business-critical production workloads.


We recommend taking the time to understand your source systems prior to the cutover change window. By investing more time in the early planning stages, you can support various processes, such as cutover preparation and post-migration validation. Customers may change the IP addresses of their servers when migrating to AWS. In this scenario, the key factor to avoid is having hardcoded IP addresses inside your application. We recommend that you look holistically at your source environment, which can have both upstream or downstream dependencies. For example, you're more likely to cause an issue to other systems that connect to the service you migrated. It's worth considering if there's value in moving all connections to use fully qualified domain names (FQDN) or DNS records prior to starting your cutover.
### When to perform the cutover
In general, the best time for a cutover event is when you have the fewest users, as you'll experience the least business impact. However, this needs to be balanced with availability of support teams during the cutover window. You need support teams to help troubleshoot and resolve potential issues. It's also important to consider the date and time of the cutover along with stakeholder readiness. If any of your stakeholders are not prepared and available at the scheduled date and time, then your cutover can face the risk of delay.
### What to test before cutover
If your migration approach permits, it's a best practice to perform functional and non-functional testing ahead of the cutover window. For example, you can leverage load testing tools to validate if the new environment is appropriately configured ahead of the cutover window. In general, testing during this phase is non-disruptive as the AWS environment isn't serving live traffic.
### What can't be tested before cutover
It might not be possible to test all scenarios that will happen in production due to dependencies with other applications. In such cases, document the potential risks, how you plan to identify the risks, and what corresponding mitigation approaches your team will take if the test fails.
### Operational readiness review
Before you cut over your application to AWS, we recommend that you perform an operational readiness review. This is where you evaluate the completeness of the testing, validate the ability of your team to monitor and obtain alerts, and confirm that your stakeholders understand how to support and maintain the workload. This will likely require working with both business and technical teams. For more information on operational readiness, see the _Operational Excellence Pillar_ of the AWS Well-Architected Framework from [AWS Well-Architected](https://aws.amazon.com/architecture/well-architected/?wa-lens-whitepapers.sort-by=item.additionalFields.sortDate&wa-lens-whitepapers.sort-order=desc&wa-guidance-whitepapers.sort-by=item.additionalFields.sortDate&wa-guidance-whitepapers.sort-order=desc) in the AWS documentation.
## Rollback
A migration rollback may be necessary under certain conditions. To prepare for a potential rollback, we recommend that you develop a rollback plan that includes the following:
  * Defined checkpoints that set off a rollback during the cutover if certain predefined criteria are met
  * A rollback strategy for managing the rollback and handling the data
  * A point of contact who will make the decision to either fix forward or roll back the migration


### Rollback during cutover or without new data
If you and your stakeholders decide to perform a rollback without any data being changed, then the rollback approach can be as simple as resuming the on-premises instances and then redirecting your traffic by modifying load balancer or DNS configurations. 
### Rollback with the changed data
If a rollback is initiated after a successful cutover and your application has received new transactions and data, then you might have to restore the data from the cloud environment to the on-premises environment. We recommend that you consider the following approaches in this scenario:
  * **Fail-forward approach** – Your on-premises database is likely to become stale post-cutover since the post-migration AWS database becomes the main database. You can use [AWS Database Migration Service](https://aws.amazon.com/dms/) (AWS DMS)to set up a fail-forward database, which will replicate the data to a new on-premises database. In the event of any issues, AWS DMS rolls back your applications to a designated fail-forward database rather than to a stale on-premises database.
  * **Dual write strategy** – In this case, your application logic must allow writes to both the old and new database.
  * **Native backup and restore** – To evaluate the time required for the restore, perform backup and restore tests using lower environments (that is, non-production environments) during the pre-cutover stage.
