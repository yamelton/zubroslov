#!/usr/bin/env python3
import json
import logging
import asyncio
from pathlib import Path
from gtts import gTTS
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Локальные импорты
from src.database import create_db_and_tables, async_session_maker
from src.models.word import Word

# Конфигурация
AUDIO_DIR = Path("static/audio")
TTS_LANG = "en"  # Язык для генерации произношения
TTS_SLOW = False  # Замедленное произношение

async def generate_audio(word: Word, session: AsyncSession):
    """Генерирует аудиофайл с произношением английского слова"""
    try:
        # Создаем директорию, если нужно
        AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        
        # Формируем путь к файлу
        audio_path = AUDIO_DIR / f"word_{word.id}.mp3"
        
        # Генерируем аудио через Google TTS
        tts = gTTS(
            text=word.english,
            lang=TTS_LANG,
            slow=TTS_SLOW,
            tld="com"  # Домен для акцента (com - американский)
        )
        tts.save(audio_path)
        
        # Обновляем запись в БД
        word.audio_path = "/" + str(audio_path)
        session.add(word)
        await session.commit()
        
        logging.info(f"Сгенерировано аудио для {word.english}")

    except Exception as e:
        logging.error(f"Ошибка генерации аудио: {str(e)}")
        raise

async def import_words(json_path: str = "all_words.json"):
    """Импортирует слова и генерирует аудио"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            words_data = json.load(f)

        async with async_session_maker() as session:
            for item in words_data:
                # Поиск существующей записи
                result = await session.execute(
                    select(Word).where(Word.russian == item['russian'])
                )
                word = result.scalars().first()

                # Создаем новую запись если не найдено
                if not word:
                    word = Word(
                        russian=item['russian'],
                        english=item['english']
                    )
                    session.add(word)
                    await session.commit()
                    await session.refresh(word)  # Получаем ID

                # Генерируем аудио если его нет
                if not word.audio_path:
                    await generate_audio(word, session)

        logging.info(f"Обработано {len(words_data)} слов")

    except Exception as e:
        logging.error(f"Ошибка импорта: {str(e)}")
        raise

async def main():
    logging.basicConfig(level=logging.INFO)
    await create_db_and_tables()
    await import_words()

if __name__ == "__main__":
    asyncio.run(main())
