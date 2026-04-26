"""Generate a sample PDF design spec for testing the design-to-prd skill."""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    ListFlowable,
    ListItem,
)
import os

OUT = os.path.join(os.path.dirname(__file__), "expense-reports-design.pdf")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="H1Custom", parent=styles["Heading1"], spaceAfter=12))
styles.add(ParagraphStyle(name="H2Custom", parent=styles["Heading2"], spaceAfter=8))
styles.add(ParagraphStyle(name="Body", parent=styles["BodyText"], spaceAfter=8, leading=14))

doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.9*inch, rightMargin=0.9*inch, topMargin=0.9*inch, bottomMargin=0.9*inch)

story = []
P = lambda text, style="Body": story.append(Paragraph(text, styles[style]))
H1 = lambda text: P(text, "H1Custom")
H2 = lambda text: P(text, "H2Custom")
SP = lambda h=0.15: story.append(Spacer(1, h*inch))

H1("Expense Reports v3 — Design Specification")
P("<b>Designer:</b> Marcus Liu &nbsp;&nbsp; <b>Date:</b> April 15, 2026 &nbsp;&nbsp; <b>Status:</b> Ready for PRD")

H2("Overview")
P("This document covers the redesign of the Expense Reports module, focused on three pain points identified during Q1 customer research: (1) report submission takes too long because users have to re-categorize each receipt manually, (2) approvers can't tell at a glance which line items have been flagged by policy rules, and (3) admins have no clear way to see which reports are stuck and where.")
P("This design covers the submitter, approver, and admin flows. Implementation is expected over two milestones.")

H2("Target users")
P("<b>Primary — Submitters:</b> employees who file expense reports, typically 1–4 times per month. They want to file quickly and not think about it again. Most are on desktop but ~30% file from mobile while traveling.")
P("<b>Secondary — Approvers:</b> managers reviewing direct reports' submissions. They batch-process reviews 1–2 times per week and want to spot exceptions fast.")
P("<b>Tertiary — Admins:</b> finance / ops staff overseeing the queue. They need visibility into the full pipeline and tools to unblock stuck reports.")

H2("Problem context")
P("From the Q1 user research deck (8 customer interviews, 240 in-app survey responses):")
items = [
    "Submitters spend an average of 14 minutes per report, 60% of which is on receipt categorization.",
    "47% of approvers said they have missed a policy violation in the last quarter because flags weren't visible enough.",
    "Admins reported that ~12% of reports get stuck in 'awaiting approval' for more than 14 days.",
]
story.append(ListFlowable([ListItem(Paragraph(t, styles["Body"])) for t in items], bulletType="bullet"))
SP()

H2("Solution")
P("<b>Submitter flow.</b> When a submitter uploads a receipt, the system auto-categorizes it using a model trained on the user's prior submissions plus org-level rules. The user sees the predicted category inline and can override with one click. (See pp. 4–6.)")
P("<b>Approver flow.</b> The approver view groups line items by policy status — 'flagged', 'needs attention', 'clean' — instead of the current chronological list. Each flagged item shows the rule that flagged it inline. (See pp. 8–10.)")
P("<b>Admin flow.</b> A new 'pipeline' view shows every report's current state, time-in-state, and assigned approver, with one-click reassignment. (See pp. 12–14.)")

H2("Key flows")
P("<b>Flow A — Submitter files a typical report.</b> User clicks 'New report' → uploads receipts (drag-and-drop or photo) → system auto-categorizes → user reviews and submits. Target: under 4 minutes for a 5-receipt report.")
P("<b>Flow B — Submitter overrides a category.</b> User taps the predicted category chip → picks a new category from the menu → system records the override and learns from it for future predictions.")
P("<b>Flow C — Approver reviews a batch.</b> Approver opens 'Pending review' → sees reports grouped by flag status → approves clean items in bulk → handles flagged items individually with policy context inline.")
P("<b>Flow D — Admin reassigns a stuck report.</b> Admin opens pipeline view → filters by 'in state >7 days' → opens a stuck report → reassigns to a different approver with one click.")

H2("Out of scope")
items2 = [
    "Receipt OCR improvements (separate workstream owned by the Data team).",
    "Mileage tracking (deferred to v4).",
    "Currency conversion logic (covered by existing service, no changes needed).",
    "Mobile app updates for the admin pipeline view (web only in v3).",
]
story.append(ListFlowable([ListItem(Paragraph(t, styles["Body"])) for t in items2], bulletType="bullet"))
SP()

H2("Risks called out by design")
items3 = [
    "Auto-categorization confidence threshold needs tuning — if too aggressive, users will distrust it; if too conservative, we won't save them time.",
    "The pipeline view can leak information across departments; permissions need careful review.",
    "Bulk-approval UX needs an undo path; once approved, reversing is painful.",
]
story.append(ListFlowable([ListItem(Paragraph(t, styles["Body"])) for t in items3], bulletType="bullet"))
SP()

H2("Dependencies")
items4 = [
    "Categorization model from the ML team (target: ready in 6 weeks).",
    "Updated policy-rule engine (Platform team, in flight).",
    "Permissions framework update for the pipeline view (Security review required).",
]
story.append(ListFlowable([ListItem(Paragraph(t, styles["Body"])) for t in items4], bulletType="bullet"))
SP()

P("<i>End of design spec. Open questions for PM live in the linked review doc.</i>")

doc.build(story)
print(f"Wrote {OUT}")
