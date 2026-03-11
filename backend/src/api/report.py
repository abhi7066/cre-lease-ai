from fastapi import Response
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.platypus import ListFlowable, ListItem
from reportlab.lib.styles import ListStyle
from reportlab.platypus import PageBreak
from io import BytesIO

from src.agents.report_agent import report_agent


def generate_report_endpoint(payload: dict):

    # --------------------------
    # Generate Report Text
    # --------------------------
    state = {
        "structured_data": payload["structured_data"],
        "sanity_flags": payload["sanity_flags"],
        "analytics_result": payload["analytics_result"]
    }

    result = report_agent(state)
    report_text = result.get("report_output", "No report generated.")

    # --------------------------
    # Create PDF in Memory
    # --------------------------
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    normal_style = styles["Normal"]

    # Title
    elements.append(Paragraph("Executive Lease Report", title_style))
    elements.append(Spacer(1, 0.3 * inch))

    # Body
    for line in report_text.split("\n"):
        elements.append(Paragraph(line, normal_style))
        elements.append(Spacer(1, 0.15 * inch))

    # Build PDF
    doc.build(elements)

    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=lease_report.pdf"
        },
    )