import { useEffect, useState } from 'react';
import api from '../api/client';
import { ActivityCalendar } from '../components/ActivityCalendar';

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
      <h2>Ваш прогресс</h2>
      {stats && (
        <div className="stats-container">
          <div className="stats-summary">
            <p>Всего слов: {stats.total}</p>
            <p>Изучено: {stats.learned}</p>
            <p>Точность: {stats.accuracy}%</p>
          </div>
        </div>
      )}
      
      <ActivityCalendar days={365} />
    </div>
  );
}
