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

        # Normalize answer for True/False questions
        answer = q.get("answer", "N/A")
        if isinstance(answer, (int, str)) and str(answer).lower() in [
            "0",
            "false",
            "f",
        ]:
            answer = "False"
        elif isinstance(answer, (int, str)) and str(answer).lower() in [
            "1",
            "true",
            "t",
        ]:
            answer = "True"

        output.append(f"  Answer: {answer}")

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
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, HRFlowable
    except ImportError:
        raise ImportError(
            "reportlab is required for PDF export. Install with: pip install reportlab"
        )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=1 * inch,
        leftMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=8,
        fontName="Helvetica-Bold",
    )

    date_style = ParagraphStyle(
        "DateStyle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=36,
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#2563eb"),
        spaceBefore=16,
        spaceAfter=8,
        fontName="Helvetica-Bold",
    )

    normal_style = ParagraphStyle(
        "CustomNormal",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#334155"),
        leading=16,  # Line height
        spaceAfter=8,
    )

    option_style = ParagraphStyle(
        "OptionStyle",
        parent=normal_style,
        leftIndent=24,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6,
    )

    meta_style = ParagraphStyle(
        "MetaStyle",
        parent=normal_style,
        fontSize=10,
        textColor=colors.HexColor("#475569"),
        leftIndent=12,
        spaceBefore=6,
        spaceAfter=6,
        borderPadding=8,
        backColor=colors.HexColor("#f8fafc"),
        borderColor=colors.HexColor("#e2e8f0"),
        borderWidth=1,
        borderRadius=4,
    )

    answer_style = ParagraphStyle(
        "AnswerStyle",
        parent=normal_style,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#059669"),
        spaceBefore=8,
    )

    explanation_style = ParagraphStyle(
        "ExplanationStyle",
        parent=normal_style,
        fontName="Helvetica-Oblique",
        textColor=colors.HexColor("#475569"),
        leftIndent=12,
        spaceBefore=4,
    )

    story = []

    # Title
    story.append(Paragraph("Exam Questions", title_style))
    story.append(
        Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            date_style,
        )
    )

    # Questions
    for i, q in enumerate(questions, 1):
        # Divider line in front of the question
        story.append(
            HRFlowable(
                width="100%",
                thickness=1.5,
                color=colors.HexColor("#cbd5e1"),
                spaceBefore=10,
                spaceAfter=14,
            )
        )

        story.append(Paragraph(f"Question {i}", heading_style))
        story.append(Paragraph(q.get("question", "N/A"), normal_style))

        if q.get("scenario"):
            story.append(
                Paragraph(f"<b>Scenario Context:</b><br/>{q['scenario']}", meta_style)
            )

        if q.get("concepts_tested"):
            story.append(
                Paragraph(
                    f"<b>Concepts:</b> {', '.join(q['concepts_tested'])}", meta_style
                )
            )

        if q.get("options"):
            story.append(Spacer(1, 0.05 * inch))
            for opt in q["options"]:
                story.append(Paragraph(f"•  {opt}", option_style))
            story.append(Spacer(1, 0.05 * inch))

        # Normalize answer for True/False questions
        answer = q.get("answer", "N/A")
        if isinstance(answer, (int, str)) and str(answer).lower() in [
            "0",
            "false",
            "f",
        ]:
            answer = "False"
        elif isinstance(answer, (int, str)) and str(answer).lower() in [
            "1",
            "true",
            "t",
        ]:
            answer = "True"

        story.append(Paragraph(f"Correct Answer: {answer}", answer_style))

        if q.get("explanation"):
            story.append(
                Paragraph(f"Explanation: {q['explanation']}", explanation_style)
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
    logger.info(
        f"Exporting {len(request.questions)} questions in {request.format} format"
    )

    if not request.questions:
        raise HTTPException(status_code=400, detail="No questions provided for export.")

    filename = (
        request.filename or f"exam_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

    try:
        if request.format == ExportFormat.JSON:
            json_bytes = json.dumps(request.questions, indent=2).encode("utf-8")
            return StreamingResponse(
                io.BytesIO(json_bytes),
                media_type="application/json",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}.json"'
                },
            )

        elif request.format == ExportFormat.TXT:
            content = _format_questions_txt(request.questions)
            return StreamingResponse(
                io.StringIO(content),
                media_type="text/plain",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}.txt"'
                },
            )

        elif request.format == ExportFormat.PDF:
            pdf_bytes = _generate_pdf_content(request.questions)
            return StreamingResponse(
                io.BytesIO(pdf_bytes),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}.pdf"'
                },
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
