import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { AuthPage } from './pages/AuthPage';
import { LearnPage } from './pages/LearnPage';
import { ProgressPage } from './pages/ProgressPage';
import Header from './components/Header';
import useAuthStore from './store/authStore';

export default function App() {
  const { isAuthenticated, fetchUserData } = useAuthStore();
  
  // Check for existing token and fetch user data on app load
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchUserData();
    }
  }, [fetchUserData]);
  
  return (
    <BrowserRouter>
      {isAuthenticated && <Header />}
      <div className={isAuthenticated ? 'app-content with-header' : 'app-content'}>
        <Routes>
          {!isAuthenticated ? (
            <>
              <Route path="/login" element={<AuthPage />} />
              <Route path="*" element={<Navigate to="/login" />} />
            </>
          ) : (
            <>
              <Route path="/" element={<LearnPage />} />
              <Route path="/progress" element={<ProgressPage />} />
              <Route path="*" element={<Navigate to="/" />} />
            </>
          )}
        </Routes>
      </div>
    </BrowserRouter>
  );
}
