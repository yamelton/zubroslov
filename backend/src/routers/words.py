from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from typing import List, Optional, Dict
import random
from datetime import datetime, timedelta

# Локальные импорты
from backend.src.database import get_session
from backend.src.models.word import Word, WordProgress
from backend.src.models.models import User
from backend.src.routers.auth import get_current_user

router = APIRouter(
    prefix="/api/words",
    tags=["Words"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=List[Word])
async def get_words(
    category: Optional[str] = Query(None, min_length=2),
    limit: int = Query(50, gt=0),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
):
    """Получение списка слов с фильтрацией по категории"""
    try:
        query = select(Word)
        if category:
            query = query.where(Word.category == category)
        
        query = query.offset(offset).limit(limit)
        
        result = session.exec(query)
        return result.all()
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        ) from e


@router.get("/next", response_model=dict)
async def get_next_word(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    exclude_last: int = Query(5)
):
    try:
        # 1. Проверяем наличие слов в базе (для тестирования)
        all_words = session.exec(select(Word)).all()
        if not all_words:
            raise HTTPException(400, "База слов пуста. Добавьте слова через админку")

        # Получаем последние показанные слова
        last_shown = session.exec(
            select(WordProgress.word_id)
            .where(WordProgress.user_id == current_user.id)
            .order_by(WordProgress.last_shown.desc())
            .limit(exclude_last)
        ).all()

        # Базовый запрос с исключением последних
        base_query = select(Word)
        if last_shown:
            base_query = base_query.where(Word.id.not_in(last_shown))

        # Выбор кандидатов с учетом прогресса
        candidates = session.exec(
            base_query.order_by(Word.id).limit(100)
        ).all()

        if not candidates:
            candidates = session.exec(select(Word)).all()

        next_word = random.choice(candidates) if candidates else None

        # Генерация вариантов ответов
        all_words = session.exec(select(Word)).all()
        wrong_choices = [w for w in all_words if w.id != next_word.id]
        options = random.sample(wrong_choices, min(7, len(wrong_choices))) + [next_word]
        random.shuffle(options)

        # Обновление статистики показа
        if next_word:
            progress = session.exec(
                select(WordProgress)
                .where(WordProgress.user_id == current_user.id)
                .where(WordProgress.word_id == next_word.id)
            ).first()

            if not progress:
                progress = WordProgress(
                    user_id=current_user.id,
                    word_id=next_word.id,
                    shown_count=1
                )
            else:
                progress.shown_count += 1
                progress.last_shown = datetime.utcnow()

            session.add(progress)
            session.commit()

        return {
            "word": next_word,
            "options":[
                {
                    "id": w.id,
                    "english": w.english,
                    # "pronunciation": w.pronunciation,
                    "russian": w.russian
                } for w in options
            ], 
            "correct_id": next_word.id if next_word else None
        }

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
