import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import api from '../api/client';

export function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const { login } = useAuthStore();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      // Создаем form-data
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      // Отправляем с правильным content-type на новый эндпоинт FastAPI Users
      const { access_token } = await api.postForm('/auth/jwt/login', formData);

      localStorage.setItem('token', access_token);
      login({ username });
      navigate('/');
    } catch (error) {
      console.error('Ошибка входа:', error);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      // Регистрация через FastAPI Users
      await api.post('/auth/register', {
        email,
        username,
        password,
      });
      
      // После успешной регистрации переключаемся на форму входа
      setIsLogin(true);
    } catch (error) {
      console.error('Ошибка регистрации:', error);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-tabs">
        <button 
          className={isLogin ? 'active' : ''} 
          onClick={() => setIsLogin(true)}
        >
          Вход
        </button>
        <button 
          className={!isLogin ? 'active' : ''} 
          onClick={() => setIsLogin(false)}
        >
          Регистрация
        </button>
      </div>

      {isLogin ? (
        <form onSubmit={handleLogin}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="submit">Войти</button>
        </form>
      ) : (
        <form onSubmit={handleRegister}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit">Зарегистрироваться</button>
        </form>
      )}
    </div>
  );
}
