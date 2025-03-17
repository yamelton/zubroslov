import { useState } from 'react';
import api from '../api/client';

// Меняем на именованный экспорт
export const useProgress = () => {
  const updateProgress = async (wordId, isCorrect) => {
    try {
      await api.put(`/progress/progress/${wordId}?is_correct=${isCorrect}`);
    } catch (error) {
      console.error('Error updating progress:', error);
    }
  };

  return { updateProgress };
};
