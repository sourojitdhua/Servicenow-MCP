# src/servicenow_mcp_server/prompts.py

"""MCP prompt templates for common ServiceNow workflows."""

from typing import Optional
from fastmcp import FastMCP


def register_prompts(mcp: FastMCP):
    """Register all prompt templates on the server."""

    @mcp.prompt()
    def triage_incident(
        incident_number: Optional[str] = None,
        incident_sys_id: Optional[str] = None,
    ) -> str:
        """Guide for triaging and routing a ServiceNow incident."""
        identifier = ""
        if incident_number:
            identifier = f"Look up incident **{incident_number}** using `get_incident_by_number`."
        elif incident_sys_id:
            identifier = f"Look up incident sys_id **{incident_sys_id}** using `get_incident`."
        else:
            identifier = "Ask the user for an incident number or sys_id, then retrieve it."

        return (
            f"{identifier}\n\n"
            "Then follow these triage steps:\n"
            "1. Review the short_description, description, and any comments/work_notes.\n"
            "2. Assess the urgency and impact — suggest adjustments if they seem wrong.\n"
            "3. Identify the correct assignment_group based on the category and CI involved.\n"
            "4. If a Knowledge Base article exists for this issue, reference it.\n"
            "5. Summarise your triage findings and recommended next actions."
        )

    @mcp.prompt()
    def create_change_workflow(
        change_type: str = "Normal",
        short_description: Optional[str] = None,
    ) -> str:
        """Step-by-step guide for creating a change request with tasks and approval."""
        desc_hint = ""
        if short_description:
            desc_hint = f' Use this as the short_description: "{short_description}".'

        return (
            f"Create a **{change_type}** change request.{desc_hint}\n\n"
            "Follow these steps:\n"
            "1. Call `create_change_request` with appropriate fields (description, impact, urgency, justification, dates).\n"
            "2. Add at least one change task via `add_change_task` describing the implementation work.\n"
            "3. Submit the change for approval via `submit_change_for_approval`.\n"
            "4. Report back the change number and current state."
        )

    @mcp.prompt()
    def investigate_ci_impact(
        ci_name: Optional[str] = None,
        ci_sys_id: Optional[str] = None,
    ) -> str:
        """Analyse the impact of a Configuration Item outage using CMDB relationships."""
        lookup = ""
        if ci_sys_id:
            lookup = f"Retrieve CI details with `get_ci` (sys_id={ci_sys_id})."
        elif ci_name:
            lookup = f'Search for the CI named "{ci_name}" using `list_cis` with a query filter.'
        else:
            lookup = "Ask the user for a CI name or sys_id, then retrieve it."

        return (
            f"{lookup}\n\n"
            "Then perform an impact analysis:\n"
            "1. Use `get_ci_relationships` to find upstream and downstream CIs.\n"
            "2. For each related CI, check if there are open incidents (`list_incidents` with a CI query).\n"
            "3. Check active SLAs on related tasks via `get_task_sla`.\n"
            "4. Summarise the blast radius: which services, users, and SLAs are affected."
        )

    @mcp.prompt()
    def onboard_user(
        first_name: str = "",
        last_name: str = "",
        email: str = "",
        department: Optional[str] = None,
    ) -> str:
        """New-user onboarding workflow: create account, add to groups, open request."""
        return (
            f"Onboard a new user: **{first_name} {last_name}** ({email}).\n\n"
            "Steps:\n"
            f"1. Create the user via `create_user` (first_name, last_name, email, department={department or 'ask user'}).\n"
            "2. Ask which groups the user should join, then call `add_group_members` for each.\n"
            "3. Open an onboarding service request via `create_request_ticket` summarising what was provisioned.\n"
            "4. Report the new user sys_id, groups added, and request number."
        )

    @mcp.prompt()
    def weekly_incident_report(
        assignment_group: Optional[str] = None,
    ) -> str:
        """Generate a weekly incident summary report using analytics and listing tools."""
        group_filter = ""
        if assignment_group:
            group_filter = f"^assignment_group={assignment_group}"

        return (
            "Generate a weekly incident report.\n\n"
            "1. Use `get_aggregate_data` on the **incident** table:\n"
            f"   - COUNT grouped by **priority** (query: 'sys_created_on>=javascript:gs.daysAgoStart(7){group_filter}').\n"
            f"   - COUNT grouped by **state** (same date filter).\n"
            "2. Use `list_recent_incidents` (limit=20) for a quick glance at the latest incidents.\n"
            "3. Use `list_breached_slas` to find any SLA breaches in the period.\n"
            "4. Compile the results into a markdown report with:\n"
            "   - Total new incidents this week\n"
            "   - Breakdown by priority and state\n"
            "   - Any SLA breaches\n"
            "   - Top 5 most recent incidents with number, description, and priority."
        )
