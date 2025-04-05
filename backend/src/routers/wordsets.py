from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from ..database import get_async_session
from ..models.models import WordSet, user_wordset, wordset_word
from ..models.word import Word
from ..models.models import User
from ..auth.router import current_active_user

router = APIRouter(
    prefix="/api/wordsets",
    tags=["WordSets"],
    responses={404: {"description": "Not found"}}
)

# Схемы для запросов и ответов
from pydantic import BaseModel

class WordSetCreate(BaseModel):
    name: str
    description: Optional[str] = None

class WordSetResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    word_count: int

class WordSetDetail(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    words: List[dict]

class WordSetAssign(BaseModel):
    user_id: uuid.UUID
    wordset_id: int

@router.post("/", response_model=WordSetResponse)
async def create_wordset(
    wordset: WordSetCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    """Создание нового набора слов"""
    # Проверяем, что пользователь имеет права администратора
    # В будущем можно добавить проверку роли пользователя
    
    new_wordset = WordSet(
        name=wordset.name,
        description=wordset.description
    )
    
    session.add(new_wordset)
    await session.commit()
    await session.refresh(new_wordset)
    
    return {
        "id": new_wordset.id,
        "name": new_wordset.name,
        "description": new_wordset.description,
        "word_count": 0
    }

@router.get("/", response_model=List[WordSetResponse])
async def get_wordsets(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    """Получение списка всех наборов слов"""
    result = await session.execute(select(WordSet))
    wordsets = result.scalars().all()
    
    # Для каждого набора получаем количество слов
    response = []
    for ws in wordsets:
        # Подсчет количества слов в наборе
        count_result = await session.execute(
            select(wordset_word)
            .where(wordset_word.c.wordset_id == ws.id)
        )
        word_count = len(count_result.all())
        
        response.append({
            "id": ws.id,
            "name": ws.name,
            "description": ws.description,
            "word_count": word_count
        })
    
    return response

@router.get("/{wordset_id}", response_model=WordSetDetail)
async def get_wordset(
    wordset_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    """Получение детальной информации о наборе слов, включая список слов"""
    result = await session.execute(
        select(WordSet).where(WordSet.id == wordset_id)
    )
    wordset = result.scalars().first()
    
    if not wordset:
        raise HTTPException(status_code=404, detail="Набор слов не найден")
    
    # Получаем слова из набора
    words_result = await session.execute(
        select(Word)
        .join(wordset_word, Word.id == wordset_word.c.word_id)
        .where(wordset_word.c.wordset_id == wordset_id)
    )
    words = words_result.scalars().all()
    
    return {
        "id": wordset.id,
        "name": wordset.name,
        "description": wordset.description,
        "words": [
            {
                "id": word.id,
                "english": word.english,
                "russian": word.russian
            } for word in words
        ]
    }

@router.post("/{wordset_id}/words/{word_id}")
async def add_word_to_set(
    wordset_id: int,
    word_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    """Добавление слова в набор"""
    # Проверяем существование набора слов
    wordset_result = await session.execute(
        select(WordSet).where(WordSet.id == wordset_id)
    )
    wordset = wordset_result.scalars().first()
    if not wordset:
        raise HTTPException(status_code=404, detail="Набор слов не найден")
    
    # Проверяем существование слова
    word_result = await session.execute(
        select(Word).where(Word.id == word_id)
    )
    word = word_result.scalars().first()
    if not word:
        raise HTTPException(status_code=404, detail="Слово не найдено")
    
    # Проверяем, не добавлено ли уже слово в набор
    existing_result = await session.execute(
        select(wordset_word)
        .where(wordset_word.c.wordset_id == wordset_id)
        .where(wordset_word.c.word_id == word_id)
    )
    if existing_result.first():
        return {"status": "already_exists"}
    
    # Добавляем слово в набор
    await session.execute(
        wordset_word.insert().values(
            wordset_id=wordset_id,
            word_id=word_id
        )
    )
    await session.commit()
    
    return {"status": "success"}

@router.delete("/{wordset_id}/words/{word_id}")
async def remove_word_from_set(
    wordset_id: int,
    word_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    """Удаление слова из набора"""
    # Проверяем существование связи
    existing_result = await session.execute(
        select(wordset_word)
        .where(wordset_word.c.wordset_id == wordset_id)
        .where(wordset_word.c.word_id == word_id)
    )
    if not existing_result.first():
        raise HTTPException(status_code=404, detail="Слово не найдено в наборе")
    
    # Удаляем слово из набора
    await session.execute(
        delete(wordset_word)
        .where(wordset_word.c.wordset_id == wordset_id)
        .where(wordset_word.c.word_id == word_id)
    )
    await session.commit()
    
    return {"status": "success"}

@router.post("/assign")
async def assign_wordset_to_user(
    assignment: WordSetAssign,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    """Назначение набора слов пользователю"""
    # Проверяем существование пользователя
    user_result = await session.execute(
        select(User).where(User.id == assignment.user_id)
    )
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Проверяем существование набора слов
    wordset_result = await session.execute(
        select(WordSet).where(WordSet.id == assignment.wordset_id)
    )
    wordset = wordset_result.scalars().first()
    if not wordset:
        raise HTTPException(status_code=404, detail="Набор слов не найден")
    
    # Проверяем, не назначен ли уже набор пользователю
    existing_result = await session.execute(
        select(user_wordset)
        .where(user_wordset.c.user_id == assignment.user_id)
        .where(user_wordset.c.wordset_id == assignment.wordset_id)
    )
    if existing_result.first():
        return {"status": "already_assigned"}
    
    # Назначаем набор пользователю
    await session.execute(
        user_wordset.insert().values(
            user_id=assignment.user_id,
            wordset_id=assignment.wordset_id
        )
    )
    await session.commit()
    
    return {"status": "success"}

@router.delete("/unassign")
async def unassign_wordset_from_user(
    assignment: WordSetAssign,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    """Отмена назначения набора слов пользователю"""
    # Проверяем существование связи
    existing_result = await session.execute(
        select(user_wordset)
        .where(user_wordset.c.user_id == assignment.user_id)
        .where(user_wordset.c.wordset_id == assignment.wordset_id)
    )
    if not existing_result.first():
        raise HTTPException(status_code=404, detail="Набор не назначен пользователю")
    
    # Удаляем назначение
    await session.execute(
        delete(user_wordset)
        .where(user_wordset.c.user_id == assignment.user_id)
        .where(user_wordset.c.wordset_id == assignment.wordset_id)
    )
    await session.commit()
    
    return {"status": "success"}

@router.get("/user/{user_id}", response_model=List[WordSetResponse])
async def get_user_wordsets(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    """Получение списка наборов слов, назначенных пользователю"""
    # Проверяем существование пользователя
    user_result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Получаем наборы слов пользователя
    wordsets_result = await session.execute(
        select(WordSet)
        .join(user_wordset, WordSet.id == user_wordset.c.wordset_id)
        .where(user_wordset.c.user_id == user_id)
    )
    wordsets = wordsets_result.scalars().all()
    
    # Для каждого набора получаем количество слов
    response = []
    for ws in wordsets:
        # Подсчет количества слов в наборе
        count_result = await session.execute(
            select(wordset_word)
            .where(wordset_word.c.wordset_id == ws.id)
        )
        word_count = len(count_result.all())
        
        response.append({
            "id": ws.id,
            "name": ws.name,
            "description": ws.description,
            "word_count": word_count
        })
    
    return response

@router.get("/my", response_model=List[WordSetResponse])
async def get_my_wordsets(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    """Получение списка наборов слов, назначенных текущему пользователю"""
    # Получаем наборы слов пользователя
    wordsets_result = await session.execute(
        select(WordSet)
        .join(user_wordset, WordSet.id == user_wordset.c.wordset_id)
        .where(user_wordset.c.user_id == current_user.id)
    )
    wordsets = wordsets_result.scalars().all()
    
    # Для каждого набора получаем количество слов
    response = []
    for ws in wordsets:
        # Подсчет количества слов в наборе
        count_result = await session.execute(
            select(wordset_word)
            .where(wordset_word.c.wordset_id == ws.id)
        )
        word_count = len(count_result.all())
        
        response.append({
            "id": ws.id,
            "name": ws.name,
            "description": ws.description,
            "word_count": word_count
        })
    
    return response
