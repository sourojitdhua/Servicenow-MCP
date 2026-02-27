# ServiceNow MCP Server — Usage Guide

**106 tools. 19 modules. One natural-language interface to your entire ServiceNow instance.**

This guide shows you how to set up the MCP server, connect it to Claude (or any MCP client), and includes **50 ready-to-use prompts** covering every module.

---

## Table of Contents

1. [Setup](#1-setup)
2. [Connecting to Claude Desktop](#2-connecting-to-claude-desktop)
3. [Connecting to Claude Code (CLI)](#3-connecting-to-claude-code-cli)
4. [How It Works](#4-how-it-works)
5. [50 Best Prompts](#5-50-best-prompts)
   - [Incident Management](#incident-management)
   - [Change Management](#change-management)
   - [Problem Management](#problem-management)
   - [Service Catalog](#service-catalog)
   - [Request Management](#request-management)
   - [CMDB Management](#cmdb-management)
   - [SLA Management](#sla-management)
   - [User & Group Management](#user--group-management)
   - [Knowledge Base](#knowledge-base)
   - [Agile & Project Management](#agile--project-management)
   - [Workflow & Script Management](#workflow--script-management)
   - [Update Sets](#update-sets)
   - [Generic Table Operations & Analytics](#generic-table-operations--analytics)
   - [Multi-Step Workflows](#multi-step-workflows)
6. [Tips for Writing Effective Prompts](#6-tips-for-writing-effective-prompts)
7. [Environment Variables Reference](#7-environment-variables-reference)

---

## 1. Setup

### Install

```bash
pip install snow-mcp
```

Or from source:

```bash
git clone https://github.com/sourojitdhua/ServicenowMCP.git
cd ServicenowMCP
pip install -e .
```

### Configure Credentials

Create a `.env` file in the project root:

```env
SERVICENOW_INSTANCE=https://your-instance.service-now.com
SERVICENOW_USERNAME=your-username
SERVICENOW_PASSWORD=your-password
```

### Verify

```bash
snow-mcp --list-tools
```

This should print all 106 tools grouped by module.

---

## 2. Connecting to Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "servicenow": {
      "command": "snow-mcp",
      "env": {
        "SERVICENOW_INSTANCE": "https://your-instance.service-now.com",
        "SERVICENOW_USERNAME": "your-username",
        "SERVICENOW_PASSWORD": "your-password"
      }
    }
  }
}
```

Restart Claude Desktop. You should see the ServiceNow tools available in the tool picker.

---

## 3. Connecting to Claude Code (CLI)

Add to your `.claude/settings.json` or project-level MCP config:

```json
{
  "mcpServers": {
    "servicenow": {
      "command": "snow-mcp",
      "args": [],
      "env": {
        "SERVICENOW_INSTANCE": "https://your-instance.service-now.com",
        "SERVICENOW_USERNAME": "your-username",
        "SERVICENOW_PASSWORD": "your-password"
      }
    }
  }
}
```

---

## 4. How It Works

When you send a natural-language prompt to Claude with the ServiceNow MCP server connected:

1. **Claude reads your intent** — it understands what ServiceNow operation you need.
2. **Claude picks the right tool(s)** — from the 106 available, it selects the matching tool and fills in the parameters.
3. **The MCP server calls the ServiceNow REST API** — with proper authentication, error handling, and retry logic.
4. **Claude formats the response** — turning raw JSON into a human-readable answer.

You never need to know tool names, sys_ids, or API endpoints. Just ask in plain English.

---

## 5. 50 Best Prompts

Below are 50 prompts you can copy-paste directly into Claude. They are organized by module and progress from simple lookups to complex multi-step workflows.

> **Note:** Replace placeholder values like `INC0010001`, team names, or descriptions with your actual data.

---

### Incident Management

**1. List recent incidents**
```
Show me the 10 most recently created incidents.
```

**2. Get incident details by number**
```
Get me the full details of incident INC0010001.
```

**3. Create a new incident**
```
Create a high-urgency incident with the description "Email server is
unreachable for all users in Building A". Set impact to High.
```

**4. Update an incident**
```
Update incident INC0010001 — change the priority to Critical and assign
it to the Network Operations group.
```

**5. Add a comment and work note**
```
Add a customer-visible comment to INC0010001 saying "We are investigating
the issue and will provide an update within 30 minutes." Also add an
internal work note saying "Initial triage: DNS resolution failing for
mail.company.com".
```

**6. Resolve an incident**
```
Resolve incident INC0010001 with close notes "Root cause was a misconfigured
DNS record. Corrected the A record for mail.company.com." Use resolution
code "Solution provided".
```

**7. Search incidents by keyword**
```
Search the incident table for any records mentioning "VPN timeout".
```

**8. List incidents with filters**
```
Show me all active Priority 1 incidents assigned to the Service Desk group.
```

---

### Change Management

**9. Create a change request**
```
Create a Normal change request titled "Upgrade database server from
PostgreSQL 14 to 16". Set impact to Medium, urgency to Low. The planned
start date is 2026-03-15 02:00:00 and end date is 2026-03-15 06:00:00.
```

**10. Add a task to a change**
```
Add a task to change request CHG0030001 with the description "Take a full
database backup before starting the upgrade".
```

**11. Submit a change for approval**
```
Submit change request CHG0030001 for approval.
```

**12. Approve or reject a change**
```
Approve change request CHG0030001 with the note "Reviewed the plan and
test results. Approved for the maintenance window."
```

**13. List pending changes**
```
List all open change requests that are currently waiting for approval.
```

---

### Problem Management

**14. Create a problem from recurring incidents**
```
Create a problem record titled "Recurring VPN disconnections during peak
hours" with impact Medium and urgency Medium. Description: "Multiple
incidents (INC0010045, INC0010052, INC0010061) report the same VPN
timeout issue between 9-11 AM daily."
```

**15. Mark a problem as a Known Error**
```
Mark the problem PRB0040001 as a Known Error with the workaround:
"Users can reconnect by switching to the backup VPN gateway at
vpn-backup.company.com."
```

**16. List open problems**
```
Show me all open problem records sorted by priority.
```

---

### Service Catalog

**17. Browse the catalog**
```
List all available service catalogs and their categories.
```

**18. Search catalog items**
```
Search the service catalog for items related to "laptop".
```

**19. Get catalog item details**
```
Show me the full details and variables (form fields) for the "New Laptop
Request" catalog item.
```

**20. Create a new catalog with categories**
```
Create a new service catalog called "Developer Tools" with two categories:
"Cloud Services" and "Local Development".
```

**21. Add a form field to a catalog item**
```
Add a mandatory single-line text variable called "business_justification"
with the label "Please provide a business justification" to the catalog
item with sys_id abc123. Place it as the first field on the form.
```

---

### Request Management

**22. Create a service request**
```
Create a new service request titled "New monitor for desk 4B-201" with
description "User needs a 27-inch monitor to replace a broken one."
```

**23. Check request status**
```
Get the status and details of request REQ0010001.
```

**24. Add a comment to a request**
```
Add a comment to REQ0010001 saying "Your monitor has been ordered and
will arrive by Friday."
```

---

### CMDB Management

**25. List CI classes**
```
What CMDB CI classes are available that relate to "server"?
```

**26. Find a specific CI**
```
List all Configuration Items in the cmdb_ci_server class that have
"prod-web" in their name.
```

**27. Create a new CI**
```
Create a new server CI called "PROD-WEB-05" in the cmdb_ci_server class
with IP address 10.0.1.55, OS "Linux", and serial number "SN-2026-0055".
```

**28. Check CI relationships**
```
Show me all parent and child relationships for the CI with sys_id xyz789.
```

---

### SLA Management

**29. List SLA definitions**
```
List all SLA definitions currently configured in the instance.
```

**30. Check breached SLAs**
```
Show me all SLA records that have been breached. Which incidents are
affected and how long ago did the breach happen?
```

**31. Check SLAs on a specific task**
```
What SLAs are attached to incident INC0010001? Are any close to breaching?
```

---

### User & Group Management

**32. Create a new user**
```
Create a new user: first name "Jane", last name "Chen", username
"jane.chen", email "jane.chen@company.com", title "Senior Developer",
department Engineering.
```

**33. Find a user**
```
Look up the user with email address john.smith@company.com.
```

**34. Create a group and add members**
```
Create a new group called "Cloud Infrastructure Team" and add users
jane.chen and john.smith to it.
```

**35. List active users in a department**
```
List all active users in the Engineering department.
```

---

### Knowledge Base

**36. Create a KB article**
```
Create a knowledge article in the IT Knowledge Base titled "How to connect
to the corporate VPN" with the following content:

1. Download the VPN client from the Self-Service Portal
2. Install and open the application
3. Enter the server address: vpn.company.com
4. Log in with your corporate credentials
5. Select "Full Tunnel" mode and click Connect
```

**37. Search and update an article**
```
Find knowledge articles about "password reset" and update the most
relevant one to include the new self-service portal URL:
https://reset.company.com.
```

**38. Publish an article**
```
Publish the knowledge article with sys_id abc123.
```

---

### Agile & Project Management

**39. Create an epic with stories**
```
Create an epic titled "Customer Portal Redesign". Then create three user
stories under it:
1. "As a customer, I want a new login page with SSO support"
2. "As a customer, I want to view my open tickets in a dashboard"
3. "As a customer, I want to submit requests via a mobile-friendly form"
```

**40. Create a scrum task**
```
Create a scrum task under story STY0010001 titled "Implement SSO
integration with Okta". Assign it to the Development team with an
estimate of 8 remaining hours.
```

**41. List projects**
```
List all active projects and their current state.
```

---

### Workflow & Script Management

**42. List workflows for a table**
```
Show me all workflows that run on the sc_req_item (request item) table.
```

**43. Create a script include**
```
Create a new Script Include called "DateUtils" with API name
"global.DateUtils" and this code:

var DateUtils = Class.create();
DateUtils.prototype = {
    initialize: function() {},
    isBusinessDay: function(date) {
        var day = date.getDay();
        return day !== 0 && day !== 6;
    },
    type: 'DateUtils'
};
```

**44. Find and update a script include**
```
Find the script include named "EmailHelper" and update its description
to "Utility for formatting and sending templated emails."
```

---

### Update Sets

**45. Create and manage an update set**
```
Create a new update set called "March 2026 - VPN Portal Fixes".
Then add the script include "VPNUtils" to it.
```

**46. List in-progress update sets**
```
Show me all update sets that are currently in progress, created by admin.
```

---

### Generic Table Operations & Analytics

**47. Query any table**
```
Get the 5 most recently created active change requests. Show only the
number, short description, state, and assigned_to fields.
```

**48. Get table schema**
```
What fields are available on the incident table? Show me their names
and types.
```

**49. Bulk update records**
```
Batch-update these 3 incidents to urgency Medium and add a work note
"Bulk reclassified per service review meeting":
- INC0010045
- INC0010052
- INC0010061
```

**50. Run an analytics query**
```
Give me a count of all active incidents grouped by priority. Then also
show me the average time to resolution for incidents closed this month,
grouped by category.
```

---

## 6. Tips for Writing Effective Prompts

### Be specific with identifiers
Instead of "update that incident", say "update incident INC0010001". Claude can look up records by number, sys_id, or name — but specificity avoids ambiguity.

### Chain operations naturally
You can ask for multi-step workflows in a single prompt:
> "Create an incident for the email outage, assign it to Network Ops, add a work note saying we're investigating, then check if there's a related problem record."

Claude will call multiple tools in sequence.

### Use ServiceNow query syntax when needed
For advanced filtering, you can include encoded queries:
> "List incidents where `active=true^priority=1^assignment_group.name=Network Operations`"

### Ask for summaries, not raw data
Instead of "list all incidents", try:
> "Summarize the top 5 critical incidents — who are they assigned to and how long have they been open?"

Claude will fetch the data and format a readable summary.

### Let Claude discover sys_ids
You don't need to know sys_ids. Just use names:
> "Assign incident INC0010001 to the 'Database Administration' group."

Claude will look up the group's sys_id automatically.

### Combine modules
The real power is cross-module prompts:
> "Find all breached SLAs, check which incidents they belong to, and create a problem record summarizing the pattern."

---

## 7. Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVICENOW_INSTANCE` | *(required)* | Your ServiceNow instance URL (e.g., `https://myco.service-now.com`) |
| `SERVICENOW_USERNAME` | *(required)* | API username |
| `SERVICENOW_PASSWORD` | *(required)* | API password |
| `SERVICENOW_VERIFY_SSL` | `true` | Set to `false` to disable SSL verification (dev only) |
| `API_TIMEOUT` | `30` | Request timeout in seconds |
| `MAX_RETRIES` | `3` | Max retry attempts for failed/rate-limited requests |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

---

## Quick Reference: All 19 Modules

| Module | Tools | Key Operations |
|--------|------:|----------------|
| Incident Management | 9 | Create, update, resolve, comment, search incidents |
| Change Management | 8 | Create, approve/reject, add tasks, lifecycle management |
| Problem Management | 5 | Create, update, list, mark as Known Error |
| Service Catalog | 11 | Browse catalogs, manage items, categories, form variables |
| Request Management | 5 | Create requests, comment, attach files |
| CMDB Management | 6 | CI classes, CRUD, relationships |
| SLA Management | 3 | Definitions, task SLAs, breach monitoring |
| User Management | 9 | Users, groups, membership CRUD |
| Knowledge Base | 8 | KBs, categories, articles, publish |
| Agile — Stories | 5 | Stories, dependencies |
| Agile — Epics | 3 | Epic CRUD |
| Agile — Scrum Tasks | 3 | Scrum task CRUD |
| Project Management | 3 | Project CRUD |
| Workflow Management | 5 | Workflow CRUD |
| Script Includes | 5 | Script Include CRUD |
| Update Sets | 7 | Update set lifecycle |
| UI Policies | 2 | UI policy and action creation |
| Table Management | 8 | Generic CRUD, schema, search, batch update |
| Analytics | 1 | Aggregation queries (COUNT, AVG, SUM, etc.) |
| **Total** | **106** | |

---

For the full tool reference with parameter details, see [TOOLS.md](TOOLS.md).
