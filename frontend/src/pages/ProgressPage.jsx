import { useEffect, useState } from 'react';
import api from '../api/client';

export function ProgressPage() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await api.get('/progress/stats');
        setStats(data);
      } catch (error) {
        console.error('Error loading stats:', error);
      }
    };
    loadStats();
  }, []);

  return (
    <div className="progress-page">
      <h2>Your Progress</h2>
      {stats && (
        <div>
          <p>Total words: {stats.total}</p>
          <p>Learned: {stats.learned}</p>
          <p>Accuracy: {stats.accuracy}%</p>
        </div>
      )}
    </div>
  );
}
