from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from backend.src.database import get_session
# from backend.src.models.progress import Progress
# from backend.src.models.user import User
from backend.src.models.models import Progress, User
from backend.src.models.word import WordProgress
from backend.src.routers.auth import get_current_user

router = APIRouter(
    prefix="/api/progress",
    tags=["Progress"],
    responses={404: {"description": "Not found"}}
)

@router.post("/session", response_model=Progress)
async def record_study_session(
    duration_seconds: int,
    words_learned: int,
    accuracy: float,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Запись учебной сессии"""
    if not (0 <= accuracy <= 1):
        raise HTTPException(status_code=400, detail="Accuracy must be between 0 and 1")
    
    progress = Progress(
        user_id=current_user.id,
        duration_seconds=duration_seconds,
        words_learned=words_learned,
        accuracy=accuracy
    )
    
    session.add(progress)
    session.commit()
    session.refresh(progress)
    return progress

@router.get("/stats", response_model=List[Progress])
async def get_progress_stats(
    days: int = 7,  # Статистика за последние X дней
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Получение статистики за период"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = select(Progress).where(
        Progress.user_id == current_user.id,
        Progress.session_start >= start_date
    )
    
    result = session.exec(query)
    return result.all()

@router.get("/summary")
async def get_summary_stats(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Сводная статистика"""
    query = select(Progress).where(Progress.user_id == current_user.id)
    all_sessions = session.exec(query).all()
    
    if not all_sessions:
        return {
            "total_time": 0,
            "total_words": 0,
            "average_accuracy": 0
        }
    
    total_time = sum(s.duration_seconds for s in all_sessions)
    total_words = sum(s.words_learned for s in all_sessions)
    avg_accuracy = sum(s.accuracy for s in all_sessions) / len(all_sessions)
    
    return {
        "total_time": total_time,
        "total_words": total_words,
        "average_accuracy": round(avg_accuracy, 2)
    }


@router.put("/progress/{word_id}")
async def update_progress(
    word_id: int,
    is_correct: bool,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    progress = session.exec(
        select(WordProgress)
        .where(WordProgress.word_id == word_id)
        .where(WordProgress.user_id == current_user.id)
    ).first()

    if not progress:
        progress = WordProgress(
            word_id=word_id,
            user_id=current_user.id,
            shown_count=1,
            correct_count=1 if is_correct else 0,
            error_count=0 if is_correct else 1
        )
        session.add(progress)
    else:
        progress.shown_count += 1
        if is_correct:
            progress.correct_count += 1
        else:
            progress.error_count += 1

    session.commit()
    return {"status": "success"}
