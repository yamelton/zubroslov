from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict
import random
import json
from datetime import datetime, timedelta

# Локальные импорты
from ..database import get_async_session
from ..models.word import Word, WordProgress, UserWordEvent
from ..models.models import User, user_wordset, wordset_word
from ..auth.router import current_active_user

router = APIRouter(
    prefix="/api/words",
    tags=["Words"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=List[dict])
async def get_words(
    category: Optional[str] = Query(None, min_length=2),
    limit: int = Query(50, gt=0),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_async_session),
):
    """Получение списка слов с фильтрацией по категории"""
    try:
        query = select(Word)
        if category:
            query = query.where(Word.category == category)
        
        query = query.offset(offset).limit(limit)
        
        result = await session.execute(query)
        words = result.scalars().all()
        
        return [
            {
                "id": w.id,
                "english": w.english,
                "russian": w.russian,
                "audio_path": w.audio_path
            } for w in words
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        ) from e


@router.get("/next", response_model=dict)
async def get_next_word(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
    exclude_last: int = Query(5)
):
    try:
        # Получаем ID наборов слов, назначенных пользователю
        user_wordsets_result = await session.execute(
            select(user_wordset.c.wordset_id)
            .where(user_wordset.c.user_id == current_user.id)
        )
        user_wordset_ids = user_wordsets_result.scalars().all()
        
        # Получаем последние показанные слова
        last_shown_result = await session.execute(
            select(WordProgress.word_id)
            .where(WordProgress.user_id == current_user.id)
            .order_by(WordProgress.last_shown.desc())
            .limit(exclude_last)
        )
        last_shown = last_shown_result.scalars().all()
        
        # Базовый запрос
        base_query = select(Word)
        
        # Если пользователю назначены наборы слов, выбираем слова только из этих наборов
        if user_wordset_ids:
            # Получаем ID слов из наборов пользователя
            user_words_result = await session.execute(
                select(wordset_word.c.word_id)
                .where(wordset_word.c.wordset_id.in_(user_wordset_ids))
            )
            user_word_ids = user_words_result.scalars().all()
            
            if not user_word_ids:
                # Если в наборах пользователя нет слов, используем все слова
                result = await session.execute(select(Word))
                all_words = result.scalars().all()
                if not all_words:
                    raise HTTPException(400, "База слов пуста. Добавьте слова через админку")
            else:
                # Ограничиваем выборку словами из наборов пользователя
                base_query = base_query.where(Word.id.in_(user_word_ids))
        else:
            # Если пользователю не назначены наборы, проверяем наличие слов в базе
            result = await session.execute(select(Word))
            all_words = result.scalars().all()
            if not all_words:
                raise HTTPException(400, "База слов пуста. Добавьте слова через админку")
        
        # Исключаем последние показанные слова
        if last_shown:
            base_query = base_query.where(Word.id.not_in(last_shown))
        
        # Выбор кандидатов с учетом прогресса
        candidates_result = await session.execute(
            base_query.order_by(Word.id).limit(100)
        )
        candidates = candidates_result.scalars().all()
        
        if not candidates:
            # Если после всех фильтров не осталось кандидатов, берем любое слово
            if user_wordset_ids:
                # Из наборов пользователя, если они есть
                user_words_query = select(Word).where(
                    Word.id.in_(
                        select(wordset_word.c.word_id)
                        .where(wordset_word.c.wordset_id.in_(user_wordset_ids))
                    )
                )
                result = await session.execute(user_words_query)
                candidates = result.scalars().all()
                
                if not candidates:
                    # Если в наборах пользователя нет слов, используем все слова
                    result = await session.execute(select(Word))
                    candidates = result.scalars().all()
            else:
                # Или из всех слов, если наборы не назначены
                result = await session.execute(select(Word))
                candidates = result.scalars().all()
        
        next_word = random.choice(candidates) if candidates else None

        # Генерация вариантов ответов
        result = await session.execute(select(Word))
        all_words = result.scalars().all()
        wrong_choices = [w for w in all_words if w.id != next_word.id]
        options = random.sample(wrong_choices, min(7, len(wrong_choices))) + [next_word]
        random.shuffle(options)

        # Обновление статистики показа
        if next_word:
            progress_result = await session.execute(
                select(WordProgress)
                .where(WordProgress.user_id == current_user.id)
                .where(WordProgress.word_id == next_word.id)
            )
            progress = progress_result.scalars().first()

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
            
            # Запись события показа слова
            word_event = UserWordEvent(
                user_id=current_user.id,
                word_id=next_word.id,
                event_type="shown",
                event_data=json.dumps({
                    "options": [opt.id for opt in options]  # Сохраняем ID предложенных вариантов
                })
            )
            session.add(word_event)
            
            await session.commit()

        return {
            "word": {
                "id": next_word.id,
                "english": next_word.english,
                "russian": next_word.russian,
                "audio_path": next_word.audio_path
            } if next_word else None,
            "options":[
                {
                    "id": w.id,
                    "english": w.english,
                    "russian": w.russian
                } for w in options
            ], 
            "correct_id": next_word.id if next_word else None
        }

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
