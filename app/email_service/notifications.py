"""
Email Notification Service for IT Ticketing System.
Uses Microsoft Graph API (OAuth2 client credentials) instead of SMTP.
"""

import requests
from flask import current_app, render_template

from app.models import Ticket

# ---------------------------------------------------------------------------
# Graph API helpers
# ---------------------------------------------------------------------------

_GRAPH_TOKEN_URL = 'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
_GRAPH_SEND_URL  = 'https://graph.microsoft.com/v1.0/users/{sender}/sendMail'


def _get_access_token() -> str | None:
    """
    Fetch a fresh OAuth2 access token using client credentials flow.
    Returns the token string, or None on failure.
    """
    tenant_id     = current_app.config.get('AZURE_TENANT_ID')
    client_id     = current_app.config.get('AZURE_CLIENT_ID')
    client_secret = current_app.config.get('AZURE_CLIENT_SECRET')

    if not all([tenant_id, client_id, client_secret]):
        current_app.logger.warning('[Email] Azure credentials not fully configured.')
        return None

    try:
        resp = requests.post(
            _GRAPH_TOKEN_URL.format(tenant_id=tenant_id),
            data={
                'grant_type':    'client_credentials',
                'client_id':     client_id,
                'client_secret': client_secret,
                'scope':         'https://graph.microsoft.com/.default',
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json().get('access_token')
    except Exception as e:
        current_app.logger.error(f'[Email] Failed to obtain access token: {e}')
        return None


def _send_via_graph(subject: str, recipients: list[str],
                    html_body: str, plain_body: str) -> bool:
    """
    Send an email via Microsoft Graph API.
    Returns True on success, False on failure.
    """
    token = _get_access_token()
    if not token:
        return False

    sender_email = current_app.config.get('MAIL_SENDER_EMAIL', 'support@company.com')
    sender_name  = current_app.config.get('MAIL_SENDER_NAME',  'Demo Company')

    payload = {
        'message': {
            'subject': subject,
            'body': {
                'contentType': 'HTML',
                'content':     html_body,
            },
            'from': {
                'emailAddress': {
                    'address': sender_email,
                    'name':    sender_name,
                }
            },
            'toRecipients': [
                {'emailAddress': {'address': addr}} for addr in recipients
            ],
        },
        'saveToSentItems': True,
    }

    try:
        resp = requests.post(
            _GRAPH_SEND_URL.format(sender=sender_email),
            json=payload,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type':  'application/json',
            },
            timeout=15,
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        current_app.logger.error(f'[Email] Graph API send failed: {e}')
        return False


# ---------------------------------------------------------------------------
# Public notification functions
# ---------------------------------------------------------------------------

def send_ticket_raised_email(ticket: Ticket):
    """
    Notify itadmin@company.com when a new ticket is raised.
    Fails silently — never crashes the app.
    """
    try:
        html_body = render_template('email/ticket_raised.html', ticket=ticket)
        plain_body = _build_raised_plain_text_body(ticket)

        success = _send_via_graph(
            subject    = f'[IT Support] New Ticket Raised — {ticket.ticket_ref} [{ticket.priority.value} Priority]',
            recipients = ['itadmin@company.com'],
            html_body  = html_body,
            plain_body = plain_body,
        )

        if success:
            current_app.logger.info(
                f'[Email] New-ticket notification sent for {ticket.ticket_ref} '
                f'to itadmin@company.com'
            )
        else:
            current_app.logger.warning(
                f'[Email] New-ticket notification failed for {ticket.ticket_ref}'
            )

    except Exception as e:
        current_app.logger.error(
            f'[Email] Unexpected error sending new-ticket notification '
            f'for {ticket.ticket_ref}: {e}'
        )


def send_ticket_solved_email(ticket: Ticket):
    """
    Send a resolution confirmation email to the ticket submitter.
    Fails silently — never crashes the app.
    """
    try:
        html_body  = render_template('email/ticket_solved.html', ticket=ticket)
        plain_body = _build_solved_plain_text_body(ticket)

        success = _send_via_graph(
            subject    = f'[IT Support] Your Ticket {ticket.ticket_ref} Has Been Resolved',
            recipients = [ticket.submitter_email],
            html_body  = html_body,
            plain_body = plain_body,
        )

        if success:
            current_app.logger.info(
                f'[Email] Resolution email sent for {ticket.ticket_ref} '
                f'to {ticket.submitter_email}'
            )
        else:
            current_app.logger.warning(
                f'[Email] Resolution email failed for {ticket.ticket_ref}'
            )

    except Exception as e:
        current_app.logger.error(
            f'[Email] Unexpected error sending resolution email '
            f'for {ticket.ticket_ref}: {e}'
        )


# ---------------------------------------------------------------------------
# Plain-text fallback builders
# ---------------------------------------------------------------------------

def _build_raised_plain_text_body(ticket: Ticket) -> str:
    submitted_at_str = (
        ticket.submitted_at.strftime('%d %b %Y at %H:%M UTC')
        if ticket.submitted_at else 'N/A'
    )
    return f"""
New IT Support Ticket Raised

────────────────────────────────────
TICKET DETAILS
────────────────────────────────────
Reference   : {ticket.ticket_ref}
Priority    : {ticket.priority.value}
Category    : {ticket.category.value if ticket.category else 'N/A'}
Sub-Category: {ticket.sub_category or '—'}
Asset ID    : {ticket.asset_id or '—'}
Submitted   : {submitted_at_str}

Raised By   : {ticket.submitter_name}
Employee ID : {ticket.submitter_employee_id}
Department  : {ticket.submitter_department}
Email       : {ticket.submitter_email}

Problem Description:
{ticket.problem_description}
────────────────────────────────────

Please log in to the IT Support portal to assign and action this ticket.

IT Support Support System
    """.strip()


def _build_solved_plain_text_body(ticket: Ticket) -> str:
    solved_by_name = ticket.solved_by.full_name if ticket.solved_by else 'IT Team'
    solved_at_str  = (
        ticket.solved_at.strftime('%d %b %Y at %H:%M UTC')
        if ticket.solved_at else 'N/A'
    )
    return f"""
Dear {ticket.submitter_name},

Your IT support ticket has been resolved.

────────────────────────────────────
TICKET DETAILS
────────────────────────────────────
Reference   : {ticket.ticket_ref}
Priority    : {ticket.priority.value}
Submitted   : {ticket.submitted_at.strftime('%d %b %Y at %H:%M UTC')}
Resolved On : {solved_at_str}
Resolved By : {solved_by_name}

Your Issue:
{ticket.problem_description}

Resolution:
{ticket.resolution_remark}
────────────────────────────────────

If your issue persists, please submit a new ticket at the IT Support portal.

Regards,
IT Support Support Team
    """.strip()
