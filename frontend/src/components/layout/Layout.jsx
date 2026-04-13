/**
 * components/layout/Layout.jsx
 * Layout principal de la aplicación.
 * 
 * Estructura: Sidebar fijo a la izquierda + contenido principal.
 * Usa Outlet de react-router para renderizar las páginas hijas.
 */
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

export default function Layout() {
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
