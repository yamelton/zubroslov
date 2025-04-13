from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import json

from ..database import get_async_session
from ..models.models import Progress, User
from ..models.word import WordProgress, UserWordEvent, Word
from ..auth.router import current_active_user

router = APIRouter(
    prefix="/api/progress",
    tags=["Progress"],
    responses={404: {"description": "Not found"}}
)

@router.post("/session", response_model=dict)
async def record_study_session(
    duration_seconds: int,
    words_learned: int,
    accuracy: float,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
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
    await session.commit()
    await session.refresh(progress)
    
    return {
        "id": progress.id,
        "user_id": progress.user_id,
        "duration_seconds": duration_seconds,
        "words_learned": words_learned,
        "accuracy": accuracy
    }

@router.get("/stats", response_model=List[dict])
async def get_progress_stats(
    days: int = 7,  # Статистика за последние X дней
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    """Получение статистики за период"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = select(Progress).where(
        Progress.user_id == current_user.id,
        Progress.session_start >= start_date
    )
    
    result = await session.execute(query)
    progress_list = result.scalars().all()
    
    return [
        {
            "id": p.id,
            "user_id": p.user_id,
            "duration_seconds": p.duration_seconds,
            "words_learned": p.words_learned,
            "accuracy": p.accuracy
        } for p in progress_list
    ]

@router.get("/summary")
async def get_summary_stats(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    """Сводная статистика"""
    query = select(Progress).where(Progress.user_id == current_user.id)
    result = await session.execute(query)
    all_sessions = result.scalars().all()
    
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
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    query = select(WordProgress).where(
        WordProgress.word_id == word_id,
        WordProgress.user_id == current_user.id
    )
    result = await session.execute(query)
    progress = result.scalars().first()

    if not progress:
        progress = WordProgress(
            word_id=word_id,
            user_id=current_user.id,
            shown_count=1,  # This is set to 1 because the word has already been shown
            correct_count=1 if is_correct else 0,
            error_count=0 if is_correct else 1,
            last_shown_position=current_user.words_shown_counter,
            exp_error_rate=0.0 if is_correct else 1.0  # Initial value based on first answer
        )
        session.add(progress)
    else:
        # Don't increment shown_count here, it's already incremented in get_next_word
        # progress.shown_count += 1  # This line was causing double counting
        if is_correct:
            progress.correct_count += 1
            # Update exponential error rate (decrease if correct)
            result_value = 0  # 0 for correct answer
        else:
            progress.error_count += 1
            # Update exponential error rate (increase if incorrect)
            result_value = 1  # 1 for incorrect answer
            
        # Update exponential error rate
        progress.exp_error_rate = (result_value + progress.exp_error_rate) / 2
    
    # Запись события ответа пользователя
    word_event = UserWordEvent(
        user_id=current_user.id,
        word_id=word_id,
        event_type="answered",
        is_correct=is_correct
    )
    session.add(word_event)

    await session.commit()
    return {"status": "success"}

@router.get("/events", response_model=List[dict])
async def get_user_word_events(
    limit: int = Query(100, gt=0),
    offset: int = Query(0, ge=0),
    word_id: Optional[int] = None,
    event_type: Optional[str] = None,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    """Получение истории событий взаимодействия со словами"""
    query = select(UserWordEvent).where(
        UserWordEvent.user_id == current_user.id
    )
    
    # Применяем фильтры, если они указаны
    if word_id is not None:
        query = query.where(UserWordEvent.word_id == word_id)
    
    if event_type is not None:
        query = query.where(UserWordEvent.event_type == event_type)
    
    # Сортировка по времени (сначала новые)
    query = query.order_by(UserWordEvent.timestamp.desc())
    
    # Пагинация
    query = query.offset(offset).limit(limit)
    
    result = await session.execute(query)
    events = result.scalars().all()
    
    # Получаем информацию о словах для отображения
    word_ids = [e.word_id for e in events]
    words_query = select(Word).where(Word.id.in_(word_ids))
    words_result = await session.execute(words_query)
    words = {w.id: w for w in words_result.scalars().all()}
    
    return [
        {
            "id": e.id,
            "word_id": e.word_id,
            "word": {
                "english": words[e.word_id].english if e.word_id in words else None,
                "russian": words[e.word_id].russian if e.word_id in words else None
            },
            "event_type": e.event_type,
            "is_correct": e.is_correct,
            "timestamp": e.timestamp,
            "metadata": json.loads(e.event_data) if e.event_data else None
        } for e in events
    ]

@router.get("/activity-calendar")
async def get_activity_calendar(
    days: int = 365,  # Период для календаря (по умолчанию год)
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    """Получение данных для календаря активности"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Определяем тип базы данных по URL
    from ..database import DATABASE_URL
    
    # Запрос для подсчета событий по дням
    if DATABASE_URL.startswith('sqlite'):
        # SQLite использует strftime для работы с датами
        query = select(
            func.strftime('%Y-%m-%d', UserWordEvent.timestamp).label('day'),
            func.count().label('count')
        ).where(
            UserWordEvent.user_id == current_user.id,
            UserWordEvent.timestamp >= start_date,
            UserWordEvent.event_type == "answered"  # Считаем только ответы
        ).group_by(
            func.strftime('%Y-%m-%d', UserWordEvent.timestamp)
        ).order_by(
            func.strftime('%Y-%m-%d', UserWordEvent.timestamp)
        )
    else:
        # PostgreSQL использует date_trunc
        # Создаем выражение один раз и используем его везде
        day_trunc = func.date_trunc('day', UserWordEvent.timestamp).label('day')
        
        query = select(
            day_trunc,
            func.count().label('count')
        ).where(
            UserWordEvent.user_id == current_user.id,
            UserWordEvent.timestamp >= start_date,
            UserWordEvent.event_type == "answered"  # Считаем только ответы
        ).group_by(
            day_trunc
        ).order_by(
            day_trunc
        )
    
    result = await session.execute(query)
    activity_data = result.all()
    
    # Форматируем результат
    calendar_data = []
    for day, count in activity_data:
        # Если day уже строка (SQLite), используем её напрямую
        if isinstance(day, str):
            date_str = day
        else:
            # Иначе форматируем datetime объект (PostgreSQL)
            date_str = day.strftime("%Y-%m-%d")
        
        calendar_data.append({
            "date": date_str,
            "count": count
        })
    
    return calendar_data
