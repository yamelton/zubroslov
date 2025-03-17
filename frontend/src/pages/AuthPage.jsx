import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import api from '../api/client';

export function AuthPage() {
  const [username, setUsername] = useState('');
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

    // Отправляем с правильным content-type
    const { access_token } = await api.postForm('/auth/token', formData);

    localStorage.setItem('token', access_token);
    login({ username });
    navigate('/');
  } catch (error) {
    console.error('Ошибка входа:', error);
  }
};

  return (
    <div className="auth-page">
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
        <button type="submit">Login</button>
      </form>
    </div>
  );
}
