import { useEffect } from 'react';
import AudioPlayer from './AudioPlayer';

export default function WordGrid({ words, selected, correctId, onSelect, correctAudioUrl }) {
  useEffect(() => {
    if (selected) {
      const timer = setTimeout(() => {
        onSelect(correctId);
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [selected, correctId, onSelect]);

  const getButtonClass = (word) => {
    if (!selected) return '';
    if (word.id === correctId) return 'correct';
    if (word.id === selected.id) return 'incorrect';
    return '';
  };

  console.log(words);

  return (
    <div className="word-grid">
      {words.map((word) => (
        <button
          key={word.id}
          className={getButtonClass(word)}
          onClick={() => onSelect(word.id)}
          disabled={!!selected}
        >
          {word.english}
          {selected && word.id === correctId && (
            <AudioPlayer url={correctAudioUrl} />
          )}
        </button>
      ))}
    </div>
  );
}
