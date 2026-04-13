/**
 * pages/LoginPage.jsx
 * Página de inicio de sesión y registro.
 * 
 * Muestra un formulario de login con opción de cambiar a registro.
 * Diseño centrado con glassmorphism y gradiente de fondo.
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { HiOutlineCube, HiOutlineEye, HiOutlineEyeSlash } from 'react-icons/hi2';

export default function LoginPage() {
  const [isRegister, setIsRegister] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    username: '', email: '', password: '', full_name: '',
  });

  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isRegister) {
        await register(form);
        // Después de registrar, hacer login automático
        await login(form.username, form.password);
      } else {
        await login(form.username, form.password);
      }
      navigate('/');
    } catch (err) {
      const detail = err.response?.data?.detail || 'Error de conexión con el servidor';
      setError(typeof detail === 'string' ? detail : 'Error de autenticación');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
      background: 'var(--bg-primary)',
    }}>
      <div style={{
        width: '100%',
        maxWidth: '420px',
        background: 'var(--bg-secondary)',
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius-xl)',
        padding: '40px 36px',
        boxShadow: 'var(--shadow-lg)',
        animation: 'slideUp 400ms ease',
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{
            width: '56px', height: '56px', margin: '0 auto 16px',
            background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))',
            borderRadius: 'var(--radius-md)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '28px', color: 'white',
          }}>
            <HiOutlineCube />
          </div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: '700', marginBottom: '4px' }}>
            {isRegister ? 'Crear Cuenta' : 'Bienvenido'}
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
            {isRegister ? 'Regístrate para acceder al sistema' : 'Inicia sesión en Inventario Kardex'}
          </p>
        </div>

        {/* Error */}
        {error && (
          <div style={{
            background: 'var(--danger-bg)', color: 'var(--danger)',
            padding: '10px 14px', borderRadius: 'var(--radius-md)',
            fontSize: '0.85rem', marginBottom: '20px',
            border: '1px solid rgba(239, 68, 68, 0.2)',
          }}>
            {error}
          </div>
        )}

        {/* Formulario */}
        <form onSubmit={handleSubmit}>
          {isRegister && (
            <>
              <div className="form-group">
                <label className="form-label">Nombre Completo</label>
                <input
                  type="text" name="full_name" className="form-input"
                  placeholder="Juan Pérez" value={form.full_name}
                  onChange={handleChange} id="input-fullname"
                />
              </div>
              <div className="form-group">
                <label className="form-label">Correo Electrónico</label>
                <input
                  type="email" name="email" className="form-input"
                  placeholder="admin@inventario.com" value={form.email}
                  onChange={handleChange} required id="input-email"
                />
              </div>
            </>
          )}

          <div className="form-group">
            <label className="form-label">Usuario</label>
            <input
              type="text" name="username" className="form-input"
              placeholder="admin" value={form.username}
              onChange={handleChange} required id="input-username"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Contraseña</label>
            <div style={{ position: 'relative' }}>
              <input
                type={showPassword ? 'text' : 'password'} name="password"
                className="form-input" placeholder="••••••"
                value={form.password} onChange={handleChange} required
                style={{ paddingRight: '44px' }} id="input-password"
              />
              <button type="button" onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute', right: '10px', top: '50%',
                  transform: 'translateY(-50%)', background: 'none',
                  border: 'none', color: 'var(--text-muted)', cursor: 'pointer',
                  fontSize: '1.1rem', display: 'flex',
                }}
              >
                {showPassword ? <HiOutlineEyeSlash /> : <HiOutlineEye />}
              </button>
            </div>
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}
            style={{ width: '100%', padding: '12px', marginTop: '8px' }} id="btn-submit"
          >
            {loading ? (
              <div className="spinner" style={{ width: '20px', height: '20px', borderWidth: '2px' }} />
            ) : (
              isRegister ? 'Crear Cuenta' : 'Iniciar Sesión'
            )}
          </button>
        </form>

        {/* Toggle login/register */}
        <p style={{
          textAlign: 'center', marginTop: '24px',
          fontSize: '0.85rem', color: 'var(--text-muted)',
        }}>
          {isRegister ? '¿Ya tienes cuenta?' : '¿No tienes cuenta?'}{' '}
          <button onClick={() => { setIsRegister(!isRegister); setError(''); }}
            style={{
              background: 'none', border: 'none',
              color: 'var(--accent-primary)', cursor: 'pointer',
              fontWeight: '600', fontSize: '0.85rem',
            }} id="btn-toggle-auth"
          >
            {isRegister ? 'Iniciar Sesión' : 'Regístrate'}
          </button>
        </p>
      </div>
    </div>
  );
}
