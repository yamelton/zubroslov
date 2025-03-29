#!/usr/bin/env python3
import json
import logging
from pathlib import Path
from gtts import gTTS
from sqlmodel import Session, select

# Локальные импорты
from src.database import create_db_and_tables, engine
from src.models.word import Word

# Конфигурация
AUDIO_DIR = Path("static/audio")
TTS_LANG = "en"  # Язык для генерации произношения
TTS_SLOW = False  # Замедленное произношение

def generate_audio(word: Word, session: Session):
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
        # word.audio_path = str(audio_path.relative_to("static"))
        word.audio_path = "/" + str(audio_path)
        session.add(word)
        session.commit()
        
        logging.info(f"Сгенерировано аудио для {word.english}")

    except Exception as e:
        logging.error(f"Ошибка генерации аудио: {str(e)}")
        raise

def import_words(json_path: str = "all_words.json"):
    """Импортирует слова и генерирует аудио"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            words_data = json.load(f)

        with Session(engine) as session:
            for item in words_data:
                # Поиск существующей записи
                word = session.exec(
                    select(Word).where(Word.russian == item['russian'])
                ).first()

                # Создаем новую запись если не найдено
                if not word:
                    word = Word(
                        russian=item['russian'],
                        english=item['english'],
                        category=item.get('category', 'general'),
                        pronunciation=item.get('pronunciation', ''),
                        difficulty=item.get('difficulty', 1)
                    )
                    session.add(word)
                    session.commit()
                    session.refresh(word)  # Получаем ID

                # Генерируем аудио если его нет
                if not word.audio_path:
                    generate_audio(word, session)

        logging.info(f"Обработано {len(words_data)} слов")

    except Exception as e:
        logging.error(f"Ошибка импорта: {str(e)}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_db_and_tables()
    import_words()
