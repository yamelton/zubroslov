#!/usr/bin/env python3
import json
import logging
import asyncio
import argparse
from pathlib import Path
from gtts import gTTS
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Локальные импорты
from src.database import create_db_and_tables, async_session_maker
from src.models.word import Word
from src.models.models import WordSet, wordset_word

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

async def import_words(json_path: str = "all_words.json", wordset_name: str = None):
    """Импортирует слова и генерирует аудио, опционально добавляя их в набор слов"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            words_data = json.load(f)

        async with async_session_maker() as session:
            # Если указано имя набора слов, проверяем его существование или создаем новый
            wordset = None
            if wordset_name:
                wordset_result = await session.execute(
                    select(WordSet).where(WordSet.name == wordset_name)
                )
                wordset = wordset_result.scalars().first()
                
                if not wordset:
                    logging.info(f"Создаем новый набор слов: {wordset_name}")
                    wordset = WordSet(
                        name=wordset_name,
                        description=f"Набор слов, импортированный из {json_path}"
                    )
                    session.add(wordset)
                    await session.commit()
                    await session.refresh(wordset)
            
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
                
                # Если указан набор слов, добавляем слово в набор
                if wordset:
                    # Проверяем, не добавлено ли уже слово в набор
                    existing_result = await session.execute(
                        select(wordset_word)
                        .where(wordset_word.c.wordset_id == wordset.id)
                        .where(wordset_word.c.word_id == word.id)
                    )
                    if not existing_result.first():
                        # Добавляем слово в набор
                        await session.execute(
                            wordset_word.insert().values(
                                wordset_id=wordset.id,
                                word_id=word.id
                            )
                        )
                        await session.commit()
                        logging.info(f"Слово '{word.english}' добавлено в набор '{wordset.name}'")

        logging.info(f"Обработано {len(words_data)} слов")

    except Exception as e:
        logging.error(f"Ошибка импорта: {str(e)}")
        raise

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description='Импорт слов из JSON файла')
    parser.add_argument('--file', type=str, default="all_words.json", help='Путь к JSON файлу со словами')
    parser.add_argument('--wordset', type=str, help='Имя набора слов для добавления импортируемых слов')
    args = parser.parse_args()
    
    await create_db_and_tables()
    await import_words(args.file, args.wordset)

if __name__ == "__main__":
    asyncio.run(main())
