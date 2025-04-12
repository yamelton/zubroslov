import React, { useState, useEffect, useRef } from 'react';
import api from '../api/client';

export function ActivityCalendar({ days = 365 }) {
  const [activityData, setActivityData] = useState([]);
  const [loading, setLoading] = useState(true);
  const calendarGridRef = useRef(null);
  
  useEffect(() => {
    const fetchActivityData = async () => {
      try {
        const data = await api.get(`/progress/activity-calendar?days=${days}`);
        setActivityData(data);
      } catch (error) {
        console.error('Error fetching activity data:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchActivityData();
  }, [days]);
  
  // Scroll to the end of the calendar when data is loaded
  useEffect(() => {
    if (!loading && calendarGridRef.current) {
      // Scroll to the rightmost position (most recent activity)
      // Use a small timeout to ensure the calendar is fully rendered
      setTimeout(() => {
        calendarGridRef.current.scrollLeft = calendarGridRef.current.scrollWidth;
      }, 100);
    }
  }, [loading]);
  
  // Функция для определения цвета ячейки в зависимости от количества слов
  const getCellColor = (count) => {
    if (count === 0) return '#ebedf0';
    if (count < 5) return '#c6e48b';
    if (count < 10) return '#7bc96f';
    if (count < 20) return '#239a3b';
    return '#196127';
  };
  
  // Создаем сетку календаря
  const renderCalendarGrid = () => {
    // Создаем мапу дата -> количество
    const activityMap = new Map();
    activityData.forEach(item => {
      activityMap.set(item.date, item.count);
    });
    
    // Получаем текущую дату и вычисляем начальную дату для календаря
    const today = new Date();
    const startDate = new Date(today);
    startDate.setDate(today.getDate() - days + 1);
    
    // Создаем массив дат для отображения
    const dateArray = [];
    for (let d = new Date(startDate); d <= today; d.setDate(d.getDate() + 1)) {
      const dateStr = d.toISOString().split('T')[0];
      const count = activityMap.get(dateStr) || 0;
      dateArray.push({ date: dateStr, count });
    }
    
    // Группируем по неделям для отображения в сетке
    const weeks = [];
    let week = [];
    
    // Определяем день недели для начальной даты (0 - воскресенье, 6 - суббота)
    const firstDay = new Date(startDate).getDay();
    
    // Добавляем пустые ячейки в начало первой недели
    for (let i = 0; i < firstDay; i++) {
      week.push(null);
    }
    
    // Заполняем календарь
    dateArray.forEach((day, index) => {
      week.push(day);
      
      // Если неделя заполнена или это последний день, добавляем неделю в массив недель
      if (week.length === 7 || index === dateArray.length - 1) {
        weeks.push([...week]);
        week = [];
      }
    });
    
    return (
      <div className="activity-calendar">
        <div className="calendar-grid" ref={calendarGridRef}>
          {weeks.map((week, weekIndex) => (
            <div key={`week-${weekIndex}`} className="calendar-week">
              {week.map((day, dayIndex) => (
                <div 
                  key={`day-${weekIndex}-${dayIndex}`} 
                  className="calendar-day"
                  style={{ 
                    backgroundColor: day ? getCellColor(day.count) : 'transparent',
                    opacity: day ? 1 : 0
                  }}
                  title={day ? `${day.date}: ${day.count} слов` : ''}
                />
              ))}
            </div>
          ))}
        </div>
        <div className="calendar-legend">
          <div className="legend-item">
            <span>Меньше</span>
            <div className="legend-cell" style={{ backgroundColor: '#ebedf0' }}></div>
            <div className="legend-cell" style={{ backgroundColor: '#c6e48b' }}></div>
            <div className="legend-cell" style={{ backgroundColor: '#7bc96f' }}></div>
            <div className="legend-cell" style={{ backgroundColor: '#239a3b' }}></div>
            <div className="legend-cell" style={{ backgroundColor: '#196127' }}></div>
            <span>Больше</span>
          </div>
        </div>
      </div>
    );
  };
  
  if (loading) {
    return <div className="loading">Загрузка календаря активности...</div>;
  }
  
  return (
    <div className="activity-calendar-container">
      <h3>Календарь активности</h3>
      {renderCalendarGrid()}
    </div>
  );
}
