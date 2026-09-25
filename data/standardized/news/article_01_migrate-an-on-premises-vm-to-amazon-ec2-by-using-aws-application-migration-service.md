# Migrate an on-premises VM to Amazon EC2 by using AWS Application Migration Service

**Source:** https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/migrate-an-on-premises-vm-to-amazon-ec2-by-using-aws-application-migration-service.html

**Landing file:** news/article_01_migrate-an-on-premises-vm-to-amazon-ec2-by-using-aws-application-migration-service.json

**Crawled:** 2026-09-25T10:20:09

---

_Thanh Nguyen, Amazon Web Services_
## Summary
When it comes to application migration, organizations can take different approaches to rehost (lift and shift) the application’s servers from the on-premises environment to the Amazon Web Services (AWS) Cloud. One way is to provision new Amazon Elastic Compute Cloud (Amazon EC2) instances and then install and configure the application from scratch. Another approach is to use third-party or AWS native migration services to migrate multiple servers at the same time.
This pattern outlines the steps for migrating a supported virtual machine (VM) to an Amazon EC2 instance on the AWS Cloud by using AWS Application Migration Service. You can use the approach in this pattern to migrate one or multiple virtual machines manually, one by one, or automatically by creating appropriate automation scripts based on the outlined steps. 
## Prerequisites and limitations
**Prerequisites**
  * An active AWS account in one of the AWS Regions that support Application Migration Service
  * Network connectivity between the source server and target EC2 server through a private network by using AWS Direct Connect or a virtual private network (VPN), or through the internet


**Limitations**
  * For the latest list of supported Regions, see the [Supported AWS Regions](https://docs.aws.amazon.com/mgn/latest/ug/supported-regions.html).
  * For a list of supported operating systems, see the [Supported operating systems](https://docs.aws.amazon.com/mgn/latest/ug/Supported-Operating-Systems.html) and the _General_ section of [Amazon EC2 FAQs](https://aws.amazon.com/ec2/faqs/).


## Architecture
**Source technology stack**
  * A physical, virtual, or cloud-hosted server running an operating system supported by Amazon EC2


**Target technology stack**
  * An Amazon EC2 instance running the same operating system as the source VM
  * Amazon Elastic Block Store (Amazon EBS)


**Source and target architecture**
The following diagram shows the high-level architecture and main components of the solution. In the on-premises data center, there are virtual machines with local disks. On AWS, there is a staging area with replication servers and a migrated resources area with EC2 instances for test and cutover. Both subnets contain EBS volumes.
![Main components to migrate a supported VM to an Amazon EC2 instance on the AWS Cloud.](https://docs.aws.amazon.com/images/prescriptive-guidance/latest/patterns/images/pattern-img/58c8bafd-9a6d-42d4-a5ce-08c4b9a286a3/images/f8396fad-7ee9-4f75-800f-e819f509e151.png)
  1. Initialize AWS Application Migration Service.
  2. Set up the staging area server configuration and reporting, including staging area resources.
  3. Install agents on source servers, and use continuous block-level data replication (compressed and encrypted).
  4. Automate orchestration and system conversion to shorten the cutover window.


**Network architecture**
The following diagram shows the high-level architecture and main components of the solution from the networking perspective, including required protocols and ports for communication between primary components in the on-premises data center and on AWS.
![Networking components including protocols and ports for communication between data center and AWS.](https://docs.aws.amazon.com/images/prescriptive-guidance/latest/patterns/images/pattern-img/58c8bafd-9a6d-42d4-a5ce-08c4b9a286a3/images/2f594daa-ddba-4841-8785-6067e8d83c2f.png)
## Tools
  * [AWS Application Migration Service](https://docs.aws.amazon.com/mgn/latest/ug/what-is-application-migration-service.html) helps you rehost (_lift and shift_) applications to the AWS Cloud without change and with minimal downtime.


## Best practices
  * Do not take the source server offline or perform a reboot until the cutover to the target EC2 instance is complete.
  * Provide ample opportunity for the users to perform user acceptance testing (UAT) on the target server to identify and resolve any issues. Ideally, this testing should start at least two weeks before cutover.
  * Frequently monitor the server replication status on the Application Migration Service console to identify issues early on.
  * Use temporary AWS Identity and Access Management (IAM) credentials for agent installation instead of permanent IAM user credentials.


## Epics  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Create the AWS Replication Agent IAM role.  |  Sign in with administrative permissions to the AWS account. On the AWS Identity and Access Management (IAM) [console](https://console.aws.amazon.com/iam/), create an IAM role:
  1. On the IAM console, choose **Roles**.
  2. Choose **Create role**.
  3. On the **Select trusted entity** page,**** in**Trusted entity type** section, select **AWS Account**.
  4. In the **An AWS account** section, select **This account ( <_account-id >_)**.
  5. Choose **Next**.
  6. On the**Add permissions** page, search for the `AWSApplicationMigrationAgentInstallationPolicy` policy, select the check box next to the policy name.
  7. Choose **Next**.
  8. On the **Role details** page, enter **MGN_Agent_Installation_Role** as the role name.
  9. Verify that the fields are correct, and then choose **Create role**.

 | AWS administrator, Migration engineer  |  
| Generate temporary security credentials.  |  On a machine with AWS Command Line Interface (AWS CLI) installed, sign in with administrative permissions. Or alternatively (within a supported AWS Region), on the AWS Management Console, sign in with administrative permissions to the AWS account, and open AWS CloudShell. Generate temporary credentials with the following command, replacing `<account-id>` with the AWS account ID. `aws sts assume-role --role-arn arn:aws:iam::<account-id>:role/MGN_Agent_Installation_Role --role-session-name mgn_installation_session_role` From the output of the command, copy the values for `AccessKeyId`,****`SecretAccessKey` , and****`SessionToken`.**** Store them in a safe location for later use.
###### Important
These temporary credentials will expire after one hour. If you need credentials after one hour, repeat the previous steps.  | AWS administrator, Migration engineer  |  
## Generate AWS credentials  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Create the AWS Replication Agent IAM role.  |  Sign in with administrative permissions to the AWS account. On the AWS Identity and Access Management (IAM) [console](https://console.aws.amazon.com/iam/), create an IAM role:
  1. On the IAM console, choose **Roles**.
  2. Choose **Create role**.
  3. On the **Select trusted entity** page,**** in**Trusted entity type** section, select **AWS Account**.
  4. In the **An AWS account** section, select **This account ( <_account-id >_)**.
  5. Choose **Next**.
  6. On the**Add permissions** page, search for the `AWSApplicationMigrationAgentInstallationPolicy` policy, select the check box next to the policy name.
  7. Choose **Next**.
  8. On the **Role details** page, enter **MGN_Agent_Installation_Role** as the role name.
  9. Verify that the fields are correct, and then choose **Create role**.

 | AWS administrator, Migration engineer  |  
| Generate temporary security credentials.  |  On a machine with AWS Command Line Interface (AWS CLI) installed, sign in with administrative permissions. Or alternatively (within a supported AWS Region), on the AWS Management Console, sign in with administrative permissions to the AWS account, and open AWS CloudShell. Generate temporary credentials with the following command, replacing `<account-id>` with the AWS account ID. `aws sts assume-role --role-arn arn:aws:iam::<account-id>:role/MGN_Agent_Installation_Role --role-session-name mgn_installation_session_role` From the output of the command, copy the values for `AccessKeyId`,****`SecretAccessKey` , and****`SessionToken`.**** Store them in a safe location for later use.
###### Important
These temporary credentials will expire after one hour. If you need credentials after one hour, repeat the previous steps.  | AWS administrator, Migration engineer  |  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Initialize the service.  |  On the console, sign in with administrative permissions to the AWS account. Choose **Application Migration Service** , and then choose **Get started**.  | AWS administrator, Migration engineer  |  
| Create and configure the Replication Settings template.  | 
  1. Provide the following configuration details:
    1. Select the staging area subnet.
    2. Select the replication server instance type (`t3.small` by default).
    3. Select the EBS volume type (gp3 by default).
    4. Select the EBS encryption option.
    5. Ensure that the **Always use Application Migration Service security group** check box is selected.
    6. Select the **Use private IP for data replication (VPN, DirectConnect, VPC peering)** check box if you are using private network connectivity between the on-premises environment and AWS.
    7. Select the **Throttle network bandwidth (per server - in Mbps)** check box if you want to limit the network bandwidth for Application Migration Service.
  2. Choose **Create template**.

Application Migration Service will automatically create all the IAM roles required to facilitate data replication and the launching of migrated servers.  | AWS administrator, Migration engineer  |  
## Initialize Application Migration Service and create the Replication Settings template  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Initialize the service.  |  On the console, sign in with administrative permissions to the AWS account. Choose **Application Migration Service** , and then choose **Get started**.  | AWS administrator, Migration engineer  |  
| Create and configure the Replication Settings template.  | 
  1. Provide the following configuration details:
    1. Select the staging area subnet.
    2. Select the replication server instance type (`t3.small` by default).
    3. Select the EBS volume type (gp3 by default).
    4. Select the EBS encryption option.
    5. Ensure that the **Always use Application Migration Service security group** check box is selected.
    6. Select the **Use private IP for data replication (VPN, DirectConnect, VPC peering)** check box if you are using private network connectivity between the on-premises environment and AWS.
    7. Select the **Throttle network bandwidth (per server - in Mbps)** check box if you want to limit the network bandwidth for Application Migration Service.
  2. Choose **Create template**.

Application Migration Service will automatically create all the IAM roles required to facilitate data replication and the launching of migrated servers.  | AWS administrator, Migration engineer  |  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Have the required AWS credentials ready.  | When you run the installer file on a source server, you will need to enter the temporary credentials that you generated earlier, including `AccessKeyId`, `SecretAccessKey`, and `SessionToken`.  | Migration engineer, AWS administrator  |  
| For Linux servers, install the agent.  | Copy the installer command, log in to your source servers, and run the installer. For detailed instructions, see the [AWS documentation](https://docs.aws.amazon.com/mgn/latest/ug/linux-agent.html).  | AWS administrator, Migration engineer  |  
| For Windows servers, install the agent.  | Download the installer file to each server, and then run the installer command. For detailed instructions, see the [AWS documentation](https://docs.aws.amazon.com/mgn/latest/ug/windows-agent.html).  | AWS administrator, Migration engineer  |  
| Wait for initial data replication to be completed.  | When the agent has been installed, the source server will appear on the Application Migration Service console, in the **Source servers** section. Wait while the server undergoes initial data replication.  | AWS administrator, Migration engineer  |  
## Install AWS Replication Agents on source machines  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Have the required AWS credentials ready.  | When you run the installer file on a source server, you will need to enter the temporary credentials that you generated earlier, including `AccessKeyId`, `SecretAccessKey`, and `SessionToken`.  | Migration engineer, AWS administrator  |  
| For Linux servers, install the agent.  | Copy the installer command, log in to your source servers, and run the installer. For detailed instructions, see the [AWS documentation](https://docs.aws.amazon.com/mgn/latest/ug/linux-agent.html).  | AWS administrator, Migration engineer  |  
| For Windows servers, install the agent.  | Download the installer file to each server, and then run the installer command. For detailed instructions, see the [AWS documentation](https://docs.aws.amazon.com/mgn/latest/ug/windows-agent.html).  | AWS administrator, Migration engineer  |  
| Wait for initial data replication to be completed.  | When the agent has been installed, the source server will appear on the Application Migration Service console, in the **Source servers** section. Wait while the server undergoes initial data replication.  | AWS administrator, Migration engineer  |  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Specify the server details.  | On the Application Migration Service console, choose the **Source servers** section, and then choose a server name from the list to access the server details.  | AWS administrator, Migration engineer  |  
| Configure the launch settings.   | Choose the **Launch settings** tab. You can configure a variety of settings, including general launch settings and EC2 launch template settings. For detailed instructions, see the [AWS documentation](https://docs.aws.amazon.com/mgn/latest/ug/launch-settings.html).  | AWS administrator, Migration engineer  |  
## Configure launch settings  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Specify the server details.  | On the Application Migration Service console, choose the **Source servers** section, and then choose a server name from the list to access the server details.  | AWS administrator, Migration engineer  |  
| Configure the launch settings.   | Choose the **Launch settings** tab. You can configure a variety of settings, including general launch settings and EC2 launch template settings. For detailed instructions, see the [AWS documentation](https://docs.aws.amazon.com/mgn/latest/ug/launch-settings.html).  | AWS administrator, Migration engineer  |  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Test the source servers.  | 
  1. On the Application Migration Service console, in the **Source servers** section, ensure that the source servers’ **Migration lifecycle** is **Ready for testing** and that **Data replication status** is **Healthy**.
  2. Select the check box to the left of each source server.
  3. Choose **Test and Cutover** , and then choose **Launch Test Instance**.
  4. When prompted, choose **Launch**.

The servers will be launched.  | AWS administrator, Migration engineer  |  
| Verify that the test completed successfully.  | After the test server is completely launched, the **Alerts** status on the page will show **Launched** for each server.  | AWS administrator, Migration engineer  |  
| Test the server.  | Perform testing against the test server to ensure that it functions as expected.  | AWS administrator, Migration engineer  |  
## Perform a test  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Test the source servers.  | 
  1. On the Application Migration Service console, in the **Source servers** section, ensure that the source servers’ **Migration lifecycle** is **Ready for testing** and that **Data replication status** is **Healthy**.
  2. Select the check box to the left of each source server.
  3. Choose **Test and Cutover** , and then choose **Launch Test Instance**.
  4. When prompted, choose **Launch**.

The servers will be launched.  | AWS administrator, Migration engineer  |  
| Verify that the test completed successfully.  | After the test server is completely launched, the **Alerts** status on the page will show **Launched** for each server.  | AWS administrator, Migration engineer  |  
| Test the server.  | Perform testing against the test server to ensure that it functions as expected.  | AWS administrator, Migration engineer  |  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Schedule a cutover window.  | Schedule an appropriate cutover timeframe with relevant teams.  | AWS administrator, Migration engineer  |  
| Perform the cutover.  | 
  1. On the Application Migration console, on the **Source Servers** page, select the check box to the left of each source server.
  2. Choose **Test and Cutover** , and select **Mark as 'Ready for cutover'**.
  3. Verify that each source server's **Migration lifecycle** is **Ready for cutover**.
  4. Choose **Test and Cutover** , and then select **Launch cutover instances**.
  5. When prompted, choose **Launch**. The servers will be launched.

The source server's **Migration lifecycle** will change to **Cutover in progress**.  | AWS administrator, Migration engineer  |  
| Verify that the cutover completed successfully.  | After the cutover servers are completely launched, the **Alerts** status on the **Source Servers** page will show **Launched** for each server.  | AWS administrator, Migration engineer  |  
| Test the server.  | Perform testing against the cutover server to ensure that it functions as expected.  | AWS administrator, Migration engineer  |  
| Finalize the cutover.  | Choose **Test and Cutover** , and then select **Finalize cutover** to finalize the migration process.  | AWS administrator, Migration engineer  |  
## Schedule and perform a cutover  
| Task  | Description  | Skills required  |  
| --- | --- | --- |  
| Schedule a cutover window.  | Schedule an appropriate cutover timeframe with relevant teams.  | AWS administrator, Migration engineer  |  
| Perform the cutover.  | 
  1. On the Application Migration console, on the **Source Servers** page, select the check box to the left of each source server.
  2. Choose **Test and Cutover** , and select **Mark as 'Ready for cutover'**.
  3. Verify that each source server's **Migration lifecycle** is **Ready for cutover**.
  4. Choose **Test and Cutover** , and then select **Launch cutover instances**.
  5. When prompted, choose **Launch**. The servers will be launched.

The source server's **Migration lifecycle** will change to **Cutover in progress**.  | AWS administrator, Migration engineer  |  
| Verify that the cutover completed successfully.  | After the cutover servers are completely launched, the **Alerts** status on the **Source Servers** page will show **Launched** for each server.  | AWS administrator, Migration engineer  |  
| Test the server.  | Perform testing against the cutover server to ensure that it functions as expected.  | AWS administrator, Migration engineer  |  
| Finalize the cutover.  | Choose **Test and Cutover** , and then select **Finalize cutover** to finalize the migration process.  | AWS administrator, Migration engineer  |  
## Related resources
  * [AWS Application Migration Service](https://aws.amazon.com/application-migration-service/)
  * [AWS Application Migration Service User Guide](https://docs.aws.amazon.com/mgn/latest/ug/what-is-application-migration-service.html)
