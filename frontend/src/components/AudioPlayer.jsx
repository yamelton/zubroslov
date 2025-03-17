import { useEffect, useRef, useState } from 'react';

export default function AudioPlayer({ url }) {
  const audioRef = useRef(null);
  const [loaded, setLoaded] = useState(false);

  const handleError = () => {
    console.error('Failed to load audio:', url);
    setLoaded(false);
  };

  useEffect(() => {
    const audioElement = audioRef.current;
    
    const tryPlay = async () => {
      try {
        if (url && audioElement) {
          await audioElement.load();
          await audioElement.play();
          setLoaded(true);
        }
      } catch (error) {
        handleError();
      }
    };

    tryPlay();

    return () => {
      if (audioElement) {
        audioElement.pause();
        audioElement.currentTime = 0;
        audioElement.removeEventListener('error', handleError);
      }
    };
  }, [url]);

  return (
    <audio 
      ref={audioRef}
      hidden
      onError={handleError}
    >
      <source src={url} type="audio/mpeg" />
      Your browser does not support the audio element.
    </audio>
  );
}
