import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import api from '../api/client';

export function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuthStore();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    try {
      // Create form-data
      const formData = new URLSearchParams();
      formData.append('username', email); // FastAPI Users expects email in the username field
      formData.append('password', password);

      // Send with correct content-type to FastAPI Users endpoint
      const response = await api.postForm('/auth/jwt/login', formData);
      
      // Store token in localStorage first
      localStorage.setItem('token', response.access_token);
      
      try {
        // After token is stored, fetch user data
        const userData = await api.get('/users/me');
        
        // Update auth store with user data and token
        login(userData, response.access_token);
        navigate('/');
      } catch (userError) {
        console.error('Error fetching user data:', userError);
        // Even if we can't fetch user data, still log the user in with basic info
        login({ username: email.split('@')[0], email }, response.access_token);
        navigate('/');
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('Неверный email или пароль');
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    try {
      // Register through FastAPI Users
      await api.post('/auth/register', {
        email,
        username,
        password,
      });
      
      // After successful registration, switch to login form
      setIsLogin(true);
      setEmail(''); // Clear the form
      setPassword('');
      setError('Регистрация успешна! Теперь вы можете войти.');
    } catch (error) {
      console.error('Registration error:', error);
      setError('Ошибка при регистрации. Возможно, пользователь уже существует.');
    }
  };

  return (
    <div className="auth-page">
      <h2 className="auth-title">Zubroslov</h2>
      
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

      {error && <div className="auth-error">{error}</div>}

      {isLogin ? (
        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label htmlFor="login-email">Email</label>
            <input
              id="login-email"
              type="email"
              placeholder="Введите ваш email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="login-password">Пароль</label>
            <input
              id="login-password"
              type="password"
              placeholder="Введите пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit">Войти</button>
        </form>
      ) : (
        <form onSubmit={handleRegister}>
          <div className="form-group">
            <label htmlFor="register-email">Email</label>
            <input
              id="register-email"
              type="email"
              placeholder="Введите ваш email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="register-username">Имя пользователя</label>
            <input
              id="register-username"
              type="text"
              placeholder="Введите имя пользователя"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="register-password">Пароль</label>
            <input
              id="register-password"
              type="password"
              placeholder="Введите пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit">Зарегистрироваться</button>
        </form>
      )}
    </div>
  );
}
