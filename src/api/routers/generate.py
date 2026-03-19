import json
from fastapi import APIRouter, Depends, HTTPException, status
from src.api.schemas.request import GenerateRequest
from src.api.schemas.response import GenerationResponse, QuestionResponse
from src.generation.pipeline import QuestionGenerationPipeline
from src.api.dependencies import get_pipeline

router = APIRouter()

@router.post("/", response_model=GenerationResponse)
async def generate_questions(
    request: GenerateRequest,
    pipeline: QuestionGenerationPipeline = Depends(get_pipeline)
):
    """
    Generate exam questions based on the provided file or text.
    """
    try:
        # call the pipeline
        raw_results = pipeline.run(
            file_path=request.file_path,
            question_type=request.question_type.value,
            difficulty=request.difficulty.value,
            num_questions=request.num_questions
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {request.file_path}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline error: {str(e)}"
        )

    questions = []
    for raw_json in raw_results:
        try:
            # The LLM might return markdown code fences like ```json ... ```
            clean_json = raw_json.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]
            
            parsed_data = json.loads(clean_json)
            
            # parsed_data should be a list of objects based on the prompt
            if isinstance(parsed_data, list):
                for q_data in parsed_data:
                    questions.append(QuestionResponse(**q_data))
            elif isinstance(parsed_data, dict):
                questions.append(QuestionResponse(**parsed_data))
                
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {raw_json}") # Log error but continue
            continue
        except Exception as e:
             print(f"Validation error: {e}")
             continue

    return GenerationResponse(
        questions=questions,
        total=len(questions)
    )
