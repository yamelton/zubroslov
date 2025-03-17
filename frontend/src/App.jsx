import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthPage } from './pages/AuthPage';
import { LearnPage } from './pages/LearnPage';
import { ProgressPage } from './pages/ProgressPage';
import useAuthStore from './store/authStore';

export default function App() {
  const { isAuthenticated } = useAuthStore();
  
  return (
    <BrowserRouter>
      <Routes>
        {!isAuthenticated ? (
          <Route path="*" element={<AuthPage />} />
        ) : (
          <>
            <Route path="/" element={<LearnPage />} />
            <Route path="/progress" element={<ProgressPage />} />
          </>
        )}
      </Routes>
    </BrowserRouter>
  );
}
