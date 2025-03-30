import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { AuthPage } from './pages/AuthPage';
import { LearnPage } from './pages/LearnPage';
import { ProgressPage } from './pages/ProgressPage';
import Header from './components/Header';
import useAuthStore from './store/authStore';

export default function App() {
  const { isAuthenticated, fetchUserData } = useAuthStore();
  const [sessionStats, setSessionStats] = useState({ correct: 0, incorrect: 0 });
  
  // Check for existing token and fetch user data on app load
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchUserData();
    }
  }, [fetchUserData]);
  
  // Function to update session stats from child components
  const updateSessionStats = (newStats) => {
    setSessionStats(newStats);
  };
  
  return (
    <BrowserRouter>
      {isAuthenticated && <Header sessionStats={sessionStats} />}
      <div className={isAuthenticated ? 'app-content with-header' : 'app-content'}>
        <Routes>
          {!isAuthenticated ? (
            <>
              <Route path="/login" element={<AuthPage />} />
              <Route path="*" element={<Navigate to="/login" />} />
            </>
          ) : (
            <>
              <Route path="/" element={<LearnPage onStatsUpdate={updateSessionStats} />} />
              <Route path="/progress" element={<ProgressPage />} />
              <Route path="*" element={<Navigate to="/" />} />
            </>
          )}
        </Routes>
      </div>
    </BrowserRouter>
  );
}
