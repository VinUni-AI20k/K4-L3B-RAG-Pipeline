# Migration playbook for AWS large migrations

**Source:** https://docs.aws.amazon.com/pdfs/prescriptive-guidance/latest/large-migration-migration-playbook/large-migration-migration-playbook.pdf

**Landing file:** legal/aws-large-migration-migration-playbook.pdf

---

Migration playbook for AWS large migrations
AWS Prescriptive Guidance
Copyright © 2026 Amazon Web Services, Inc. and/or its affiliates. All rights reserved.

AWS Prescriptive Guidance: Migration playbook for AWS large
migrations
Copyright © 2026 Amazon Web Services, Inc. and/or its affiliates. All rights reserved.
Amazon's trademarks and trade dress may not be used in connection with any product or service
that is not Amazon's, in any manner that is likely to cause confusion among customers, or in any
manner that disparages or discredits Amazon. All other trademarks not owned by Amazon are
the property of their respective owners, who may or may not be affiliated with, connected to, or
sponsored by Amazon.

Table of Contents
Step 1: Review the completed waves and identify gaps in the current migration runbook ... 19
iii

iv

Migration playbook for AWS large migrations
Wally Lu, Chris Baker, Tuhin Mukherjee, and Senay Swinney, Amazon Web Services
In a large migration, the migration workstream uses the wave plans and migration metadata
supplied by the portfolio workstream in order to migrate workloads to the AWS Cloud. The
migration workstream is responsible for submitting any change requests, migrating the
application, coordinating application testing with the application owners, performing cutover,
and monitoring the application through the hypercare period. In the first stage, initializing a large
migration, you create the runbooks that the migration workstream uses to migrate the applications
and servers. In the second stage, implementing a large migration, the migration workstream plans
sprints and uses the migration runbooks in order to migrate and cutover the applications. For more
information about core and supporting workstreams, see Workstreams in a large migration in the
Foundation playbook for AWS large migrations.
This migration playbook outlines the tasks of the migration workstream, which spans both stages
of a large migration, initialization and implementation:
• In stage 1, initialize, you draft, test, and refine the runbooks, and then you automate manual
tasks for each migration pattern.
• In stage 2, implement, you perform the migration with the predefined runbooks built in stage 1.
Guidance for large migrations
Migrating 300 or more servers is considered a large migration. The people, process, and technology
challenges of a large migration project are typically new to most enterprises. This document is
part of an AWS Prescriptive Guidance series about large migrations to the AWS Cloud. This series is
designed to help you apply the correct strategy and best practices from the outset, to streamline
your journey to the cloud.
The following figure shows the other documents in this series. Review the strategy first, then the
guides, and then proceed to the playbooks. To access the complete series, see Large migrations to
the AWS Cloud.
Guidance for large migrations 1

About the runbooks, tools, and templates
We recommend using the attached templates and then customizing them for your portfolio,
processes, and environment. The provided templates include standard processes, typical cutover
processes, and placeholders for processes that are unique to your environment. The instructions in
this playbook tell you when and how to customize each of these templates. This playbook includes
the following templates:
• Rehost migration runbook template
• Rehost migration task list template
For migration patterns, from which you can build your own runbooks, see AWS Prescriptive
Guidance migration patterns.
Migration runbooks require varying levels of detail:
• Detailed runbooks – Detailed runbooks are best suited for migration patterns that you will
repeat many times. For these patterns, we recommend starting with the Rehost migration
runbook template (Microsoft Word format). This template captures as many details as possible,
including screenshots and step-by-step instructions, and it is designed to help multiple people
perform the same task consistently.
• Task List – For migration patterns that are one-off or very simple, a short task list is a better
option. For these patterns, we recommend starting with the Rehost migration task list template
(Microsoft Excel format). This template contains a high-level task list and is typically used for
About the runbooks, tools, and templates 2

tracking and managing ownership of tasks. You can also use a task list to track the status of tasks
that are documented in a runbook.
Whether you are using a detailed runbook or a short task list, verify that your runbook describes
the tasks in sequence. For complex tasks, you can provide links to external documentation.
Attachments
To access additional content that is associated with this document, download and unzip the
following file:
attachment.zip
Attachments 3

Stage 1: Initializing a large migration
In the initialize stage, the goal is to define standard operating procedures (SOPs) for the large
migration, also known as runbooks. You build custom runbooks based on your company's policies
and processes. If another team member is responsible for defining the runbooks in your large
migration project, skip to Stage 2: Implementing a large migration, where you will use the
runbooks to prioritize applications and perform wave planning. Stage 1 consists of the following
tasks and steps:
• Task 1: Validating the migration patterns and migration metadata
• Step 1: Validate the migration patterns
• Step 2: Validate the migration metadata and wave plan
• Task 2: Creating drafts of the migration runbooks
• Step 1: Create a migration runbook draft for each pattern
• Step 2: Update the migration runbooks with your policies and processes
• Task 3: Analyzing and testing your migration runbooks
• Step 1: Conduct a walkthrough of each runbook
• Step 2: Conduct a POC that tests each migration pattern
• Step 3: Review and identify the gaps in the current migration runbook drafts
• Task 4: Improving your migration runbooks
• Step 1: Update the migration runbooks and repeat the testing
• Step 2: Automate repetitive tasks
• Step 3: Build a migration task list
With the migration runbooks in place, in stage 2, the migration teams follow the procedures and
perform large migrations that have predictable and measurable outcomes.
Task 1: Validating the migration patterns and metadata
In this task, you validate the migration patterns identified in the assessment and wave planning
activities in the portfolio workstream, and then you validate the migration metadata source. The
goal is to verify that sufficient data has been collected to support each migration pattern.
This task consists of the following steps:
Task 1: Validating the migration patterns and metadata 4

• Step 1: Validate the migration patterns
• Step 2: Validate the migration metadata and wave plan
Step 1: Validate the migration patterns
In the portfolio workstream, you performed an initial assessment of the application portfolio,
selected migration strategies, and identified migration patterns for each strategy. This information
should be contained in your portfolio assessment runbook. For more information, see the Portfolio
playbook for AWS large migrations.
In this step, you review the migration strategies, verify that you have identified all migration
patterns, and confirm that you are ready to draft migration runbooks. You might repeat this task
throughout the project, and as your understanding of the portfolio matures, it is likely you will
identify additional migration patterns in later stages of the migration.
1. Review the migration strategies for the portfolio
A migration strategy is the approach used to migrate an on-premises application to the AWS
Cloud. There are seven migration strategies for moving applications to the cloud, known as
the 7 Rs. Common strategies for large migrations include rehost, replatform, relocate, and
retire. Refactor is not recommended for large migrations because it involves modernizing the
application during the migration. This is the most complex of the migration strategies, and
it can be complicated to manage for a large number of applications. Instead, we recommend
rehosting, relocating, or replatforming the application and then modernizing the application
after the migration is complete. For more information about the 7 Rs, see the Guide for AWS
large migrations.
Based on the output of the initial portfolio assessment, you have a list of all the required
migration strategies for the portfolio and determined how much of the portfolio is allocated to
each strategy. For example:
• Rehost - 70%
• Replatform - 20%
• Retire - 10%
2. Verify that the migration patterns for the portfolio
A migration pattern is a repeatable migration task that details the strategy, the destination,
and the application or service used. In this step, you verify that the migration patterns include
Step 1: Validate the migration patterns 5

detailed information, such as which tools to use and which AWS services are targeted. For
example:
• Rehost to Amazon Elastic Compute Cloud (Amazon EC2) by using AWS Application Migration
Service (AWS MGN) or Cloud Migration Factory
• Replatform to Amazon EC2 by using AWS CloudFormation templates to build new
infrastructure in the AWS Cloud
• Replatform to Amazon Relational Database Service (Amazon RDS) by using AWS Database
Migration Service (AWS DMS) or a native database technology
• In the Portfolio playbook for AWS large migrations, you map each migration pattern to its
migration strategy and document the results in a table like the following example.
Strategy Pattern
Rehost Rehost to Amazon EC2 by using Application
Migration Service or Cloud Migration Factory
Replatform Replatform to Amazon RDS by using AWS
DMS or a native database technology
Replatform Replatform to Amazon EC2 by using AWS
CloudFormation templates to build new
infrastructure in the AWS Cloud
Step 2: Validate the migration metadata and wave plan
In this step, you validate the source location of the migration metadata. You check that the data
structure, such as the available columns in an Excel document, is suitable to hold the required
metadata, and you check that all the metadata is available.
1. Validate the migration metadata for your migration patterns
Each migration pattern needs a different set of migration metadata in order to migrate the
servers and apps. For example, a rehost migration to Amazon EC2 requires that you provide
specifications for the target instance, such as the VPC subnet, security group, and instance type
information. However, a storage migration, database migration, or replatform migration requires
a different set of migration metadata. You typically define migration metadata requirements in
Step 2: Validate the migration metadata and wave plan 6

the portfolio assessment runbook, but you need to make sure that you have sufficient metadata
to support each of your migration patterns. For more information about metadata identification
and collection, see the Portfolio playbook for AWS large migrations.
2. Validate the source location of the migration metadata and the wave plan
You typically document the source location of the migration metadata in your metadata
management runbook. Ideally, the location acts as a single source of truth, such as a wave-
planning spreadsheet. It is also possible that the metadata is still in multiple places, including
the following common locations:
• Discovery tool
• Configuration management database (CMDB)
• App owner questionnaire
• Migration wave-planning spreadsheet
Validate the following for the metadata source location:
a. Is the source catalog being maintained with locations of all metadata sources and owners?
b. Does the source location (for example, wave-planning spreadsheet) have all the required
migration metadata?
c. Are there clear instructions for accessing each metadata source?
d. If there is no single source, is each metadata source clearly mapped to its attributes?
e. Is there a clear wave plan for the servers and apps, and are at least five waves ready for the
migration workstream?
f. Is there a process to update the sources? If so, what is the frequency and notification process?
Task exit criteria
When you have met the following exit criteria, proceed to the next task:
• You have validated the list of clearly defined migration patterns.
• The source location of the migration metadata has all the required metadata for each pattern, or
a process is in place to capture any missing metadata.
• You have validated the wave plan and migration metadata for at least five waves, and you have
defined a process for notifications and updates.
Task exit criteria 7

Task 2: Creating drafts of the migration runbooks
In this task, you draft and review migration runbooks for each migration pattern. For example,
you draft a migration runbook for rehost to Amazon EC2 and another runbook for replatform to
Amazon RDS. You repeat this task until you have drafted a migration runbook for every migration
pattern identified in the previous task.
You can use the attached runbook templates and customize them for your environment. For
migration patterns that are repeated frequently, we recommend using the Rehost migration
runbook template (Microsoft Word format), and for patterns that are one-off or very simple, we
recommend the Rehost migration task list template (Microsoft Excel format). You can also use a
task list to track the status of tasks that are documented in a runbook. For more information, see
About the runbooks, tools, and templates.
This task consists of the following steps:
• Step 1: Create a migration runbook draft for each pattern
• Step 2: Update the migration runbooks with your policies and processes
Step 1: Create a migration runbook draft for each pattern
In this step, you draft runbooks for each of your migration patterns. A complete migration runbook
typically contains instructions for how to use the selected migration service or tool, any tasks that
are unique to your environment, and cutover instructions.
1. Open the attached Rehost migration runbook template (Microsoft Word format).
2. Update the Premigration tasks section, Migration tasks section, and Cutover tasks section with
instructions that are specific to your migration pattern. Depending on your use case, you might
need to update all three sections. Include the following when customizing your tasks:
• Standard migration instructions for the selected service – You can typically find the
information needed to complete your template in AWS documentation. For example, see the
following:
• How to use the new AWS Application Migration Service for lift-and-shift migrations
• Getting started with AWS DataSync
• AWS Database Migration Service step-by-step walkthroughs
Task 2: Creating drafts of the migration runbooks 8

• Tasks that are unique to your IT environment – Record the tasks that are unique to your IT
operations and environment. The goal is that a new person joining your migration teams can
follow the runbook with minimal learning curve. For example, what monitoring software do
you need to install on the target machine after cutover? Which Domain Name System (DNS)
server do you use for that subnet? How do you submit a request for change (RFC)?
• Cutover tasks – Every environment has a slightly different cutover process. It is important to
document all the steps for cutover in your environment because you want everyone to follow
the same process. Documenting these steps minimizes time spent in the cutover window and
helps you plan the amount of time needed to complete the cutover.
Step 2: Update the migration runbooks with your policies and
processes
Runbook and task list templates cover the majority of the migration tasks, or the portion of the
process that is standard. The remaining tasks are unique to your environment, and you must
customize the runbook accordingly. For example, consider whether your runbooks should contain
custom tasks for the following processes in your environment.
Connectivity
• How to connect to a VMware environment
• How to connect to a DNS server and update DNS records
• How to connect to the migration automation server
• How to connect to the source environment
• How to connect to a document repository, such as SharePoint or Confluence
Permissions and change management
• How to submit an RFC in your environment
• How to review the status of the RFC for each wave
• How to grant access for a new migration engineer
• How to request permissions to the source servers
• How to request permissions to the target AWS account
• Who has permission to connect to the target server after the cutover
Step 2: Update the migration runbooks with your policies and processes 9

Migration implementation and cutover
• Which software to install or uninstall on the target server
• How to change infrastructure settings, such as firewall, routing, and load balancer settings
• Who can change infrastructure settings
• How to change the application configuration during cutover
• How to conduct application testing
• How to complete a cutover and go-live
• How to complete tasks that occur after cutover, such as configuring monitoring or backups
Some of these tasks might sound trivial, but knowledge and permissions vary in any environment.
It is important to document these tasks in the same migration runbook.
Tip
We highly recommend using automation to accelerate your large migration. Using a
migration factory model simplifies and reduces the number of issues with repetitive tasks,
especially for rehost and replatform migration patterns. AWS Cloud Migration Factory
Solution was designed to help customers migrate at scale with automation. You can deploy
the solution and use predefined automation scripts in your runbook.
Task exit criteria
Repeat this task as necessary, and when you have met the following exit criteria, proceed to the
next task:
• You have drafted a runbook for each migration pattern.
• Each runbook draft contains three main sections: pre-migration tasks, migration tasks, and
cutover tasks.
• Your runbook drafts include tasks that are unique to your environment.
• Your detailed runbook drafts include step-by-step guidance and screenshots.
Task exit criteria 10

Task 3: Analyzing and testing your migration runbooks
In this task, you walk through each runbook that you built in the previous task, analyze any
identified gaps, conduct a migration proof of concept (POC), and review the notes and feedback.
This task consists of the following steps:
• Step 1: Conduct a walkthrough of each runbook
• Step 2: Conduct a POC that tests each migration pattern
• Step 3: Review and identify the gaps in the current migration runbook drafts
Step 1: Conduct a walkthrough of each runbook
In this step, the migration teams assess the runbook and task sequence as though they were
performing it for real. The migration teams meet and review each step, and the team members
ask questions and share their feedback. This walkthrough process helps the teams identify missing
steps and sequence issues. Complete the walkthrough as follows:
1. Gather the migration teams that are responsible for completing the tasks in the runbook.
2. Walk through the steps in the runbook one by one, as if this was a live migration. As you go,
identify and make note of any gaps or issues. Do not perform the migration or tasks as part of
the walkthrough.
3. Update the runbook draft to address any gaps or issues identified in the walkthrough.
Step 2: Conduct a POC that tests each migration pattern
1. Select a POC candidate from the already prepared waves.
2. Open the migration runbook draft.
3. Complete the runbook step by step in order to migrate the POC candidate as follows:
• Follow every step in the runbook. Do not make assumptions or make your own decisions.
• Assume the person using the runbook has no prior knowledge about migration or your
environment.
• If a step is not clear but you can continue, make note of the step and continue.
Task 3: Analyzing and testing your migration runbooks 11

• If a step is missing and you can't continue, stop, and highlight the section from which you
could not proceed. Work with the runbook owner to clarify the missing step so that you can
continue and complete the POC.
Step 3: Review and identify the gaps in the current migration runbook
drafts
1. Review any issues or gaps identified in the previous steps.
2. Analyze the gaps and consider the following questions:
• Does the runbook have the steps needed to complete a migration and cutover, from end to
end?
• Does the runbook contain reference links for the tasks that are predefined in your
environment?
• Does the runbook clearly defined who, what, when, and how to complete a task?
Task exit criteria
When you have met the following exit criteria, proceed to the next task:
• You have reviewed and tested each migration runbook.
• For each runbook, you have completed a migration POC for at least one application and for more
than two operating system (OS) variants.
• You have identified and documented the identified gaps and issues in each runbook.
Task 4: Improving your migration runbooks
In this task, you improve the runbooks by repeating the POC multiple times. With each wave, the
POC test and retrospective, a meeting in which the team reviews the completed wave, provide
opportunity to improve the runbooks. You also improve your runbooks by automating repetitive
tasks, which increases the velocity of the migration and reduces the risk of manual configuration
errors.
This task consists of the following steps:
• Step 1: Update the migration runbooks and repeat the testing
Step 3: Review and identify the gaps in the current migration runbook drafts 12

• Step 2: Automate repetitive tasks
• Step 3: Build a migration task list
Step 1: Update the migration runbooks and repeat the testing
1. For the issues and gaps identified in the previous task, update the runbooks with detailed
instructions. For example:
• If a step is missing, add step-by-step instructions
• If a step is not clear, consider updating the text, adding a screenshot, or adding reference links
2. Repeat the previous task until you are satisfied that the instructions are complete and clear.
3. Test the final draft of each runbook by asking a new migration team member, one who has not
tested this runbook before, to perform a POC and complete the runbook.
Step 2: Automate repetitive tasks
1. Review each runbook and identify areas of automation for manual tasks. Consider the following
probing questions:
• Are there any repetitive, manual tasks for each server or app in the runbook?
• Are there any actions that you perform on every server or application?
• Do you need to install or uninstall software on the target server?
• Do you need to change network or infrastructure settings one by one for each server?
• Do you need to manually copy and paste any data?
2. Build automation scripts and update the runbooks.
3. Repeat task 3 and task 4 until you have documented the runbooks with clear and complete
information and automated repetitive migration tasks.
Note
For automating migration tasks, we highly recommend that you build new scripts or
customize existing scripts in AWS Cloud Migration Factory Solution.
Step 1: Update the migration runbooks and repeat the testing 13

Step 3: Build a migration task list
A migration task list can help you manage the status and owners of tasks. You build a task list for
each migration runbook, and you include the high-level information from the runbook without
including the details. A task list typically contains the following information, and you can add more
attributes as needed:
• Descriptive name, such as:
• Check server OS version
• Install an agent
• Restart a server
• Update the DNS
• Dependencies
• Sequence of tasks
• Owner
• Estimation of time required to complete each task
• Status
There are many tools available for creating and managing task lists. You can use the attached
Rehost migration task list template (Microsoft Excel format). You can also use project management
tools, such as Jira or a Kanban board.
Note
We also recommend using the Excel task list template to document small, well-understood,
or non-repetitive tasks, such as restarting a server or getting an IP address. These tasks
should be captured and tracked but don't require the detailed steps of the Word runbook
template.
Task exit criteria
Repeat this task as necessary, and when you have met the following exit criteria, proceed to the
next task:
Step 3: Build a migration task list 14

• You have identified opportunities for automation and have either developed automation scripts
or have a plan to do so.
• Three or more people have peer-reviewed each runbook.
• Two or more people who were not on the development team for the runbook have tested it end-
to-end.
• Using the most up-to-date runbook, you have migrated 20 or more servers to more than one
AWS account.
• You have developed a task list to help track and manage the progress of the migration.
Task exit criteria 15

Stage 2: Implementing a large migration
In stage 1, you developed migration runbooks for each migration pattern. In stage 2, you use these
runbooks to migrate servers and then improve the runbooks in order to accelerate the velocity of
the migration. Building and updating runbooks is not a one-off task. You might need to do that
throughout your large migration journey. For example, you might need to create new runbooks if
the scope increases and you identify new migration patterns, or you might need to improve the
existing runbooks if the migration velocity is below the target and introducing more automation
would reduce the number of manual tasks and accelerate the migration.
Note
The wave plan developed in the portfolio workstream determines the activities in the
migration workstream. Before starting stage 2, verify that you have validated your wave
plan. For instructions and more information about the wave plan, see Portfolio playbook
for AWS large migrations.
Stage 2 consists of the following tasks and steps:
• Task 1: Performing sprint planning for scheduled waves
• Step 1: Review the backlog for the scheduled waves
• Step 2: Assign tasks and establish due dates
• Task 2: Performing migration tasks
• Task 3: Performing cutover tasks
• Task 4: Reviewing and improving the migration runbooks
• Step 1: Review the completed waves and identify gaps in the current migration runbook
• Step 2: Update the migration runbooks and complete testing
Task 1: Performing sprint planning for scheduled waves
In this task, you assign waves to sprints, which is a fixed period of time in which the migration team
works on all waves within that sprint. If each sprint is 2 weeks in duration, each wave spans at least
two sprints. Sprint planning refers to the process of assigning owners and due dates to all of the
tasks within that sprint.
Task 1: Performing sprint planning for scheduled waves 16

This task consists of the following steps:
• Step 1: Review the backlog for the scheduled waves
• Step 2: Assign tasks and establish due dates
Step 1: Review the backlog for the scheduled waves
In this step, you review existing backlogs, or current and pending tasks, for all the concurrent
waves, and you use the recommended tools and mechanisms to manage the wave. For example,
you might use a Kanban board with a swimlane for each wave, or you might use Jira and track
waves with stories and epics. For more information, refer to the Project governance playbook for
AWS large migrations.
Step 2: Assign tasks and establish due dates
In this step, for all waves in this sprint, you assign owners to each task and set a due date
accordingly. You can use the migration task list spreadsheet you created in stage 1 to manage
your wave progress, task ownership, and due dates, and the tasks are defined in detail in the
migration runbook for each pattern. Because waves typically overlap, it is common to manage
many concurrent tasks from different waves at the same time. In addition, each wave can range
from 3-6 weeks, depending on your internal process. For an example of a wave schedule, see the
Stage 2: Implement a large migration section of the Guide for AWS large migrations.
Important
Do not add tasks to the sprint without updating the runbook or task list. These documents
that you built in stage 1 should be a source of truth for all your migration activities. If any
step is missing or incorrect, update and validate the runbook before adding tasks to the
sprint.
Task 2: Performing pre-migration and migration tasks
Now you perform pre-migration and migration tasks and adhere to a schedule based on your sprint
planning outcome. A sprint backlog contains a list of all tasks in the migration, for all waves in the
current sprint, and organizes the tasks by week. For a list of tasks, see your migration runbooks for
each migration pattern, which were created in stage 1 of this playbook. For the wave schedule, see
Step 1: Review the backlog for the scheduled waves 17

your project management tools, which were established in the Project governance playbook for
AWS large migrations. Perform the tasks in the scheduled weeks. The following is an example of a
rehost migration task schedule in which there are migration tasks for different waves in the same
week.
| Task name            | Wave   |     | Category |     | Owner    |
| -------------------- | ------ | --- | -------- | --- | -------- |
| Verify prerequisites | Wave 1 |     | Build    |     | Jane Doe |
| Install replication  | Wave 1 |     | Build    |     | Jane Doe |
agent
| Validate launch  | Wave 2 |     | Validate |     | Jane Doe |
| ---------------- | ------ | --- | -------- | --- | -------- |
template
| Launch test instances | Wave 3 |     | Boot-up testing |     | Jane Doe |
| --------------------- | ------ | --- | --------------- | --- | -------- |
Task 3: Performing cutover tasks
At this point, you have completed the migration tasks and tested all of the servers and apps, and
you are ready for cutover. Use the RACI matrices you created in the Foundation playbook for AWS
large migrations to manage the tasks and ownership of each cutover task, and use your migration
runbook for each pattern to perform the cutover activities. The following table is an example
of how you might track and manage cutover progress. It is common to have multiple migration
patterns in the same wave for different applications.
| Task name | Wave | Migration  |     | Owner | Status |
| --------- | ---- | ---------- | --- | ----- | ------ |
runbook
| Check replicati  | Wave 1 | Rehost        |     | Jane Doe | Completed   |
| ---------------- | ------ | ------------- | --- | -------- | ----------- |
| on               |        | to Amazon EC2 |     |          |             |
| Launch cutover   | Wave 1 | Rehost        |     | Jane Doe | Completed   |
| EC2 instance     |        | to Amazon EC2 |     |          |             |
| Validate EC2     | Wave 1 | Rehost        |     | Jane Doe | In progress |
| instance status  |        | to Amazon EC2 |     |          |             |
Task 3: Performing cutover tasks 18

| Launch        | Wave 1 | Replatform to  | John Smith | In progress |
| ------------- | ------ | -------------- | ---------- | ----------- |
| databases in  |        | Amazon RDS     |            |             |
Amazon RDS
| Complete      | Wave 1 | Replatform to   | John Smith | Not started |
| ------------- | ------ | --------------- | ---------- | ----------- |
| storage data  |        | Amazon Elastic  |            |             |
| transfer      |        | File System     |            |             |
(Amazon EFS)
| Perform app  | Wave 1 | All | Jane Doe | Not started |
| ------------ | ------ | --- | -------- | ----------- |
testing
| App acceptance  | Wave 1 | All | Jane Doe | Not started |
| --------------- | ------ | --- | -------- | ----------- |
decision
Task 4: Reviewing and improving the migration runbooks
This task consists of the following steps:
• Step 1: Review the completed waves and identify gaps in the current migration runbook
• Step 2: Update the migration runbooks and complete testing
Step 1: Review the completed waves and identify gaps in the current
migration runbook
Fail fast is a philosophy that uses frequent and incremental testing to reduce the development
lifecycle, and it is a critical part of an agile approach to a large migration. After each cutover,
schedule a retrospective meeting to review each task with the migration teams. Ask the following
probing sample questions. You can also add your own questions:
• Was the cutover successful? If not, what was the issue?
• Does the migration runbook cover all of the tasks to perform the migration and cutover?
• Do any of the tasks take longer than expected?
• Are you aware of any technical issues with any tasks in the runbook?
• Are there any manual tasks that can be automated?
Task 4: Reviewing and improving the migration runbooks 19

• Are there any process-related issues with the runbook or cutover?
Step 2: Update the migration runbooks and complete testing
After collecting data from the retrospective meeting, update the migration runbooks as follows:
• Add detailed instructions for any missing steps.
• Fix or update any steps as needed.
• Perform an end-to-end migration test with at least one Windows and one Linux server.
• Send the updated runbook to the migration teams for use in the next wave.
Step 2: Update the migration runbooks and complete testing 20

Resources
AWS large migrations
To access the complete AWS Prescriptive Guidance series for large migrations, see Large migrations
to the AWS Cloud.
Additional references
• AWS Cloud Migration Factory Solution
• AWS Prescriptive Guidance migration patterns
AWS large migrations 21

Contributors
The following individuals contributed to this document:
• Chris Baker, Senior Migration Consultant
• Wally Lu, Principal Consultant
22

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
23
