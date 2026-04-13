/**
 * components/layout/Sidebar.jsx
 * Barra lateral de navegación con enlaces a todas las secciones.
 * 
 * Resalta el enlace activo basándose en la ruta actual.
 * Incluye el logo, navegación principal y botón de logout.
 */
import { NavLink, useNavigate } from 'react-router-dom';
import {
  HiOutlineSquares2X2,
  HiOutlineCube,
  HiOutlineTag,
  HiOutlineArrowsRightLeft,
  HiOutlineClipboardDocumentList,
  HiOutlineArrowRightOnRectangle,
} from 'react-icons/hi2';
import { useAuth } from '../../context/AuthContext';

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="logo-icon">📦</div>
        <h1>
          Inventario
          <span>Sistema Kardex</span>
        </h1>
      </div>

      {/* Navegación */}
      <nav className="sidebar-nav">
        <span className="nav-section-title">Principal</span>

        <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} id="nav-dashboard">
          <HiOutlineSquares2X2 className="nav-icon" />
          Dashboard
        </NavLink>

        <NavLink to="/products" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} id="nav-products">
          <HiOutlineCube className="nav-icon" />
          Productos
        </NavLink>

        <NavLink to="/categories" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} id="nav-categories">
          <HiOutlineTag className="nav-icon" />
          Categorías
        </NavLink>

        <span className="nav-section-title">Operaciones</span>

        <NavLink to="/movements" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} id="nav-movements">
          <HiOutlineArrowsRightLeft className="nav-icon" />
          Movimientos
        </NavLink>

        <NavLink to="/kardex" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} id="nav-kardex">
          <HiOutlineClipboardDocumentList className="nav-icon" />
          Kardex
        </NavLink>
      </nav>

      {/* Footer: Usuario y logout */}
      <div style={{
        padding: '16px 12px',
        borderTop: '1px solid var(--border-color)',
        marginTop: 'auto',
      }}>
        {user && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '8px 12px',
            marginBottom: '8px',
          }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.8rem',
              fontWeight: '700',
              color: 'white',
              flexShrink: 0,
            }}>
              {user.username?.charAt(0).toUpperCase()}
            </div>
            <div style={{ overflow: 'hidden' }}>
              <div style={{ fontSize: '0.82rem', fontWeight: '600', color: 'var(--text-primary)' }}>
                {user.full_name || user.username}
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {user.email}
              </div>
            </div>
          </div>
        )}
        <button onClick={handleLogout} className="nav-link" style={{ width: '100%', border: 'none', background: 'none', textAlign: 'left' }} id="btn-logout">
          <HiOutlineArrowRightOnRectangle className="nav-icon" />
          Cerrar Sesión
        </button>
      </div>
    </aside>
  );
}
