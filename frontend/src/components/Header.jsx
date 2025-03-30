import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';

export default function Header() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <header className="app-header">
      <div className="header-content">
        <div className="logo">Zubroslov</div>
        <nav className="nav-links">
          <a href="/" className="nav-link">Учить</a>
          <a href="/progress" className="nav-link">Прогресс</a>
        </nav>
        <div className="user-section">
          {user && (
            <>
              <span className="username">{user.username}</span>
              <button onClick={handleLogout} className="logout-button">
                Выйти
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
