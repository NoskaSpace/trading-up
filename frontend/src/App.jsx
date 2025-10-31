import React, { useEffect, useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api';

function App() {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [token, setToken] = useState(() => window.localStorage.getItem('token') ?? '');
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // 토큰이 존재할 때는 자동으로 상태 정보를 불러온다.
    if (token) {
      fetchStatus();
    }
  }, [token]);

  const handleChange = (event) => {
    // 입력 필드의 값을 최신 상태로 유지한다.
    const { name, value } = event.target;
    setCredentials((prev) => ({ ...prev, [name]: value }));
  };

  const handleLogin = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);

    try {
      const body = new URLSearchParams();
      body.append('username', credentials.username);
      body.append('password', credentials.password);

      const response = await fetch(`${API_BASE_URL}/auth/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body
      });

      if (!response.ok) {
        throw new Error('로그인에 실패했습니다. 자격 증명을 확인하세요.');
      }

      const data = await response.json();
      window.localStorage.setItem('token', data.access_token);
      setToken(data.access_token);
      setCredentials({ username: '', password: '' });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchStatus = async () => {
    setError('');
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/status`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      if (response.status === 401) {
        throw new Error('세션이 만료되었습니다. 다시 로그인하세요.');
      }

      if (!response.ok) {
        throw new Error('상태 정보를 불러오지 못했습니다.');
      }

      const data = await response.json();
      setStatus(data);
    } catch (err) {
      setStatus(null);
      setError(err.message);
      window.localStorage.removeItem('token');
      setToken('');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    // 로그아웃 시 로컬 스토리지의 토큰을 제거한다.
    window.localStorage.removeItem('token');
    setToken('');
    setStatus(null);
  };

  return (
    <div className="container">
      <header>
        <h1>Trading Up 모니터링</h1>
        {token && (
          <button type="button" onClick={handleLogout} className="secondary">
            로그아웃
          </button>
        )}
      </header>

      {!token ? (
        <form onSubmit={handleLogin} className="card">
          <h2>관리자 로그인</h2>
          <label>
            아이디
            <input
              type="text"
              name="username"
              value={credentials.username}
              onChange={handleChange}
              autoComplete="username"
              required
            />
          </label>
          <label>
            비밀번호
            <input
              type="password"
              name="password"
              value={credentials.password}
              onChange={handleChange}
              autoComplete="current-password"
              required
            />
          </label>
          <button type="submit" disabled={loading}>
            {loading ? '로그인 중...' : '로그인'}
          </button>
          {error && <p className="error">{error}</p>}
        </form>
      ) : (
        <section className="card">
          <div className="card-header">
            <h2>시스템 상태</h2>
            <button type="button" onClick={fetchStatus} disabled={loading}>
              {loading ? '갱신 중...' : '새로 고침'}
            </button>
          </div>
          {error && <p className="error">{error}</p>}
          {status ? (
            <ul className="status-list">
              <li>
                <strong>상태</strong>
                <span>{status.status}</span>
              </li>
              <li>
                <strong>버전</strong>
                <span>{status.version}</span>
              </li>
              <li>
                <strong>서버 시각</strong>
                <span>{new Date(status.timestamp).toLocaleString()}</span>
              </li>
            </ul>
          ) : (
            <p>상태 정보를 불러오려면 새로 고침을 클릭하세요.</p>
          )}
        </section>
      )}
    </div>
  );
}

export default App;
