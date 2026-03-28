from pathlib import Path
from .base import BaseExporter
from src.core.logger import get_logger

logger = get_logger("export.pdf")


try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        HRFlowable,
    )
    from reportlab.lib.enums import TA_CENTER

    BLUE_DARK = colors.HexColor("#1F497D")
    BLUE_MID = colors.HexColor("#2E75B6")
    GREY = colors.HexColor("#707070")
    LIGHT_BG = colors.HexColor("#F2F7FC")

    _REPORTLAB_AVAILABLE = True

except ImportError:
    _REPORTLAB_AVAILABLE = False
    BLUE_DARK = BLUE_MID = GREY = LIGHT_BG = None


class PDFExporter(BaseExporter):
    """
    Exports questions to a clean, styled PDF using ReportLab.

    Handles all question types:
        - Multiple Choice  (bulleted options)
        - True / False
        - Short Answer
        - Essay
        - Scenario-Based   (scenario + concepts_tested)

    Requires:
        pip install reportlab
        (add `reportlab>=4.0.0` to pyproject.toml dependencies)
    """

    def export(self, questions: list[dict], output_path: str) -> str:
        """
        Build and save a PDF from a list of question dicts.

        Args:
            questions:    List of question dicts (pipeline output).
            output_path:  Destination .pdf file path.

        Returns:
            Absolute path to the exported file.

        Raises:
            ImportError:  If reportlab is not installed.
        """
        if not _REPORTLAB_AVAILABLE:
            raise ImportError(
                "reportlab is required for PDF export. "
                "Run: pip install reportlab  (add reportlab>=4.0.0 to pyproject.toml)"
            )

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(path),
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        styles = self._build_styles()
        story = self._build_story(questions, styles)

        doc.build(story)
        logger.info(f"[PDFExporter] Exported {len(questions)} questions → {path}")
        return str(path.absolute())

    def _build_styles(self) -> dict:
        """Create and return a dict of named ParagraphStyles."""
        base = getSampleStyleSheet()

        return {
            "title": ParagraphStyle(
                "DocTitle",
                parent=base["Title"],
                fontSize=20,
                textColor=BLUE_DARK,
                spaceAfter=6,
                alignment=TA_CENTER,
            ),
            "subtitle": ParagraphStyle(
                "DocSubtitle",
                parent=base["Normal"],
                fontSize=10,
                textColor=GREY,
                spaceAfter=14,
                alignment=TA_CENTER,
            ),
            "q_num": ParagraphStyle(
                "QuestionNum",
                parent=base["Normal"],
                fontSize=12,
                textColor=BLUE_MID,
                fontName="Helvetica-Bold",
                spaceBefore=10,
                spaceAfter=4,
            ),
            "q_text": ParagraphStyle(
                "QuestionText",
                parent=base["Normal"],
                fontSize=11,
                textColor=colors.black,
                spaceAfter=6,
            ),
            "label": ParagraphStyle(
                "Label",
                parent=base["Normal"],
                fontSize=10,
                textColor=GREY,
                fontName="Helvetica-Bold",
                spaceAfter=2,
            ),
            "body": ParagraphStyle(
                "Body",
                parent=base["Normal"],
                fontSize=10,
                textColor=colors.black,
                spaceAfter=4,
                leftIndent=10,
            ),
            "scenario": ParagraphStyle(
                "Scenario",
                parent=base["Normal"],
                fontSize=10,
                textColor=colors.black,
                backColor=LIGHT_BG,
                borderPad=6,
                spaceAfter=6,
                leftIndent=10,
                rightIndent=10,
            ),
            "option": ParagraphStyle(
                "Option",
                parent=base["Normal"],
                fontSize=10,
                textColor=colors.black,
                spaceAfter=2,
                leftIndent=20,
            ),
        }

    def _build_story(self, questions: list[dict], styles: dict) -> list:
        """Build the full ReportLab flowable list."""
        story = []

        story.append(Paragraph("📝  Exam Question Bank", styles["title"]))
        story.append(
            Paragraph(f"Total questions: {len(questions)}", styles["subtitle"])
        )
        story.append(HRFlowable(width="100%", thickness=1, color=BLUE_DARK))
        story.append(Spacer(1, 0.4 * cm))

        for idx, q in enumerate(questions, start=1):
            story.extend(self._build_question_block(idx, q, styles))

        return story

    def _build_question_block(self, idx: int, q: dict, styles: dict) -> list:
        """Return a list of flowables for a single question."""
        block = []
        letters = ["A", "B", "C", "D", "E"]

        block.append(Paragraph(f"Question {idx}", styles["q_num"]))
        block.append(Paragraph(q.get("question", ""), styles["q_text"]))

        if q.get("scenario"):
            block.append(Paragraph("Scenario:", styles["label"]))
            block.append(Paragraph(q["scenario"], styles["scenario"]))

        if q.get("options"):
            block.append(Paragraph("Options:", styles["label"]))
            for i, opt in enumerate(q["options"]):
                letter = letters[i] if i < len(letters) else str(i + 1)
                block.append(Paragraph(f"{letter}.  {opt}", styles["option"]))

        block.append(Paragraph("Answer:", styles["label"]))
        block.append(Paragraph(str(q.get("answer", "")), styles["body"]))

        if q.get("explanation"):
            block.append(Paragraph("Explanation:", styles["label"]))
            block.append(Paragraph(q["explanation"], styles["body"]))

        if q.get("concepts_tested"):
            block.append(Paragraph("Concepts tested:", styles["label"]))
            block.append(Paragraph(", ".join(q["concepts_tested"]), styles["body"]))

        block.append(Spacer(1, 0.2 * cm))
        block.append(HRFlowable(width="100%", thickness=0.5, color=GREY))
        block.append(Spacer(1, 0.3 * cm))

        return block
