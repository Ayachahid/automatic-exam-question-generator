from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List
from src.api.schemas.kb import (
    IndexRequest,
    IndexResponse,
    RAGGenerateRequest,
    KBResetResponse,
)
from src.api.schemas.response import GenerationResponse, QuestionResponse
from src.generation.rag_pipeline import RAGQuestionGenerationPipeline
from src.api.dependencies import get_rag_pipeline
from src.core.logger import get_logger

router = APIRouter()
logger = get_logger("api.kb")


@router.post("/index", response_model=IndexResponse)
async def index_documents(
    request: IndexRequest,
    background_tasks: BackgroundTasks,
    pipeline: RAGQuestionGenerationPipeline = Depends(get_rag_pipeline),
):
    """
    Index multiple files into the knowledge base in the background.
    """
    logger.info(f"Index request for {len(request.file_paths)} files")
    try:
        background_tasks.add_task(pipeline.index_files, request.file_paths)
        return IndexResponse(
            message="Successfully indexed documents",
            indexed_files=request.file_paths,
            total_chunks=0,  # We could track this if needed
        )
    except Exception as e:
        logger.error(f"Indexing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Indexing error: {str(e)}",
        )


@router.post("/generate", response_model=GenerationResponse)
async def generate_rag_questions(
    request: RAGGenerateRequest,
    pipeline: RAGQuestionGenerationPipeline = Depends(get_rag_pipeline),
):
    """
    Generate questions based on a query using retrieved context.
    """
    logger.info(f"RAG Generation request for query: '{request.query}'")
    try:
        questions_data = pipeline.run_rag(
            query=request.query,
            question_type=request.question_type.value,
            difficulty=request.difficulty.value,
            num_questions=request.num_questions,
            n_results=request.n_results,
        )

        questions = [QuestionResponse(**q) for q in questions_data]
        return GenerationResponse(questions=questions, total=len(questions))
    except Exception as e:
        logger.error(f"RAG Generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG Generation error: {str(e)}",
        )


@router.post("/reset", response_model=KBResetResponse)
async def reset_kb(pipeline: RAGQuestionGenerationPipeline = Depends(get_rag_pipeline)):
    """
    Reset the knowledge base.
    """
    logger.warning("KB Reset requested")
    try:
        pipeline.vector_store.reset()
        return KBResetResponse(message="Knowledge base successfully reset")
    except Exception as e:
        logger.error(f"Reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reset error: {str(e)}",
        )


@router.get("/files", response_model=List[str])
async def list_files(
    pipeline: RAGQuestionGenerationPipeline = Depends(get_rag_pipeline),
):
    """
    List unique files currently indexed in the knowledge base.
    """
    try:
        return pipeline.vector_store.list_indexed_files()
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing files: {str(e)}",
        )
