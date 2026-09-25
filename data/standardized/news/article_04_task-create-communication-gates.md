# Task: Defining communication gates and schedules

**Source:** https://docs.aws.amazon.com/prescriptive-guidance/latest/large-migration-governance-playbook/task-create-communication-gates.html

**Landing file:** news/article_04_task-create-communication-gates.json

**Crawled:** 2026-09-25T10:20:13

---

In stage 2 of a large migration project, the portfolio workstream is actively planning waves, and the migration workstream is migrating those waves. The project governance workstream oversees these activities and helps guide the waves through communication gates. A _communication gate_ is a touchpoint when you formally communicate ongoing wave activities and status to the stakeholders. At each gate, a designated gate owner notifies the specified audience about the wave status and reminds application owners about upcoming activities or meetings. Gates typically correspond with migration milestones, and defining communication gates maximizes transparency for all project stakeholders. You move waves through the gates individually, or you can group waves together.
In this task, you do the following:
  * [Step 1: Define the communication gates](https://docs.aws.amazon.com/prescriptive-guidance/latest/large-migration-governance-playbook/task-create-communication-gates.html#step-communication-gates)
  * [Step 2: Create a T-minus schedule template](https://docs.aws.amazon.com/prescriptive-guidance/latest/large-migration-governance-playbook/task-create-communication-gates.html#step-create-tminus-schedule)
  * [Step 3: Create standard email templates for each gate](https://docs.aws.amazon.com/prescriptive-guidance/latest/large-migration-governance-playbook/task-create-communication-gates.html#step-email-templates)


## Step 1: Define the communication gates
During the migration, you repeat the communication gates for each wave or for a group of waves, until you have migrated all workloads and the project is complete. At a minimum, we recommend the following communication gates. You might decide to add more gates to your project as appropriate for your project.  
| Gate  | Approximate timeline  | Purpose  | Gate owner  | Audience  |  
| --- | --- | --- | --- | --- |  
| Gate 1: Create T-minus schedule  | Before wave plan complete  | Schedule dates for each gate  | Project manager or communications team  | Application owners, communication lead, migration lead  |  
| Gate 2: T-28 commit meeting  | 4 weeks prior to cutover  | Kick off wave with application owners   | Project manager or communications team  | Application owners, communication lead, migration lead  |  
| Gate 3: T-21 communication  | 3 weeks prior to cutover  | Reminder that cutover is scheduled to occur in 21 days  | Project manager or communications team  | Application owners, communication lead  |  
| Gate 4: T-14 checkpoint meeting  | 2 weeks prior to cutover  | Review the schedule and assess progress on readiness tasks   | Project manager and migration lead  | Application owners, communication lead, migration lead  |  
| Gate 5: T-7 communication  | 1 week prior to cutover  | Reminder that cutover is scheduled to occur in 7 days  | Communications team  | Application owners, operations team  |  
| Gate 6: T-1 go or no-go meeting  | 24–48 hours prior to cutover  | Confirm readiness for migration cutover  | Project manager or communications team  | Cloud operations team, application owners, infrastructure team   |  
| Gate 7: T-0 cutover meeting  | Day of cutover   | Cut over and test the applications   | Project manager and migration lead  | Cloud operations team  |  
| Gate 8: Hypercare period start  | 1 business day after cutover  | Notification that cutover is complete and hypercare period has started  | Project manager or communications team  | Application owners  |  
| Gate 9: Hypercare period end  | 4 business days after cutover  | Notification that hypercare period is complete  | Project manager, communications team, or cloud operations team  | Application owners in wave, communication lead, cloud operations team   |  
The following image shows the sequence of these communication gates in the portfolio and migration workstreams. Gate 1 occurs during wave planning, gates 2–6 occur during the migration, gate 7 is the cutover meeting, and gates 8–9 occur during the hypercare period. Gates 2–6 are named with the format T-#. The T refers to time remaining, and the # is the number of days remaining until the scheduled cutover date.
Define the communication gates for your large migration project as follows:
  1. Determine whether you require additional communication gates for your project. For example, if your project doesn't have a single-threaded leader who is responsible for facilitating migration readiness with application owners, you might want to include additional communication gates for reminding application owners about upcoming activities and due dates.
  2. In a shared repository or project-tracking application, such as Jira or Confluence, record the communication gates for your large migration project. Make sure that you record the following attributes for each gate:
     * Gate number and name
     * Approximate timeline of when the gate occurs in relation to workstream milestones or cutover
     * Purpose of the gate
     * The individual or team who is responsible for the gate, known as the _gate owners_
     * The individuals or teams who receive the communication or attend the gate meeting, known as the _audience_
     * (Optional) The communication template or presentation template that the gate owner should use


## Step 2: Create a T-minus schedule template
A _T-minus schedule_ is a visual way to represent all of the high-level migration activities that need to be completed for each wave. It covers the period of time between the end of wave planning and the end of the hypercare period. Because the high-level migration activities vary based on the migration strategy, you need a T-minus schedule template for each migration strategy. You share the T-minus schedules at the kickoff meeting and at the T-28 and T-14 commit meetings.
Typically, you build a T-minus schedule by working back from the cutover date. You organize the activities into migration milestones, and you track detailed tasks separately within your project management tools. The T-minus schedule also highlights the communication gates that you defined in [Step 1: Define the communication gates](https://docs.aws.amazon.com/prescriptive-guidance/latest/large-migration-governance-playbook/task-create-communication-gates.html#step-communication-gates).
We recommend starting with the attached _T-minus schedule template_ (Microsoft PowerPoint format). Do the following:
  1. Open the _T-minus schedule template_. This template contains a default T-minus schedule for the rehost migration strategy.
  2. Modify the default rehost migration activities based on your use case. For a list of activities for each migration strategy, refer to the responsible, accountable, consulted, informed (RACI) matrices that you created in the [Foundation playbook for AWS large migrations](https://docs.aws.amazon.com/prescriptive-guidance/latest/large-migration-foundation-playbook/).
  3. Modify the default communication gates based on the decisions you made in [Step 1: Define the communication gates](https://docs.aws.amazon.com/prescriptive-guidance/latest/large-migration-governance-playbook/task-create-communication-gates.html#step-communication-gates).
  4. Using the rehost T-minus schedule as a starting point, create a T-minus schedule for each migration strategy, such as replatform or refactor.
  5. Share the T-minus schedules with the communications team, migration team, and cloud operations team. Make sure that all teams are in alignment and no adjustments are necessary.
  6. Add the completed T-minus schedule templates to your kickoff presentation and to your wave workshop presentation.


## Step 3: Create standard email templates for each gate
Create templates for the email communications that you will send to application owners at each communication gate. These emails should contain basic information about the applications in the wave, inform application owners of the wave status, and remind stakeholders about any upcoming due dates and meetings.
We recommend starting with the following attached templates:
  * _Communication template for T-28_(Microsoft Word format)
  * _Communication template for T-21_(Microsoft Word format)
  * _Communication template for T-14_(Microsoft Word format)
  * _Communication template for T-7_(Microsoft Word format)
  * _Communication template for T-1_(Microsoft Word format)
  * _Communication template for T-0_(Microsoft Word format)
  * _Communication template for cutover complete_(Microsoft Word format)
  * _Communication template for hypercare complete_(Microsoft Word format)


## Task exit criteria
This task is complete when you have done the following:
  * You have defined the communication gates for your large migration project.
  * You have created a T-minus schedule template.
  * You have shared the T-minus schedule template with the project stakeholders.
  * You have integrated the T-minus schedule template into your kickoff presentation and your wave workshop presentation.
  * You have created standard templates for gate email communications.
