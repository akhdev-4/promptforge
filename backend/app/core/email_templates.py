"""Branded HTML email templates.

Email clients are not browsers: no flexbox/grid, unreliable ``<style>`` blocks,
and images are often blocked by default. So these templates use table-based
layout with inline CSS, keep the logo decorative (the wordmark is live text, so
the brand still reads with images off), and always ship a plain-text
alternative alongside the HTML.
"""

from __future__ import annotations

from html import escape

from app.core.config import settings

# Brand palette (mirrors the app's primary violet).
_VIOLET = "#7c3aed"
_INK = "#18181b"
_MUTED = "#71717a"
_BORDER = "#e4e4e7"
_CANVAS = "#f4f4f5"
_FONT = "Segoe UI,Roboto,Helvetica,Arial,sans-serif"


def _logo_url() -> str:
    return f"{settings.FRONTEND_URL.rstrip('/')}/promptforge-logo.png"


def render_email(
    *,
    heading: str,
    preheader: str,
    body_html: str,
    cta_label: str | None = None,
    cta_url: str | None = None,
    footer_note: str | None = None,
) -> str:
    """Wrap ``body_html`` in the branded PromptForge shell.

    ``preheader`` is the snippet shown next to the subject in most inboxes; it's
    hidden inside the message itself.
    """
    button = ""
    fallback = ""
    if cta_label and cta_url:
        # Table-based button so Outlook renders the background reliably.
        button = f"""
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:28px 0;">
          <tr>
            <td align="center" bgcolor="{_VIOLET}" style="border-radius:10px;">
              <a href="{cta_url}"
                 style="display:inline-block;padding:13px 28px;font-family:{_FONT};
                        font-size:15px;font-weight:600;color:#ffffff;
                        text-decoration:none;border-radius:10px;">
                {escape(cta_label)}
              </a>
            </td>
          </tr>
        </table>"""
        fallback = f"""
        <p style="margin:0 0 4px;font-size:13px;color:{_MUTED};">
          Or paste this link into your browser:
        </p>
        <p style="margin:0 0 8px;font-size:13px;word-break:break-all;">
          <a href="{cta_url}" style="color:{_VIOLET};">{escape(cta_url)}</a>
        </p>"""

    note = (
        f'<p style="margin:20px 0 0;font-size:13px;line-height:20px;color:{_MUTED};">{footer_note}</p>'
        if footer_note
        else ""
    )

    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <meta name="color-scheme" content="light">
    <title>{escape(heading)}</title>
  </head>
  <body style="margin:0;padding:0;background:{_CANVAS};">
    <!-- Inbox preview text, hidden in the body itself. -->
    <div style="display:none;max-height:0;overflow:hidden;opacity:0;">{escape(preheader)}</div>

    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
           style="background:{_CANVAS};padding:32px 12px;">
      <tr>
        <td align="center">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                 style="max-width:560px;background:#ffffff;border:1px solid {_BORDER};
                        border-radius:14px;overflow:hidden;">

            <!-- Brand header -->
            <tr>
              <td style="padding:24px 32px;border-bottom:1px solid {_BORDER};">
                <table role="presentation" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td style="padding-right:10px;" valign="middle">
                      <img src="{_logo_url()}" width="32" height="34" alt=""
                           style="display:block;border:0;outline:none;">
                    </td>
                    <td valign="middle"
                        style="font-family:{_FONT};font-size:19px;font-weight:700;
                               color:{_INK};letter-spacing:-0.2px;">
                      PromptForge
                    </td>
                  </tr>
                </table>
              </td>
            </tr>

            <!-- Content -->
            <tr>
              <td style="padding:32px;font-family:{_FONT};color:{_INK};">
                <h1 style="margin:0 0 14px;font-size:21px;line-height:28px;font-weight:700;color:{_INK};">
                  {escape(heading)}
                </h1>
                {body_html}
                {button}
                {fallback}
              </td>
            </tr>

            <!-- Footer -->
            <tr>
              <td style="padding:18px 32px 24px;border-top:1px solid {_BORDER};
                         font-family:{_FONT};">
                {note}
                <p style="margin:12px 0 0;font-size:12px;line-height:18px;color:{_MUTED};">
                  Sent by <a href="{settings.FRONTEND_URL}" style="color:{_MUTED};">PromptForge</a>
                  — the home for production-tested AI prompts.
                </p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""


def team_invite_email(
    *, team_name: str, inviter: str, link: str, expires_days: int
) -> tuple[str, str, str]:
    """Build the team invitation email. Returns ``(subject, text, html)``."""
    subject = f"{inviter} invited you to join {team_name} on PromptForge"

    text = (
        f"{inviter} invited you to join the team \"{team_name}\" on PromptForge.\n\n"
        f"Accept the invitation:\n{link}\n\n"
        "Joining gives you access to the team's private prompts.\n"
        "If you don't have an account yet, sign up with this email address and "
        "you'll join the team automatically.\n\n"
        f"This invitation expires in {expires_days} days. "
        "If you weren't expecting it, you can safely ignore this email."
    )

    body_html = f"""
                <p style="margin:0 0 14px;font-size:15px;line-height:23px;">
                  <strong>{escape(inviter)}</strong> invited you to join the team
                  <strong>{escape(team_name)}</strong> on PromptForge.
                </p>
                <p style="margin:0;font-size:15px;line-height:23px;color:{_MUTED};">
                  Joining gives you access to this team's private prompts. If you don't
                  have an account yet, sign up with this email address and you'll join
                  the team automatically.
                </p>"""

    html = render_email(
        heading=f"Join {team_name}",  # render_email escapes the heading
        preheader=f"{inviter} invited you to join {team_name} on PromptForge.",
        body_html=body_html,
        cta_label="Accept invitation",
        cta_url=link,
        footer_note=(
            f"This invitation expires in {expires_days} days. "
            "If you weren't expecting it, you can safely ignore this email."
        ),
    )
    return subject, text, html
