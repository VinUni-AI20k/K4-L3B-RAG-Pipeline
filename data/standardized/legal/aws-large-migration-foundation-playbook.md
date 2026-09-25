# Foundation playbook for AWS large migrations

**Source:** https://docs.aws.amazon.com/pdfs/prescriptive-guidance/latest/large-migration-foundation-playbook/large-migration-foundation-playbook.pdf

**Landing file:** legal/aws-large-migration-foundation-playbook.pdf

---

Foundation playbook for AWS large migrations
AWS Prescriptive Guidance
Copyright © 2026 Amazon Web Services, Inc. and/or its affiliates. All rights reserved.

AWS Prescriptive Guidance: Foundation playbook for AWS large
migrations
Copyright © 2026 Amazon Web Services, Inc. and/or its affiliates. All rights reserved.
Amazon's trademarks and trade dress may not be used in connection with any product or service
that is not Amazon's, in any manner that is likely to cause confusion among customers, or in any
manner that disparages or discredits Amazon. All other trademarks not owned by Amazon are
the property of their respective owners, who may or may not be affiliated with, connected to, or
sponsored by Amazon.

Table of Contents
iii

Foundation playbook for AWS large migrations
Wally Lu, Chris Baker, Dwayne Bordelon, Dev Kar, Phani Lingamallu, Tuhin Mukherjee, and Senay
Swinney, Amazon Web Services
A large migration project is built upon its people foundation and platform foundation. Properly
preparing these foundations is critical to the success of the project. Platform refers to the
technology decisions you make, such as infrastructure, operations, and security. People refers to the
teams and individuals who contribute to the project, from beginning to end.
In this playbook, you build the foundation workstream. Because this workstream is intended to
prepare the platform and people before you begin migrating applications, you start and complete
this workstream within the first stage of a large migration, initialization. For more information
about core and supporting workstreams, see Workstreams in a large migration in the Foundation
playbook for AWS large migrations.
The purpose of this playbook is to prepare the platform foundation and people foundation to
support a large-scale migration effort. Both of these foundations are critical to the success of large
migrations. This guide consists of the following sections:
• People foundation – In this section, you define the workstreams in your large migration project
and build a responsible, accountable, consulted, informed (RACI) matrix for each high-level
task. It also includes recommendations for establishing a Cloud Enablement Engine (CEE). This
section also contains training resources and helps you build a training dashboard for your large
migration.
• Platform foundation – In this section, you review technology considerations for the on-premises
and AWS Cloud environments, such as infrastructure, operations, security. You make key
decisions in these categories, which you record as migration principles.
Guidance for large migrations
Migrating 300 or more servers is considered a large migration. The people, process, and technology
challenges of a large migration project are typically new to most enterprises. This document is
part of an AWS Prescriptive Guidance series about large migrations to the AWS Cloud. This series is
designed to help you apply the correct strategy and best practices from the outset, to streamline
your journey to the cloud.
Guidance for large migrations 1

The following figure shows the other documents in this series. Review the strategy first, then the
guides, and then proceed to the playbooks. To access the complete series, see Large migrations to
the AWS Cloud.
About the tools and templates
In this playbook, you create the following tools, which you use to prepare the platform and people:
• Migration principles
• RACI matrices
• Dashboard for training
We recommend using the attached templates and then customizing them for your portfolio,
processes, and environment. The instructions in this playbook tell you when and how to customize
each of these templates. This playbook includes the following templates:
• Dashboard template for training – This dashboard template helps you build a training plan for
each workstream and track each individual's progress toward completing the required training.
• Data replication calculator – This workbook helps you estimate the amount of time needed to
complete data replication.
• Migration principles template – This template helps you record the key infrastructure,
operations, and security decisions that you need to make when preparing your platform.
• RACI template – This template helps you build a high-level and detailed RACI matrices that
outline the roles and responsibilities of your large migration project.
About the tools and templates 2

Attachments
To access additional content that is associated with this document, download and unzip the
following file:
attachment.zip
Attachments 3

People foundation
This section focuses on preparing the people and processes involved in your project for the
activities in each stage of the large migration. To build the people foundation, you need to define
the workstreams in your project, organize individuals into functional teams, confirm that that roles
and responsibilities are well understood, and complete training.
This section consists of the following topics:
• Workstreams in a large migration
• Roles
• Team organization and composition
• Training and skills required for large migrations
Workstreams in a large migration
Large migration projects typically consist of multiple workstreams, and each workstream has a
clear scope of tasks. Each workstream is independent but also supports the other workstreams
to accomplish the same goal – migrate servers at scale. This section discusses the standard core
workstreams for large migrations as well as common supporting workstreams.
Core workstreams
Core workstreams are needed for every large migration, regardless of company size or segment.
The following is an overview of the primary roles of each core workstream:
• Foundation workstream – This workstream is focused on preparing the people and platform for
the large migration.
• Project governance workstream – This workstream manages the overall migration project,
facilitates communication, and focuses on completing the project within budget and on time.
• Portfolio workstream – The teams in this workstream collect metadata to support the
migration, prioritize applications, and perform wave planning.
• Migration workstream – Using the wave plan and collected metadata from the portfolio
workstream, the teams in this workstream migrate and cutover the applications and servers.
Workstreams in a large migration 4

Information and activities flow from upstream to downstream in a large migration, as shown in
the following table. Information comes from the upstream foundation and project governance
workstreams, through the portfolio workstream, and into the migration workstream. For example,
the portfolio workstream is upstream of the migration workstream because the portfolio
workstream prepares the metadata and wave plan that the migration workstream uses to migrate
and cutover the applications and servers. Adding additional, supporting workstreams in your
large migration project might change the flow of information and activities through the core
workstreams.
Important
You need to assign a project-level technical leader for your large migration project.
This role is not part of any individual workstream but has the total responsibility of all
workstreams. This individual oversees all workstreams to make sure they work together and
stay focused on the project-level goals.
Core workstream name Upstream workstreams Downstream workstreams
Foundation — Migration
Portfolio
Project governance — Migration
Portfolio
Portfolio Foundation Migration
Project governance
Migration Foundation —
Project governance
Portfolio
Core workstreams 5

The following are the primary functions of each core workstream in the phases of a large
migration. The playbooks in this document series are structured to help you navigate the tasks for
each workstream in the appropriate phase and stage.
|     |     | Foundation | Project  | Portfolio | Migration |
| --- | --- | ---------- | -------- | --------- | --------- |
governance
| Phase 1: Assess |     | —   | —   | —   | —   |
| --------------- | --- | --- | --- | --- | --- |
Phase 2: Mobilize You might  You might  You might  You might
|     |     | have          | have          | have           | have          |
| --- | --- | ------------- | ------------- | -------------- | ------------- |
|     |     | designed      | designed      | completed      | completed     |
|     |     | the AWS       | a project     | an initial     | a pilot       |
|     |     | landing zone  | managemen     | portfolio      | migration in  |
|     |     | or workstrea  | t process in  | assessment     | this phase.   |
|     |     | ms in this    | this phase.   | and discovery  |               |
|     |     | phase.        |               | in this phase. |               |

| Phase 3:  | Stage 1:  | Establish  | Develop  | Develop  | Develop  |
| --------- | --------- | ---------- | -------- | -------- | -------- |
Migrate Initialize workstreams  project  metadata,  migration
|     |     | and review    | managemen    | wave            | runbooks. |
| --- | --- | ------------- | ------------ | --------------- | --------- |
|     |     | landing       | t processes  | planning, and   |           |
|     |     | zone design.  | and          | application     |           |
|     |     | Prepare for   | communica    | prioritization  |           |
|     |     | change.       | tion and     | runbooks.       |           |
meeting
Formalize
plans.
migration
principles,
teams, and
RACI matrix.
Complete
training.
|     | Stage 2:  | —   | Facilitate and  | Collect       | Migrate      |
| --- | --------- | --- | --------------- | ------------- | ------------ |
|     | Implement |     | communica       | metadata for  | and cutover  |
Core workstreams 6

te the status the migration waves, and
of waves and , prioritiz iterate the
the overall e applicati runbooks
migration ons, and plan to increase
project. waves. velocity.
The following sections describe each of the core workstreams in more detail, including common
tasks for each workstream, the expected outcome of each workstream, and the skills required
in each workstream. It is not required that each individual in the workstream have every skill. A
workstream consists of one more cross-functional teams, so each person contributes different
skills. But as a team, they should have all the skills listed.
Foundation workstream
The foundation workstream consists of two categories: platform foundation and people
foundation. Building the platform foundation helps confirm that both the AWS and the on-
premises infrastructures are ready to support the large migration. Building a people foundation
prepares and trains the project teams for the migration and sets up all workstreams.
Common tasks • Build and validate the AWS landing zone
• Prepare the on-premises infrastructure
to support the migration, such as making
networking or firewall changes, permissions
changes, or Active Directory changes
• Set up the project core workstreams and
supporting workstreams
• Set up the training plan for the team
• Build the RACI matrices with project
managers
Expected outcome • Source and target platforms are prepared
for the large migration.
• People are ready to support the large
migration
• All workstreams are set up.
Core workstreams 7

Required skills • Deep knowledge of on-premises data
centers, including servers, storage, and
networking
• Experience with the AWS Cloud and
knowledge of AWS compute services,
including landing zones and AWS Control
Tower
• Experience with large data center or cloud
migrations
• Experience building a training plan
• Experience building a cross-functional team
Project governance workstream
The project governance workstream manages the overall migration project and is responsible for
delivering the project on budget and on time.
Common tasks • Kick off the project
• Set up the governance model
• Set up the Cloud Enablement Engine (CEE)
• Set up the communication plan
• Set up the escalation plan
• Build RACI matrices
• Set up the project management framework
• Set up status reporting and project tracking
• Set up risk and issue tracking
• Continuously manage the project by using
the predefined processes and tools
Expected outcome • Ensure that every workstream is able to
complete their tasks on time
• Ensure collaboration across workstreams
Core workstreams 8

• Ensure that the project achieves the defined
business outcomes
• Deliver the project on budget and on time
Required skills • Experience with common project
management methodologies, such as
waterfall, agile, Kanban, and scrum
• Experience with common project
management tools, such as Jira, Microsoft
Project, and Confluence
• Experience with large migration project
management
Portfolio workstream
The portfolio workstream manages all of the migration discovery activities, collects metadata,
prioritizes applications, and creates a wave plan to support the migration workstream.
Common tasks • Validate the migration strategies and
patterns
• Complete portfolio discovery by using
discovery tools and configuration
management database (CMDB)
• Define the required metadata, collection
processes, and storage location
• Prioritize applications
• Perform application deep dives, including
dependency analysis and target state design
• Perform wave planning
• Collect migration metadata
Expected outcome • Continuously create wave plans and collect
migration metadata, and then hand off to
the migration workstream
Core workstreams 9

Required skills • Deep knowledge of on-premises CMDB, data
repositories, and content management tools
• Experience with common portfolio discovery
tools, such as Flexera One and modelizeIT
• Experience with portfolio assessment and
application prioritization
• Experience with application deep dives and
application owner interviews
• Experience with application designs for the
AWS Cloud
• Experience with wave planning for large
migrations
• Experience with automation, including shell
scripting, Python, and Microsoft PowerShell
Migration workstream
The migration workstream manages the migration implementation-related activities, including
data replication and cutover. Because the migration team performs the migration and cutover, a
common misconception is that the migration workstream does everything in a large migration
project. However, the migration workstream is dependent on other workstreams to build the
foundation and provide portfolio data to support the migration.
Tip
The migration workstream is generally the largest workstream in a large migration project.
Depending on the size and strategy of your project, consider dividing this workstream into
multiple sub-workstreams. For example:
• Rehost migration workstream
• Replatform migration workstream
• Refactor migration workstream
• Relocate migration workstream
Core workstreams 10

• Migration workstream for a specialized workload, such as SAP or databases
Common tasks • Validate the migration wave plans
• Build the migration runbooks
• Use AWS migration services to transfer data,
such as AWS Application Migration Service
(AWS MGN), AWS Database Migration
Service (AWS DMS), and AWS DataSync
• Install and uninstall software on source
and target servers as needed support the
migration
• Write automation scripts to automate
migration activities
• Launch target AWS environments, such as
Amazon Elastic Compute Cloud (Amazon
EC2) instances, for testing or cutover
• Work with change management team for
changes and cutovers
• Perform migration cutover
• Support application owners during applicati
on testing
• If cutover fails, help roll back the server
Expected outcome • Complete migration cutover and application
go-live in target AWS accounts
Required skills • Deep knowledge of on-premises data
centers, including servers, storage, and
networking
• Experience with the AWS Cloud and
knowledge of AWS compute services,
including landing zone and AWS Control
Tower
Core workstreams 11

• Experience with AWS migration services,
including Application Migration Service,
AWS DMS, DataSync, and AWS Snow Family
• Experience with large data center or cloud
migrations and cutovers
• Experience with automation, including shell
scripting, Python, and Microsoft PowerShell
Supporting workstreams
Supporting workstreams support the core workstreams. These workstreams are optional, and you
might decide to use them based on your use case and the current stage of your migration. The
following are some common supporting workstreams that you might want to include in your large
migration project:
• Security and compliance workstream – This workstream defines and builds the security
standards for the target AWS infrastructure and supports migrations.
• Cloud operations (Cloud Ops) workstream – This workstream manages applications after
cutover, when the hypercare period is complete.
• Application testing workstream – This workstream performs application testing before and
during the cutover.
• Specializedworkload migration workstream – This workstream supports migrations for specific,
specialized workloads, such as SAP or databases.
You might not need a dedicated workstream for these activities. It is common to have an individual
or set of individuals be responsible for these activities and then embed those individuals in one
of the core workstreams. For example, every large migration requires a security and compliance
person because you need to make sure your target infrastructure is secure and compliant. However,
security and compliance assessments and decisions are typically performed early in the migration,
most commonly in the mobilize phase. If you have already completed this, you do not need a
dedicated workstream to repeat the same tasks. However, it is recommended that you embed a
security and compliance person in the migration workstream in order to support the migration
activities.
Supporting workstreams 12

When you add supporting workstreams, it modifies the flow of information and activities through
the core workstreams. The following table is an example of how adding workstreams changes this
flow. Your supporting workstreams might differ from the examples in this table.
| Workstream name | Type | Upstream workstrea  | Downstream          |
| --------------- | ---- | ------------------- | ------------------- |
|                 |      | ms                  | workstreams         |
| Migration       | Core | Foundation          | Application testing |
|                 |      | Project governance  | Cloud operations    |
|                 |      | Portfolio           |                     |
Security and
compliance
| Portfolio | Core | Foundation | Migration |
| --------- | ---- | ---------- | --------- |
Project governance
Security and
compliance
| Project governance | Core | —   | Migration |
| ------------------ | ---- | --- | --------- |
Portfolio
| Foundation | Core | —   | Migration |
| ---------- | ---- | --- | --------- |
Portfolio
Cloud operations
| Security and  | Supporting | —   | Migration |
| ------------- | ---------- | --- | --------- |
compliance
Portfolio
| Cloud operations | Supporting | Migration | —   |
| ---------------- | ---------- | --------- | --- |
Application testing
Foundation
Supporting workstreams 13

Application testing Supporting Migration Cloud operations
Specialized workload Supporting Foundation Application testing
migration
Project governance Cloud operations
Portfolio
Security and
compliance
Security and compliance workstream
The security and compliance workstream defines and builds the security standards for AWS
infrastructure and supports migrations. Using the standards established by this workstream,
application owners typically define the security and compliance requirements for each application.
You might decide to have the security and compliance workstream review and approve the
requirements for some or all applications.
Common tasks • Define the security requirements for the
AWS landing zone, such as centralized
logging, encryption, AWS Identity and
Access Management (IAM) policies, and
Active Directory integration
• Define the compliance requirements, such
as HIPAA, personally identifiable informati
on (PII), Service Organization Control
(SOC), and Federal Risk and Authorization
Management Program (FedRAMP)
• Define the security requirements for the
migration, such as firewall, security group,
and IAM role requirements
Supporting workstreams 14

• Manage changes for security-related tasks,
such as changes to firewalls, security groups,
and permissions
Expected outcome • Complete migration cutover and application
go-live in target AWS accounts
Required skills • Deep knowledge of on-premises data
centers, including servers, storage, and
networking
• Deep knowledge of the specialized workload
in scope
• Experience with the AWS Cloud and
knowledge of AWS compute services,
including landing zones and AWS Control
Tower
• Experience with AWS migration tools,
including Application Migration Service,
AWS DMS, DataSync, and AWS Snow Family
• Experience with large data center or cloud
migrations and cutovers
Cloud operations workstream
The cloud operations workstream supports the applications after migration cutover. Sometimes
cloud operations is in a separate workstream with dedicated resources, but most commonly,
these resources come from existing IT operations teams. In that case, no dedicated workstream is
required.
Common tasks • Monitor and back up the migrated servers
and applications
• Manage the business-as-usual service
requests from the application teams, such as
Supporting workstreams 15

increasing the disk size or changing instance
types
• Resolve any application issues and outages
as needed
• Manage the patching policies and schedules
• Manage the maintenance tasks and requests
Expected outcome • Migrated servers and applications are
running smoothly on AWS
• Respond to service requests from users and
resolve any issues
Required skills • Deep understanding of how the on-premises
data center currently operates
• Experience with common AWS operations
services, such as Amazon CloudWatch, AWS
Config, AWS CloudTrail, AWS Backup, AWS
Support
• Experience with troubleshooting, and
understands the SLA
• Experience with supporting large migrations
Application testing workstream
The application testing workstream supports application testing before and during the cutover.
This workstream is more common in projects where system integrators manage the data centers
because the application owners don't have sufficient knowledge to perform the application tests.
In most cases, the application owner performs these activities, and a dedicated application testing
workstream is not required.
Common tasks • Perform application testing before the
cutover
Supporting workstreams 16

• Perform application testing during the
cutover
• Make application changes as needed to
work in the new environment
• Make a go or no-go decision for applications
based on testing results during cutover
Expected outcome • Complete application testing on time during
cutover
• Make application changes as needed to
support the target environment
Required skills • Deep knowledge of the applications and
how they operate on premises
• Experience with the AWS Cloud, especially
the target AWS services
• Experience with large migrations
Migration workstream for a specialized workload
You can create a migration workstream that is dedicated to specialized workloads. Generally, you
can build standard migration patterns and runbooks to migrate servers and applications at scale,
and these are managed by the migration workstream. However, in some cases, certain applications
require special migration processes. For example, you might need a special process in order to
migrate Hadoop workloads, SAP HANA databases, or mission-critical applications that cannot
tolerate the standard amount of down time. For more information about specialized workloads,
see MAP specialized workloads at AWS Migration Acceleration Program.
Common tasks • Validate the migration wave plans
• Build migration runbooks
• Use migration tools or native application
tools to transfer data
Supporting workstreams 17

• Launch target AWS environments, such as
EC2 instances, for testing or cutover
• Work with the change management team
for changes and cutovers
• Perform migration cutover
• Support application owners during applicati
on testing
• If cutover fails, roll back the application or
server
Expected outcome • Complete migration cutover and application
go-live in target AWS accounts
Required skills • Deep knowledge of on-premises data
centers, including servers, storage, and
networking
• Deep knowledge of the specialized workload
in scope
• Experience with the AWS Cloud and
knowledge of AWS compute services,
including landing zones and AWS Control
Tower
• Experience with AWS migration tools,
including Application Migration Service,
AWS DMS, DataSync, and AWS Snow Family
• Experience with large data center or cloud
migrations and cutovers
• Experience with migrating the specialized
workload
Supporting workstreams 18

Roles
The following are the common roles in a large migration project. Because these roles might go
by another title in your organization, a brief description of each role is provided. If a role is not
available in your organization, you might investigate whether other resources in your organization
can perform this role or seek outside support in the form of a consultant.
| General role | Alternate titles | Workstreams | Characteristics |
| ------------ | ---------------- | ----------- | --------------- |
Application owner Application architect  All Should have in-depth
|     | , application project   |     | knowledge of their  |
| --- | ----------------------- | --- | ------------------- |
|     | coordinator, applicati  |     | applications        |
on project manager
Automation engineer DevOps engineer Migration, portfolio Should have
experience and in-
depth knowledge
of how to build
automation scripts
Cloud architect Cloud engineer,  Migration, foundatio  Should have
|     | migration consultan    | n, portfolio | experience and in- |
| --- | ---------------------- | ------------ | ------------------ |
|     | t, architecture lead,  |              | depth knowledge    |
|     | cloud infrastructure   |              | of how to design   |
|     | architect              |              | the AWS Cloud      |
infrastructure, how
to perform portfolio
assessment and wave
planning, and how to
use migration tools to
migrate workloads to
the AWS Cloud
Cloud operations lead Migration technical  Cloud operations Should have
|     | support, cloud        |     | experience and in- |
| --- | --------------------- | --- | ------------------ |
|     | operations workstrea  |     | depth knowledge    |
|     | m lead                |     | of how to operate  |
Roles 19

workloads in the AWS
Cloud
Communication lead Business unit liaison Project governance Should have relations
hip to the business
unit and manage all
communications
| Executive leadership | Project sponsor | All | Should have clear  |
| -------------------- | --------------- | --- | ------------------ |
vision of the
migration project
| Migration lead | Migration support  | Migration | Should have          |
| -------------- | ------------------ | --------- | -------------------- |
|                | lead, migration    |           | experience and in-   |
|                | technical product  |           | depth knowledge      |
|                | owner, migration   |           | of all migration     |
|                | workstream lead    |           | patterns and how to  |
use migration tools to
migrate workloads to
the AWS Cloud
| Portfolio lead | Discovery lead,       | Portfolio | Should have        |
| -------------- | --------------------- | --------- | ------------------ |
|                | wave planning lead,   |           | experience and in- |
|                | portfolio workstream  |           | depth knowledge    |
|                | lead                  |           | of how to perform  |
discovery, portfolio
assessment, and wave
planning
Project manager Program manager,  Project governance Should have
|     | project coordinat       |     | experience and in-   |
| --- | ----------------------- | --- | -------------------- |
|     | or, Scrum master,       |     | depth knowledge      |
|     | project delivery lead,  |     | of how to manage     |
|     | program delivery        |     | a large migration    |
|     | lead, large migration   |     | project and how to   |
|     | manager                 |     | use agile methodolo  |
gies
Roles 20

| Project technical lead | Engineering lead,      | All | Should have        |
| ---------------------- | ---------------------- | --- | ------------------ |
|                        | technical lead, chief  |     | experience and in- |
|                        | architect              |     | depth knowledge    |
of all workstreams
and how to deliver
a migration project
from start to finish.
Responsible for
the entire project
outcome across all
workstreams
| System integrator | Global system  | All | Varies, depending  |
| ----------------- | -------------- | --- | ------------------ |
|                   | integrator     |     | on the workstrea   |
m. Should have in-
depth knowledge
of workstream-level
activities, such as
portfolio assessment
or server migration
Testing lead Testing specialist,  Application testing Should have
|     | application testing  |     | experience and in- |
| --- | -------------------- | --- | ------------------ |
|     | workstream lead      |     | depth knowledge    |
of how to perform
application testing in
the AWS Cloud

Team organization and composition
This section includes the following topics:
• Best practices for team organization and composition
• Creating RACI matrices
Team organization and composition 21

• Cloud Enablement Engine (CEE)
Best practices for team organization and composition
Team composition in a large migration varies by organization and changes over the course of the
project. The following are best practices that are common for all large migration projects:
• Identify a single-threaded technical leader at the project level and avoid silos – Large
migration projects often have multiple workstreams and teams, each team has different tasks
and expected outcomes. A single-threaded leader at the project level is important because
this leader makes sure all workstreams work together and stay connected. This helps prevent
silos and boundaries. For example, the portfolio workstream needs to continuously send the
migration metadata to the migration workstream to support the migration activities. Without
a complete understanding of the required migration metadata, the output of the portfolio
workstream might not work as an input for the migration workstream. A single-threaded
leader helps coordinate the inputs and outputs of each workstream to help the migration run
efficiently.
• Align all workstream-level outcomes with the project-level business outcomes– Project-level
business outcomes should be communicated to all workstream leaders before the migration
starts. Each workstream leader must understand the role of their workstream and design their
processes to support the project-level business outcomes. For example, if a project-level business
outcome is exiting a data center in the next 12 months and speed is the most important factor,
the workstream leaders should do the following:
• All workstreams should prioritize rehost migrations, reduce the number of manual tasks, and
add automation to improve the velocity.
• The portfolio workstream should define standardized patterns and limit customizable patterns
to reduce the amount of time required to design the target environment.
• Design workstreams based on project scope and stage – Every migration project is different,
and one size does not fit all. We recommend having four core workstreams for all large migration
projects: migration workstream, portfolio workstream, project governance workstream, and
foundation workstream. You might decide to create additional, supporting workstreams
depending on your use case. For more information about workstreams, see Workstreams in a
large migration. For example, if you have not yet designed the security guardrails in the mobilize
phase, you need to create a security and compliance workstream that can define the security
and compliance requirements before you start migrating. For more information about building
Best practices for team organization and composition 22

the security guardrails in the mobilize phase, see Security, risk and compliance in Mobilize your
organization to accelerate large-scale migrations.
• Get the application team involved before the migration – A large migration is never just
an IT infrastructure project – it changes the operating model for your business. Involving
the application team early and embedding the application owners into your large migration
workstreams is critical to the success of large migration project. For example, during portfolio
assessment, schedule your meetings early with application owners so that they can participate in
the deep dive and help design their application's target state on AWS.
• Determine the team size based on workstreams and business outcomes – Your expected
business outcomes and migration strategies drive the size of each team, which is composed of
smaller units called pods. In each workstream, you define teams for each migration strategy and
then separate those teams into pods. For example, if rehost is your primary migration strategy,
then you should have a rehost migration team that is composed of pods that contain 3­–5
people. When operating at peak velocity, a pod of 4­–5 people on a migration team can typically
rehost up to 50 servers per week. This is approximately 200 servers per month or 2,500 servers
per year. If your target is to rehost 100 servers per week, you should create two pods of 4–-
5 people within the rehost migration team. If you are targeting less than 50 servers per week,
you can reduce the size of the migration pod to 3 people. Replatform migrations usually cost
more than rehost, and the same size pod can migrate up to 20 servers per week. The portfolio
workstream is usually half the size of the migration workstream. You create additional teams and
pods in each workstream to support each migration strategy. These recommendations assume
that your migration resources are skilled and do not require significant training. The following
table is an example of how you would divide the migration and portfolio workstreams into teams
and pods for the rehost and replatform migration strategies. The following example assumes
that you need to migrate 120 servers per week (100 rehost + 20 replatform) or 6,000 servers
per year. This example is the maximum velocity. We recommend that you plan for additional
resources in order to help prevent delays.
Workstream Team Pod Resources
Migration workstrea Rehost migration Rehost migration 4­–5 people
m team pod 1
Rehost migration 4­–5 people
pod 2
Best practices for team organization and composition 23

Replatform Replatform 4–5 people
migration team migration pod
Portfolio workstream Portfolio team Portfolio pod 1 3–4 people
Portfolio pod 2 3–4 people
• Build a governance model in the early stage – A large migration typically involves many people,
including people from your own company, third-party software vendors, system integrators,
or external consultants. Your project might include representatives from AWS, such as your
account team, support engineers, or experts from AWS Professional Services. Your delivery
model varies depending on your project scope and who you work with to deliver the project.
For example, your project might include AWS or a system integrator, or you might include
both. It is important to build a governance model early and create a RACI matrix that clearly
defines the roles and responsibilities. As a recommendation, we also recommend creating a
Cloud Enablement Engine (CEE), also known as Cloud Center of Excellence, in your organization
and including representation from all parties. The key purpose of the CEE is to transform the
organization from an on-premises operating model to a cloud-operating model. This centralized
team is critical to the success of a large migration because it manages relationships, makes key
decisions, and handles escalations throughout the project. The CEE is discussed in more detail
later in this guide.
Creating RACI matrices
A large migration project typically involves a lot of people, so building a governance model is
important to manage the project. One of the key components of a governance model is a RACI
matrix, which is used to define the roles and responsibilities for all parties involved in the large
migration. The name RACI matrix is derived from the four responsibility types defined in the matrix:
• Responsible (R) – This role is responsible for performing the work to complete the task.
• Accountable (A) – This role is held accountable for making sure the task is completed. This role is
also responsible for ensuring the prerequisites are met and delegating the task to those who are
responsible.
• Consulted (C) – This role should be consulted for opinions or expertise on the task. Depending
on the task, this responsibility type might not be required.
• Informed (I) – This role should be kept up to date on the progress of the task and notified when
the task is completed.
Creating RACI matrices 24

Because of the complexity of a large migration, we do not recommend using a single RACI matrix
to document every task in the large migration. A multi-layer RACI matrix is a much more accessible
approach. You start by building a high-level RACI matrix, and then you add more details to each
section to build a detailed matrix. Building a detailed RACI matrix is not a one-off approach. You
need to build new matrices or add more details to the existing ones as you progress through the
portfolio and discover more migration strategies and patterns.
You can use the attached RACI template (Microsoft Excel format) as a starting point for building
your own high-level and detailed RACI matrices. This template includes two examples of detailed
RACI matrices, one for a rehost migration and another for a replatform migration. The tasks in
these examples are included for sample purposes only, and you should customize these examples
based on your use case.
Build a high-level RACI matrix
Before you start building a high-level RACI matrix, you need to have the following information
ready:
• Who are the high-level parties involved in this migration? Identify any partners or consultants
that will be involved in this project, such as AWS Professional services or system integrators.
Consider whether any part of your current IT infrastructure is managed by an external partner.
The following are examples of high-level parties:
• Your organization
• AWS Professional Services
• System integrators
• What are the workstreams in your migration? For more information, see Workstreams in a large
migration. At a minimum, you should have the four core workstreams, and you can add support
workstreams as needed for your project.
• What are the high-level tasks in your migration? Create a list of the high-level tasks in your
migration. The following are examples of high-level tasks:
• Build an AWS landing zone
• Perform portfolio assessment and collect migration metadata
• Perform a rehost, replatform, or relocate migration
• Perform application testing and cutover
• Perform project management and governance tasks
Creating RACI matrices 25

Do the following to build your high-level RACI matrix:
1. Open the attached RACI template (Microsoft Excel format).
2. On the High-level RACI tab, in the first row, enter your organization name and any partners that
you identified.
3. In the first column, enter the high-level tasks and workstreams that you identified.
4. In the matrix, determine which parties are responsible for each task as follows:
• If a party is responsible for completing the task, enter an R.
• If a party is accountable for completing the task, enter an A.
• If a party should be consulted about the task, enter a C.
• If a party should be informed about the task, enter an I.
The following table is an example of a high-level RACI matrix.
Task Your organizat Partner A Partner B Partner C
ion
Build an AWS R/C A I I
landing zone
Perform R/C A I I
portfolio
assessment and
wave planning
Perform rehost C C R/A I
migration
activities
Perform C C I R/A
replatform
migration
activities
Creating RACI matrices 26

Project R/C A I I
management
and governance
Application C R/A C C
changes and
testing
Cloud operation I C R/A I
s
Build the detailed RACI matrices
After creating the high-level RACI matrix, the next step is to create a detailed RACI for each high-
level task and further refine the tasks, parties, and ownership. Before you start building detailed
matrices, you need to have the following information ready:
• What are the detailed tasks in your migration? After you have prepared the runbooks and
task lists for your large migration project, the processes and details in these runbooks form the
detailed layer of your RACI matrix. For example, for a rehost migration, detailed tasks might
include installing a replication agent, verifying replication, and launching test instances for boot-
up testing. If you haven't done so already, follow the instructions in the following playbooks to
create these documents:
• Portfolio playbook for AWS large migrations
• Migration playbook for AWS large migrations
• What smaller teams make up each workstream and each high-level party? For example, teams
in your organization might include an application team, infrastructure team, operations team,
networking team, or a project management office.
Do the following to build a detailed RACI matrix:
1. Open your high-level RACI matrix.
2. Create a copy of the Detailed RACI (template) spreadsheet.
3. Name the copied spreadsheet for a high-level task that you identified in Build a high-level RACI
matrix.
4. In the first row, enter the names of the teams involved in this high-level task.
Creating RACI matrices 27

5. In the first column, enter the detailed tasks that you identified for this high-level task. You can
group the detailed tasks into logical sequential groups, which helps readers navigate the matrix.
6. In the matrix, determine which teams are responsible for each task as follows:
• If a team is responsible for completing the task, enter an R.
• If a team is accountable for the task, enter an A.
• If a team should be consulted about the task, enter a C.
• If a team should be informed about the task, enter an I.
7. For each detailed task, confirm that only one team is responsible and only one team is
accountable. If multiple teams are responsible or accountable, this can indicate that the task is
not clearly defined or doesn't have clear ownership.
8. Share the detailed RACI matrix with the identified teams and confirm that all teams are familiar
with their roles and responsibilities.
9. Repeat this process for each high-level task that you identified in Build a high-level RACI matrix.
For examples of detailed RACI matrices, see the Rehost RACI and Replatform RACI spreadsheets in
the attached RACI template.
Cloud Enablement Engine (CEE)
Best practices for using a CEE
The purpose of a CEE is transforming an IT organization from an on-premises operating model
to a cloud-operating model, and it is responsible for guiding the organization through the
organizational and cultural changes. As a best practice, it is recommended that you establish a
CEE for your large migration. The well-defined foundational processes and guard rails of a CEE
can help you achieve the scale and velocity required for large migrations. For information about
setting up a CEE, see Cloud Enablement Engine: A Practical Guide. The following are additional
recommendations and best practices for establishing a CEE for a large migration project:
• The CEE team should be comprised of cross-functional leaders with the following qualities:
• Have deep institutional knowledge
• Have strong, long-standing internal relationships
• Have a vested interest in the progress and success in the large migration
• Are curious and want to learn
• Are primarily or solely focused on the migration
Cloud Enablement Engine (CEE) 28

• The CEE team should be a mix of people who have worked together previously and newcomers
who can provide fresh insights.
• The CEE team should have strong executive support and alignment on the migration objectives.
• Make sure the goals of the CEE team are specific to the large migration.
• Conduct regular, open meetings that provide opportunities for questions and answers,
demonstrate cloud services and architectures, and share updates on successful migrations and
other wins.
• The CEE team should be empowered to make critical decisions about the large migration project.
Typical CEE roles and responsibilities for large migrations
The following table provides roles in a large-migration CEE team, and it describes the typical tasks
and responsibilities for each role. The actual composition of your team and their responsibilities
can vary based your use case, scope, and business objective.
Roles Tasks and responsibilities
Executive sponsor • Managing escalations
• Aligning the organization tightly around the
objectives and criticality of the migration.
• Serving as the voice of authority
Enterprise architect or project-level technical • Identifying and documenting the reference
lead architecture for known workload types
• Designing and building migration processes
for the entire project, across all workstreams
• Serving as the single-threaded technical
leader who makes sure all workstreams are
collaborating and working to deliver the
same business-level objectives
• Strong institutional knowledge of major
applications and common architectures
Cloud Enablement Engine (CEE) 29

Project management office lead • Managing timelines, onboarding, training,
documentation, reporting, communication,
and resource governance
• Managing resourcing and training
• Managing migration-related town halls
Migration lead • Designing migration processes and tools
• Designing migration strategies and
automation
• Overseeing migration cutovers and
achieving the target velocity
Portfolio lead • Designing portfolio assessment and wave
planning processes and tools
• Designing portfolio discovery and data
collection processes
• Overseeing the continuous supply of
migration metadata and wave plans to the
migration workstream
Cloud operations lead • Designing the operating model for running
workloads on AWS
• Designing strategies for monitoring,
incident response, tagging, business
continuity, and disaster recovery strategies
Application team leader • Managing the relationship with individual
application owners
• Managing migration planning and cutovers
for their applications
• Managing application changes, testing, and
approvals
Cloud Enablement Engine (CEE) 30

Network and infrastructure lead • Designing the AWS landing zone for target
accounts
• Designing network connectivity and
infrastructure
• Designing and deploying security groups
• Managing infrastructure and networking
changes to support the large migration
Licensing lead • Identifying all commercial off-the-shelf
(COTS) and enterprise applications and
working with the migration team and
application team to plan migration strategie
s around licensing
Security and compliance lead • Designing authentication and authorization
for the large migration, including Active
Directory, single sign-on, and IAM policies
• Designing network security, including on-
premises firewalls, and managing vulnerabi
lities
• Designing compliance requirements for in-
scope workloads
Training and skills required for large migrations
The people involved in the large migration are a critical resource, and it is equally as important to
prepare them for the migration as it is to prepare the landing zone or workstreams. This section is
dedicated to training the people in your project, ensuring that your teams have the skills necessary
to perform a large migration. While some skills are common and required for many roles, other
skills are more specialized and require thoughtful recruitment or training. By ensuring individuals
are properly trained for their roles before the migration starts, the workstreams can operate
efficiently, and you can quickly ramp up the migration to the target velocity.
Training is divided into levels: prerequisites, fundamentals, and advanced. Every person in your
large migration project should complete the prerequisite-level training, which reviews basic
information about the AWS Cloud and migration concepts. For fundamentals and advanced levels,
Training and skills required for large migrations 31

you use a training plan to assign a training level to each workstream. You then use a training
tracking tool to record each individual's progress toward completing the required trainings in their
workstream. It is important to note that we recommend training based on workstreams rather than
roles and job titles because roles can vary significantly between organizations.
Each of the following sections lists and describes the training resources recommended for the level:
• Large migration training – Prerequisites
• Large migration training – Fundamentals
• Large migration training – Advanced
Prerequisites
At a minimum, the resources in every workstream should have foundational understanding of
infrastructure, networking, and core AWS services, Cloud Adoption Framework (AWS CAF) and the
AWS Well-Architected Framework. The following are recommended for this training level:
• AWS Technical Essentials –This foundational training module provides an overview of AWS
services and cloud technology, such as virtual private clouds (VPCs), Amazon Elastic Compute
Cloud (Amazon EC2), Availability Zones, and AWS Regions.
• Foundational training for infrastructure, networking, and data centers – Provide foundational
training about infrastructure and networking, such as Transmission Control Protocol (TCP),
Internet Protocol (IP), Domain Name System (DNS), Dynamic Host Configuration Protocol
(DHCP), and load balancers. Provide training about data center technologies, such as the
software development lifecycle (SDLC) and IT service management (ITSM). Training requirements
in this category vary based on your environment and use case, and many training resources are
available. We recommend working with your IT department to identify technology-level training
that is appropriate for all personnel in your large migration project.
• Organizational processes – Provide training for any processes that are specific to your
organization, such as change management processes. You must understand the deadlines,
approvals, and formal documents required to make changes in your organization, such as firewall
and domain changes. Determine whether external partners or consultants need this training in
order to support your project.
• Shared Responsibility Model – If you are working with AWS Professional Services, this webpage
describes how you will share roles and responsibilities with AWS.
Prerequisites 32

• An Overview of the AWS Cloud Adoption Framework (AWS CAF) – This whitepaper helps you
understand the goals of AWS CAF, the AWS CAF perspective, and the stakeholders involved.
Fundamentals
This section provides an overview of the processes, tools, and guidelines required to successfully
complete a large migration. The following are recommended for this training level:
• How to migrate – This webpage helps you understand the three-phase migration process.
• About the migration strategies – This section of the Guide for AWS large migrations describes
each of the migration strategies and common use cases for each in a large migration project.
• Migrating to AWS: A high level introduction – This course provides an overview of the key topics
and target audience of the Migrating to AWS classroom course.
• Migrating to AWS - This course explains how to plan and migrate existing workloads to the AWS
Cloud.
• Strategy and best practices for AWS large migrations – This strategy discusses best practices for
large migrations and provides use cases from customers across various industries.
• Introduction to Database Migration – In this course, you learn how to migrate a production
database by using the AWS Database Migration Service (AWS DMS) and AWS Schema Conversion
Tool (AWS SCT).
• AWS DataSync Primer – The course helps you get started with AWS DataSync, showing you how
to move large amounts of data between on-premises storage and the AWS Cloud.
• Lift-and-Shift Application Workloads – This webpage helps you understand the basics the rehost,
or lift-and-shift, migration strategy.
• AWS Transform MGN (MGN) – A Technical Introduction – This course introduces AWS Transform
MGN.
• Application portfolio assessment strategy for AWS Cloud migration – This AWS Prescriptive
Guidance strategy helps you understand the key stages to successfully assess your application
portfolio.
• AWS Cloud Migration Factory Solution – This webpage helps you understand what AWS Cloud
Migration Factory Solution is.
• CloudEndure Migration Factory best practices (YouTube video) – This video and provides an
overview of the AWS Cloud Migration Factory Solution and shares best practices for large-
Fundamentals 33

scale migrations. It includes information about how to coordinate and automate many manual
migration processes.
Advanced training
Advanced training for large migrations dives deeper into the migration methodologies, tools, and
best practices by providing workshops and training resources for the workstreams. The following
are recommended for this training level:
• Cloud migration factory workshop – This technical workshop provides information about how to
accelerate a large migration by using automation and the migration factory model.
• Guide for AWS large migrations – This guide contains high-level information about performing a
large migration and introduces the large migration playbooks.
• Foundation playbook for AWS large migrations (this guide) – Use this playbook to train
workstreams about preparing the platform foundation and people foundation for a large
migration.
• Project governance playbook for AWS large migrations – This playbook provides step-by-
step instructions for setting up the project governance framework and providing continuous
governance throughout the migration.
• Portfolio playbook for AWS large migrations – This playbook provides step-by-step instructions
to help you build your application prioritization runbook, metadata management runbook, and
wave planning runbook.
• Migration playbook for AWS large migrations – This playbook provides step-by-step instructions
for preparing migration runbooks for each migration pattern and preparing migration task lists.
Create your training dashboard
You can use the attached Dashboard template for training (Microsoft Excel format) as a starting
point for building your own training plan and tracking tool. You use a training plan to assign a
training level to each workstream. You then use a training tracking tool to record each individual's
progress toward completing the required trainings in their workstream.
1. On the Prerequisites spreadsheet, Fundamentals spreadsheet, and Advanced spreadsheet, add
or remove workstreams as appropriate for your large migration project.
2. On the Prerequisites spreadsheet, update the training materials as needed for your use case.
Define the appropriate training for infrastructure, networking, and data centers. We recommend
Advanced training 34

working with your IT department to identify technology-level training that is appropriate for all
personnel in your large migration project. This spreadsheet should contain the training materials
that you want all members of every workstream to complete.
3. On the Fundamentals spreadsheet, update the training materials as needed for your use case,
and identify which workstreams should train on each item listed.
4. On the Advanced spreadsheet, update the training materials as needed for your use case, and
identify which workstreams should train on each item listed.
5. On the Training tracker spreadsheet, enter the name of each individual in your large migration
project and their workstream.
6. As each individual completes the required training for their workstream, mark the training as
complete.
Create your training dashboard 35

Platform foundation
This section focuses on assessing the readiness of the on-premises infrastructure, preparing the
AWS landing zone or reviewing the existing landing zone design, and identifying the migration
tools needed. You review the common infrastructure, operations, and security questions that you
should consider for building a platform. You document your answers and decisions as migration
principles. As a result, you have a solid platform to achieve the scale and velocity required for large
migrations.
This section includes the following topics:
• Landing zone considerations for a large migration
• On-premises considerations for a large migration
• Document your migration principles
Landing zone considerations for a large migration
A landing zone is a well-architected AWS environment that is scalable and secure. By establishing
standards for the landing zone, such as defining the number of accounts and designing the subnets
and security groups, you build a solid foundation. This foundation gives you the ability to enable,
provision, and operate your environment for both business agility and governance at scale while
accelerating your cloud adoption journey. For more information about landing zones and strategies
for building them, see Setting up a secure and scalable multi-account AWS environment.
In addition to the standard business, operational, security and compliance considerations for your
landing zone strategy, you must consider how to facilitate a large migration. You must design
the landing zone to support existing, on-premises workloads during the migration and after, in
cases where some workloads remain on premises. This guide provides additional landing zone
considerations that affect the migration velocity and overall migration timeline.
Typically, landing zones are designed and deployed to support new workloads in the AWS Cloud.
This is because organizations are adopting AWS before making the decision to migrate a large
number of existing applications. The benefit of this approach is that the organization gains
valuable knowledge and skills in AWS before the large migration, but it can also lead to conflicts
between the various stakeholders. Some stakeholders might want to modernize the application
during the migration because they want to take advantage of cloud-native features. However,
the common goal of a large migration is to achieve maximum migration velocity and ease the
Landing zone considerations for a large migration 36

transition by migrating as many applications as possible without modifying the workload. You then
modernize these applications after the migration is complete.
Some key factors of the landing zone that can affect your large migration program project are:
• Network bandwidth availability and management
• Account strategy for workload isolation and resource management
• Security and administrative controls for migrated workloads
This section reviews the infrastructure, operations, and security questions that you should consider
when building your AWS landing zone. It also contains recommendations for how to design and
deploy your landing zone to support a large migration project. As you answer the questions in
this section, these decisions become migration principles, which you document according to the
instructions in Document your decisions as large migration principles.
Infrastructure considerations
Have you considered? Description Actions
How much data will you The desired migration velocity After you have completed
migrate per day and per dictates the type of network the portfolio assessment,
week? connection and network determine the total amount
throughput requirements. of storage needed for all
It also can affect the wave migrated resources in the
planning selection criteria. cloud. Use this value to
calculate the amount of time
required to migrate the data
using the current network
bandwidth. You might need
to increase the bandwidth
to meet the migration
timeframes, or you might
need to use alternatives, such
as AWS Snow Family solutions
. You can use the attached
Data replication calculato
r (Microsoft Excel format)
Infrastructure considerations 37

to calculate the required
bandwidth for each migration
wave.
What is the average write The bandwidth required During portfolio assessmen
speed of the source servers in to transfer the replicated t, you need to determine
each wave? data is based on the write the average number of data
speed of the participating writes performed per by
source servers. The amount of each server. You can use
bandwidth required for server the attached Data replicati
replication is the average on calculator (Microsoft
write speed of your source Excel format) to understan
servers multiplied by the d the bandwidth required
number of servers in the for migration traffic. The
largest wave. bandwidth required for
migration traffic is in addition
to the bandwidth used for
normal business activity. After
the migration is complete,
you no longer need the
additional bandwidth to
support the migration
activities.
Infrastructure considerations 38

Could additional network If the network bandwidth Early in the project lifecycle
activities or existing infrastru also supports other business , carefully assesses and
cture limit or reduce the functions, these activitie calculate the network
replication speed? s can reduce the amount bandwidth required to
of bandwidth available for support all business activitie
replicating servers during the s. Consider the bandwidth
migration. needed for normal business
activities, server replication,
and new migration-related
activities, such as syncing on-
premises file shares with data
on AWS.
Providers might have long
lead times to increase the
network capacity, and you
might need to upgrade the
existing on-premises infrastru
cture. Consider whether any
additional upgrades would
be required as a consequen
ce of upgrading the network
infrastructure. Assessing
bandwidth requirements early
in the project provides time to
make any necessary changes.
Infrastructure considerations 39

Does your current AWS The number of servers and When the portfolio
subnet strategy meet the IP workload isolation requireme assessment has enough
addressing requirements for nts dictates the subnet information about the
migrating the on-premises strategy for your landing infrastructure inventory
workloads? zone. , assess the on-premises
network structure and
incorporate it into the landing
zone design as early as
Large migrations might
possible.
require larger subnets
than you expect. In a large
migration, you group
workloads in subnets similar
to their setup in the on-
premises infrastructure.
To simplify the migration,
larger, flatter subnet designs
are preferred initially, and
then, during modernization,
you redesign the subnets as
needed.
How many servers do you The size of the largest Review the high-level
plan to replicate and migrate migration wave affects the migration plan, and use that
in parallel? subnet requirements and AWS to design your subnet. For
service quotas. example, if you have a plan
to migrate 200 servers into
one subnet, the Classless
Inter-Domain Routing (CIDR)
range for that subnet should
have enough IP addresses to
support the target number
of servers. Also, increase the
AWS service quota for each
target account as needed.
Infrastructure considerations 40

Have you identified the  Security groups are used to  In your runbook for applicati
security group strategies for  manage the inbound and  on prioritization, review the
your migration resources? outbound traffic for AWS  migration strategies, and then
|     | resources. It is important to   | design the security groups    |
| --- | ------------------------------- | ----------------------------- |
|     | design security groups early    | based on the migration        |
|     | in order to avoid delaying the  | strategies. For example, if   |
|     | migration.                      | the migration strategy is to  |
rehost most of the workloads,
consider a temporary, generic
security group that supports
migration cutover instead of
refactoring the network and
applying application-specific
security groups.
Are there load balancers in  Typically, when migrating  Assessment of load balancers
| use? | servers in an environment       | needs to start early in the  |
| ---- | ------------------------------- | ---------------------------- |
|      | with load balancers, you need   | discovery phase in order     |
|      | to assess the configuration of  | to account for any custom    |
|      | the load balancer and then      | configurations. In most      |
|      | migrate the load balancer.      | environments, load balancer  |
|      | Migration options for the       | configurations are fairly    |
|      | load balancer include using     | standard, but some might     |
|      | Elastic Load Balancing (ELB)    | have complex logic that      |
|      | or a partner appliance-based    | determines whether you can   |
|      | solution.                       | migrate to ELB or a partner  |
appliance-based solution.
Infrastructure considerations 41

Do any servers need to retain The safest and easiest way Keeping source IP addresses
their source IP address? to migrate servers to the affects how you form move
cloud is to allocate new IP groups when wave planning.
addresses to the migrated The most common approach
instances. In some situation is to migrate a whole subnet
s, you might need to keep to AWS in a single move
the same IP address as the group because this makes
source server. For example, a routing and switching
legacy application might have straight-forward at the
a hardcoded IP address that network level.
no one knows how to change.
The following are key actions
for keeping IP addresses:
• Carefully assess cross‑sub
net communications
between servers.
• Decide how you will switch
routing of IP addresses for
migrated servers. Common
options include switching a
whole subnet or deploying
a network technology that
manages static IP routing
on a server-by-server basis.
Infrastructure considerations 42

How much latency is  It is common to start the  If you are using a high or
acceptable between the  migration with VPN links  variable latency connection
source and AWS? because they can be set up  type, review each applicati
|     | quickly and then transitio    | on's requirements and          |
| --- | ----------------------------- | ------------------------------ |
|     | n to a direct connectio       | plan the migration waves       |
|     | n established using AWS       | accordingly. Plan to put       |
|     | Direct Connect. VPN links     | applications that require      |
|     | generally have higher and     | low latency connections in     |
|     | more variable latency, which  | later waves, when alternative  |
affects data throughput and,  connection types are available
|     | more importantly, application  | .   |
| --- | ------------------------------ | --- |
response times.
Operations considerations
| Have you considered? | Description | Actions |
| -------------------- | ----------- | ------- |
Have you identified an AWS  AWS best practices for a well- In your runbook for applicati
account strategy for your  architected environment  on prioritization, review
landing zone? recommend that you should  your selected migration
|     | separate your resources and    | strategies and use them        |
| --- | ------------------------------ | ------------------------------ |
|     | workloads into multiple AWS    | to determine your account      |
|     | accounts. You can think of     | strategy. For example, if you  |
|     | AWS accounts as isolated       | want to migrate as quickly     |
|     | resource containers: they      | as possible and rehost is the  |
|     | offer workload categorization  | most common migration          |
|     | and can reduce the scope       | strategy, fewer accounts is    |
|     | of impact in the event of a    | easier to manage. However,     |
|     | disaster.                      | if your migration strategies   |
require modernizing applicati
ons and you need to separate
business units for complianc
e reasons, you should include
one or more accounts for
Operations considerations 43

each business unit in your
account strategy.
Do you need to switch Monitoring tools are critical Select a monitoring tool
monitoring tools during the for cloud operations. Your before starting the migration
migration? If so, is this part existing tools might not . Make sure the migration
of the migration process, or work in the cloud because team incorporates instructi
does it occur before or after of compatibility or licensing ons for setting up monitorin
the migration? reasons. As part of the design, g in the migration patterns.
you need to decide which We recommend building
monitoring tools to use for an automation script that
the workload in the AWS replaces or reuses the
Cloud. monitoring tools, as needed.
Have you identified applicati Large migration is a transform Work with a project
on owners, and are they ation rather than just an management office and Cloud
aware of any changes that infrastructure project. Include Enablement Engine team
must be made to the applicati application owners early to to align with application
on so that it functions support the migration. For team leaders and make sure
properly in the cloud? example, application owners that communication is clear
validate the wave plan, create across all application teams.
test plans, and participate in For more information about
the cutover. communication and project
transparency, see the Project
governance playbook for AWS
large migrations.
Operations considerations 44

Have you selected a backup Backup and recovery tools are Select backup and recovery
and recovery solution, and critical for cloud operation tools before starting the
does it work with migrated s. Your existing tools might migration. Make sure the
workloads? not work in the cloud because migration team incorpora
of compatibility or licensing tes instructions for setting
reasons. As part of the design, up backup and recovery
you need to decide which in the migration patterns.
backup and recovery tools to We recommend building
use for the workload in the an automation script that
AWS Cloud. replaces or reuses the backup
and recovery tools, as needed.
Have you identified all shared Shared services are services Schedule a deep dive with
services and deployed them in that support multiple the infrastructure team and
the landing zone? applications, such as email, application team leaders
Active Directory, or shared before completing the
database environments. You landing zone design. Review
typically need to deploy and confirm the list of shared
shared services in the cloud services that you must deploy
before the migration so in the cloud before starting
that migrated applications the migration. The most
perform as expected. common shared services are
Active Directory, network
devices, Domain Name
System (DNS), and infrastru
cture software.
Have you reviewed AWS Every AWS service has a Review the migration plan.
service quotas for your target service quota. Some of these For any target account that
AWS Region and account? quotas can be increased. It is requires an increased service
important to review quotas quota, request an increase.
before cutover. If insufficient For more information and
resources are available, the instructions, see AWS service
cutover might fail. quotas.
Operations considerations 45

Do you need to upgrade your  AWS Enterprise support plan  Contact your AWS account
AWS Support plan? offers 24/7 phone support  team to discuss different
|     | and faster response times  | support options and select  |
| --- | -------------------------- | --------------------------- |
|     | than other plans. Because  | the appropriate support     |
the cutover window is usually  plan for your large migration
|     | very short, having access to  | project. |
| --- | ----------------------------- | -------- |
an experienced engineer to
help resolve cutover issues
can be critical to the success
of a large migration.
Have you notified your AWS  The AWS Enterprise On- Notify your AWS technical
technical account manager  Ramp support team assigns  account manager of your
(TAM) about your large  a pool of Technical Account  upcoming large migration
| migration plan? | Managers (TAMs) who             | project and share your        |
| --------------- | ------------------------------- | ----------------------------- |
|                 | coordinate access to proactive  | migration plan. Your TAMs     |
|                 | programs, preventative          | will make sure AWS support    |
|                 | programs, and AWS subject       | resources are available when  |
|                 | matter experts. Your TAMs       | needed. For example, your     |
|                 | can schedule availability of    | TAMs can schedule a support   |
|                 | support resources as needed.    | engineer during cutover,      |
and the engineer can help
mitigate technical issues and
streamline the cutover.
Security considerations
| Have you considered? | Description | Actions |
| -------------------- | ----------- | ------- |
Have you identified  Manage identity and access  Work with the migration
AWS Identity and Access  for all members of your  team to identify the roles and
Management (IAM) roles  large migration project. By  responsibilities. Determine
and policies for access  attaching IAM roles to the  which roles can access which
management? migrated resources and  AWS account, and identify the
defining access policies, you  level of access that each role
|     | control who can access the  | has. Work with the security  |
| --- | --------------------------- | ---------------------------- |
Security considerations 46

migrated resources in the teams to validate that the
cloud. IAM roles are correct for each
target AWS resource.
Are there any complianc Workloads might have Work with compliance team
e requirements for your different compliance and portfolio team to identify
workloads? requirements, such as the the compliance requireme
Health Insurance Portabili nts for each application,
ty and Accountability Act and design your target AWS
(HIPAA) or payment card account accordingly. For
industry Data Security example, you might need
Standard (PCI DSS). You must to migrate some workloads
identify these requirements to AWS GovCloud (US) or
before the migration and plan to a specific AWS Region.
for how to meet them. We recommend that you
document the complianc
e requirements for each
application so that you can
use this information later in
the application prioritization
and wave planning process.
Does your security team need A large migration project Work with the migration team
to review and approve any to the AWS Cloud uses to identify all of the tools,
tools or services that you plan many services, such as AWS services, and applications
to use during the migration? Application Migration Service, that you expect to use in the
AWS Database Migration migration. Work with the
Service (AWS DMS), AWS security team to review the
DataSync, and portfolio company policies and approve
discovery tools (such as these tools accordingly before
Flexera One). Some organizat the migration starts.
ions require that all new tools
and services are approved
before use.
Security considerations 47

On-premises considerations for a large migration
On-premises infrastructure that supports your business operations must also be prepared for the
large migration. By preparing the current infrastructure, you can help reduce the impact of the
large migration to the business operations and application users.
This section reviews the infrastructure, operations, and security questions that you should consider
when preparing your on-premises infrastructure for the large migration. As you answer the
questions in this section, these decisions become migration principles, which you document
according to the instructions in Document your decisions as large migration principles.
Infrastructure considerations
| Have you considered? | Description | Actions |
| -------------------- | ----------- | ------- |
Have you designed the on- Because of the large number  Review the design of routing
premises DNS and routers to  of servers and target AWS  tables, and make sure there
support traffic to and from  accounts, it is important  are correct routes between
target AWS accounts? to confirm that different  the AWS accounts and on-
|     | networking component        | premises data centers. Also,  |
| --- | --------------------------- | ----------------------------- |
|     | s are configured correctly  | make sure the DNS server is   |
|     | to support the migration    | able to support DNS queries   |
|     | strategies and scale.       | from both on-premises         |
servers and AWS resources.
How will the migration team  The migration team needs  Review the existing authentic
access both the on-premises  to access the source and  ation and authorization
and AWS environments? target servers to perform  mechanisms and build a
|     | migration activities, such as     | strategy to grant access.  |
| --- | --------------------------------- | -------------------------- |
|     | install a replication agent on a  | You can use an Active      |
source server or uninstall old  Directory group, IAM role, and
|     | software on a target server. | Security Assertion Markup  |
| --- | ---------------------------- | -------------------------- |
Language 2.0 (SAML 2.0)
federation to allow single
sign-on to the AWS account.
We recommend creating a
local admin user in case there
On-premises considerations for a large migration 48

are any authentication issues
with Active Directory.
Are there any known  A large migration requires  Review the network configura
congestion points in the  lots of bandwidth to replicate  tion with the networking
current network configura  the data from on-premis  team to better understan
tion that would slow data  es data center to the cloud.  d the network path from
throughput during the  Understanding any existing  the source machines to the
migration? congestion points or limitatio  target AWS accounts. Identify
|     | ns helps you better plan the  | potential congestion points,  |
| --- | ----------------------------- | ----------------------------- |
|     | migration.                    | such as a connection that is  |
shared between the migration
and production workloads.
Operations considerations
| Have you considered? | Description | Actions |
| -------------------- | ----------- | ------- |
Do you have any scheduled  A change freeze during  Review the change
blocked days, also known as migration can take critical  management process with
change freezes, that could  resources and time away from  the operations team, and take
impact the migration? an ongoing migration project. blocked days into considera
tion when you plan cutover
windows.
Have you reserved change  Change management  According to your change
days for the migration? processes can be complex,  management process,
|     | and some organizations         | schedule changes at least five  |
| --- | ------------------------------ | ------------------------------- |
|     | allow changes only in certain  | waves in advance. This helps    |
|     | maintenance windows.           | prevent delays.                 |
Have all of the servers in  System changes or uninstall  Review the dates of the last
scope for the migration been  ed patches might cause  server reboots. If a server has
recently rebooted? issues during the migration,  not been restarted within
|     | which would necessitate long  | the last 90 days, schedule a  |
| --- | ----------------------------- | ----------------------------- |
|     | cutover windows or rolling    | restart before migrating the  |
|     | back the server. The best     | server.                       |
Operations considerations 49

practice is to confirm that
the server has been recently
rebooted on the target side
before migrating.
How does the disaster Disaster recovery and Review the existing disaster
recovery and business business continuity plans recovery and business
continuity plan work today, are critical components of continuity plans and make
and has this been factored meeting the recovery time sure the plans work for your
into the landing zone design? objective (RTO) and recovery target AWS account. If not,
point objective (RPO) of the design new plans before
application. You need to make moving workload to the AWS
sure these plans work for Cloud.
both your on-premises and
AWS workloads during the
transition period.
Security considerations
Have you considered? Description Actions
Have you created firewall Depending on the processes Review the existing firewall
rules to support the large in your organization, it can change process with security
migration? take a long time to complete team, and design a strategy
a change request for firewall for large migration firewall
configurations. changes accordingly. You
might need to design a
custom process for the
large migration project, or
you might need to submit
changes early in the project.
It is recommended that you
consider using an AWS virtual
private cloud (VPC) as an
extension to your data center
and avoid building firewall
Security considerations 50

rules that are too complex,
which could significantly
delay the large migration.
Have you set up Active Active Directory is used for Review the Active Directory
Directory in the AWS authentication and authoriza design with your security and
environment? tion. You need to make infrastructure teams. Make
sure the target account sure the target AWS account
workloads are able to connect has connectivity to the correct
to the domain controller for domain controller. Make sure
authentication and authoriza that the target AWS subnet
tion. You can either add a CIDR blocks are in the correct
new domain controller in the Active Directory sites so that
target VPC, or you can allow the workloads in AWS are
the AWS workload to connect able to connect to the nearest
to the on-premises domain domain controllers.
controllers.
Have you identified third-par Third-party connections and During the deep dive
ty connections and applicati application interdependencies session with the application
on interdependencies? require that you modify the owners, review the external
firewall rule, network access dependencies for each
control list, and security application. Submit a request
group. to modify firewall rules and
the network access control list
and change security groups
accordingly, based on the
third-party dependency
requirements.
Security considerations 51

Does your on-premises You might need to assess and Review the access policy in
environment have any update these security tools in your source environment. If
additional security tools that order to allow the migration a security tool is being used
control access and processes tools to function in the AWS in the access policy, confirm
running on the systems, such landing zone. that the tool functions in the
as CyberArk? AWS Cloud, and then make
sure that the migration team
has access to both the source
and target environments. If
any changes are required,
add these steps into your
migration runbooks.
Document your migration principles
After reviewing the landing zone and on-premises considerations, you should document your
answers and decisions. These become the migration principles that guide the rest of the project.
Do the following:
1. Open the attached Migration principles template (Microsoft Word format).
2. Review the infrastructure, operations, and security considerations in the Landing zone
considerations for a large migration and On-premises considerations for a large migration
sections of this guide, and discuss the questions with the recommended teams.
3. Document the infrastructure, operations, and security decisions in your migration principles
document. For examples of how to record these decisions, see the following table.
4. As needed for your use case, add new categories, items, and principles. For example, you might
want to record migration principles for portfolio assessment or project management decisions.
The following is an example of how you might record your decisions to some of the questions in
this guide.
Category Item Principle
Document your migration principles 52

Infrastructure DNS server Use Amazon-provided
DNS as the primary DNS
server for all Amazon Elastic
Compute Cloud (Amazon EC2)
instances. Set up a condition
al forwarder that forwards
queries to an on-premises
DNS server.
Security groups Use a temporary security
group to permit all standard
infrastructure traffic between
the source and target
environments.
EC2 instance types If utilization data is available
from a discovery tool, such
as Flexera One or modelizeIT,
use this information to help
determine the target instance
type.
If utilization data is not
available, size the target
instance based on the
provisioned central processing
unit (CPU) and memory of the
on-premises infrastructure.
Operations Clean up Servers remain in the staging
area until the migration phase
is complete, at the end of the
hypercare period.
Document your migration principles 53

|     | AWS Backup | By default, the tag applied  |
| --- | ---------- | ---------------------------- |
to each instance is backup
= true. If backups are not
required, the migration teams
should change the tag to
false.
|     | Monitoring | Use Amazon CloudWatch for  |
| --- | ---------- | -------------------------- |
monitoring of EC2 instances
. After cutover, remove the
existing monitoring agent
from the target EC2 instances.
| Security | Active Directory | Build a domain controlle  |
| -------- | ---------------- | ------------------------- |
r in each VPC, and link the
subnet of that VPC to your
Active Directory site. For more
information, see Designing
the Site Topology. This
configures all clients to use
the correct domain controller.
|     | Server access | Users must retrieve a  |
| --- | ------------- | ---------------------- |
password from CyberArk
to connect to the source
machines.
|     | AWS Management Console  | Users must use federated  |
| --- | ----------------------- | ------------------------- |
|     | access                  | login to access the AWS   |
Management Console.
Document your migration principles 54

Resources
AWS large migrations
To access the complete AWS Prescriptive Guidance series for large migrations, see Large migrations
to the AWS Cloud.
Training resources
For training resources, see the following sections of this document:
• Prerequisites
• Fundamentals
• Advanced
Additional references
• AWS service quotas
• Cloud Enablement Engine: A Practical Guide
• Overview of Data Transfer Costs for Common Architectures (AWS blog post)
• Setting up a secure and scalable multi-account AWS environment
AWS large migrations 55

Contributors
The following individuals contributed to this document:
• Chris Baker, Senior Migration Consultant
• Dwayne Bordelon, Senior Cloud Application Architect
• Dev Kar, Senior Consultant
• Wally Lu, Principal Consultant
56

Document history
The following table describes significant changes to this guide.
| Change               | Description                  | Date        |
| -------------------- | ---------------------------- | ----------- |
| Updated name of AWS  | We updated the name of       | May 2, 2022 |
| solution             | the referenced AWS solution  |             |
from CloudEndure Migration
Factory to Cloud Migration
Factory.
| Initial publication | —   | February 28, 2022 |
| ------------------- | --- | ----------------- |
57
