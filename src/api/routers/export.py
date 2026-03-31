import io
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from src.api.schemas.request import ExportRequest, ExportFormat
from src.core.logger import get_logger

logger = get_logger("api.routers.export")

router = APIRouter()


def _format_questions_txt(questions: list) -> str:
    """Format questions as plain text."""
    output = []
    output.append("=" * 60)
    output.append("GENERATED EXAM QUESTIONS")
    output.append(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("=" * 60)
    output.append("")

    for i, q in enumerate(questions, 1):
        output.append(f"Question {i}: {q.get('question', 'N/A')}")

        if q.get("scenario"):
            output.append(f"  Scenario: {q['scenario']}")

        if q.get("concepts_tested"):
            output.append(f"  Concepts: {', '.join(q['concepts_tested'])}")

        if q.get("options"):
            output.append("  Options:")
            for opt in q["options"]:
                output.append(f"    - {opt}")

        output.append(f"  Answer: {q.get('answer', 'N/A')}")

        if q.get("explanation"):
            output.append(f"  Explanation: {q['explanation']}")

        output.append("")
        output.append("-" * 60)
        output.append("")

    return "\n".join(output)


def _generate_pdf_content(questions: list) -> bytes:
    """Generate simple PDF content using reportlab."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError:
        raise ImportError(
            "reportlab is required for PDF export. Install with: pip install reportlab"
        )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=12,
        alignment=1,  # Center
    )
    normal_style = ParagraphStyle("CustomNormal", parent=styles["Normal"], fontSize=11)
    heading_style = ParagraphStyle(
        "CustomHeading", parent=styles["Heading2"], fontSize=13, spaceAfter=6
    )

    story = []

    # Title
    story.append(Paragraph("Generated Exam Questions", title_style))
    story.append(
        Paragraph(
            f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ParagraphStyle("DateStyle", parent=styles["Normal"], fontSize=9, alignment=1),
        )
    )
    story.append(Spacer(1, 0.25 * inch))

    # Questions
    for i, q in enumerate(questions, 1):
        story.append(Paragraph(f"Question {i}", heading_style))
        story.append(Paragraph(q.get("question", "N/A"), normal_style))

        if q.get("scenario"):
            story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph(f"<b>Scenario:</b> {q['scenario']}", normal_style))

        if q.get("concepts_tested"):
            story.append(
                Paragraph(
                    f"<b>Concepts tested:</b> {', '.join(q['concepts_tested'])}",
                    normal_style,
                )
            )

        if q.get("options"):
            story.append(Spacer(1, 0.1 * inch))
            options_data = [[opt] for opt in q["options"]]
            options_table = Table(options_data, colWidths=[5 * inch])
            options_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            story.append(options_table)

        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph(f"<b>Answer:</b> {q.get('answer', 'N/A')}", normal_style))

        if q.get("explanation"):
            story.append(Spacer(1, 0.1 * inch))
            story.append(
                Paragraph(f"<b>Explanation:</b> {q['explanation']}", normal_style)
            )

        story.append(Spacer(1, 0.2 * inch))

    doc.build(story)
    return buffer.getvalue()


@router.post("/", tags=["Export"])
async def export_questions(request: ExportRequest):
    """
    Export generated questions in various formats (JSON, PDF, TXT).

    - **questions**: List of question objects to export
    - **format**: Desired export format (json, pdf, txt)
    - **filename**: Optional custom filename
    """
    logger.info(f"Exporting {len(request.questions)} questions in {request.format} format")

    if not request.questions:
        raise HTTPException(status_code=400, detail="No questions provided for export.")

    filename = request.filename or f"exam_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    try:
        if request.format == ExportFormat.JSON:
            json_bytes = json.dumps(request.questions, indent=2).encode("utf-8")
            return StreamingResponse(
                io.BytesIO(json_bytes),
                media_type="application/json",
                headers={"Content-Disposition": f'attachment; filename="{filename}.json"'},
            )

        elif request.format == ExportFormat.TXT:
            content = _format_questions_txt(request.questions)
            return StreamingResponse(
                io.StringIO(content),
                media_type="text/plain",
                headers={"Content-Disposition": f'attachment; filename="{filename}.txt"'},
            )

        elif request.format == ExportFormat.PDF:
            pdf_bytes = _generate_pdf_content(request.questions)
            return StreamingResponse(
                io.BytesIO(pdf_bytes),
                media_type="application/pdf",
                headers={"Content-Disposition": f'attachment; filename="{filename}.pdf"'},
            )

    except ImportError as e:
        logger.error(f"Missing dependency for export: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Export feature unavailable: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

    raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")
