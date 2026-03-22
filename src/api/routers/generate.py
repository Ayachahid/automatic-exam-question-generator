from fastapi import APIRouter, Depends, HTTPException, status
from src.api.schemas.request import GenerateRequest
from src.api.schemas.response import GenerationResponse, QuestionResponse
from src.generation.pipeline import QuestionGenerationPipeline
from src.api.dependencies import get_pipeline

router = APIRouter()


@router.post("/", response_model=GenerationResponse)
async def generate_questions(
    request: GenerateRequest,
    pipeline: QuestionGenerationPipeline = Depends(get_pipeline),
):
    """
    Generate exam questions based on the provided file or text.
    """
    try:
        questions_data = pipeline.run(
            file_path=request.file_path,
            text=request.text,
            question_type=request.question_type.value,
            difficulty=request.difficulty.value,
            num_questions=request.num_questions,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline error: {str(e)}",
        )

    # Map dictionaries to Pydantic models
    questions = []
    for q_data in questions_data:
        try:
            questions.append(QuestionResponse(**q_data))
        except Exception as e:
            print(f"Validation error for question: {e}")
            continue

    return GenerationResponse(questions=questions, total=len(questions))
