import { useEffect, useState } from 'react';
import WordGrid from '../components/WordGrid';
import { useProgress } from '../hooks/useProgress';
import api from '../api/client';

export function LearnPage({ onStatsUpdate }) {
  const [sessionStats, setSessionStats] = useState({
    correct: 0,
    incorrect: 0
  });
  const [currentWord, setCurrentWord] = useState(null);
  const [options, setOptions] = useState([]);
  const [selected, setSelected] = useState(null);
  const [progressStats, setProgressStats] = useState({
    learned: 0,
    total: 0
  });
  const { updateProgress } = useProgress();

  useEffect(() => {
    loadNextWord();
  }, []);

  // Update parent component when session stats change
  useEffect(() => {
    if (onStatsUpdate) {
      onStatsUpdate(sessionStats);
    }
  }, [sessionStats, onStatsUpdate]);

  const loadNextWord = async () => {
    try {
      const response = await api.get('/words/next');

      // Добавляем полный URL только к основному слову
      const updatedWord = {
        ...response.word,
        audioUrl: `${import.meta.env.VITE_SERVER_URL || 'http://localhost:8000'}${response.word.audio_path}`
      };
      console.log(updatedWord.audioUrl);

      // Оставляем options без изменений
      setCurrentWord(updatedWord);
      setOptions(response.options);
      setSelected(null);

    } catch (error) {
      console.error('Error loading word:', error);
    }
  };

  const handleSelect = async (wordId) => {
    if (selected) return;
    
    const isCorrect = wordId === currentWord?.id;
    setSelected({ id: wordId, isCorrect });
    setSessionStats(prev => ({
      correct: prev.correct + (isCorrect ? 1 : 0),
      incorrect: prev.incorrect + (!isCorrect ? 1 : 0)
    }));
    await updateProgress(currentWord.id, isCorrect);
    
    setTimeout(loadNextWord, 1500);
  };

  return (
    <div className="learn-page">
      <h1>{currentWord?.russian}</h1>
      <WordGrid 
        words={options} 
        selected={selected}
        correctId={currentWord?.id}
        onSelect={handleSelect}
        correctAudioUrl={currentWord?.audioUrl}
      />
    </div>
  );
}
