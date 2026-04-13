/**
 * pages/DashboardPage.jsx
 * Página principal del dashboard.
 * 
 * Muestra 4 tarjetas de estadísticas y la tabla de stock
 * actual de todos los productos con indicadores de stock bajo.
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  HiOutlineCube, HiOutlineArrowsRightLeft,
  HiOutlineExclamationTriangle, HiOutlineCurrencyDollar,
} from 'react-icons/hi2';
import { kardexApi } from '../api/inventory';

export default function DashboardPage() {
  const [stock, setStock] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const data = await kardexApi.getAllStock();
      setStock(data);
    } catch (err) {
      console.error('Error cargando stock:', err);
    } finally {
      setLoading(false);
    }
  };

  // Estadísticas calculadas
  const totalProducts = stock.length;
  const lowStockCount = stock.filter(s => s.is_low_stock).length;
  const totalValue = stock.reduce((sum, s) => sum + Number(s.total_value), 0);
  const totalUnits = stock.reduce((sum, s) => sum + Number(s.current_quantity), 0);

  if (loading) {
    return <div className="loading-center"><div className="spinner" /></div>;
  }

  return (
    <div>
      {/* Header */}
      <div className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p>Resumen general del inventario</p>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card cyan">
          <div className="stat-icon cyan"><HiOutlineCube /></div>
          <div className="stat-info">
            <h3>Productos</h3>
            <div className="stat-value">{totalProducts}</div>
            <div className="stat-sub">productos activos</div>
          </div>
        </div>

        <div className="stat-card purple">
          <div className="stat-icon purple"><HiOutlineArrowsRightLeft /></div>
          <div className="stat-info">
            <h3>Total Unidades</h3>
            <div className="stat-value">{Number(totalUnits).toLocaleString()}</div>
            <div className="stat-sub">en inventario</div>
          </div>
        </div>

        <div className="stat-card green">
          <div className="stat-icon green"><HiOutlineCurrencyDollar /></div>
          <div className="stat-info">
            <h3>Valor Total</h3>
            <div className="stat-value">${Number(totalValue).toLocaleString('es-MX', { minimumFractionDigits: 2 })}</div>
            <div className="stat-sub">valor del inventario</div>
          </div>
        </div>

        <div className="stat-card orange">
          <div className="stat-icon orange"><HiOutlineExclamationTriangle /></div>
          <div className="stat-info">
            <h3>Stock Bajo</h3>
            <div className="stat-value">{lowStockCount}</div>
            <div className="stat-sub">requieren atención</div>
          </div>
        </div>
      </div>

      {/* Tabla de stock */}
      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border-color)' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: '700' }}>Stock Actual</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '2px' }}>
            Inventario actual de todos los productos
          </p>
        </div>

        {stock.length > 0 ? (
          <div className="table-container" style={{ border: 'none', borderRadius: 0 }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>SKU</th>
                  <th>Producto</th>
                  <th>Categoría</th>
                  <th style={{ textAlign: 'right' }}>Cantidad</th>
                  <th style={{ textAlign: 'right' }}>Precio Unit.</th>
                  <th style={{ textAlign: 'right' }}>Valor Total</th>
                  <th>Estado</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {stock.map((item) => (
                  <tr key={item.product_id}>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.82rem', color: 'var(--text-accent)' }}>
                      {item.sku}
                    </td>
                    <td style={{ fontWeight: '500', color: 'var(--text-primary)' }}>{item.product_name}</td>
                    <td>{item.category_name || '—'}</td>
                    <td style={{ textAlign: 'right', fontWeight: '600', color: 'var(--text-primary)' }}>
                      {Number(item.current_quantity).toLocaleString()} {item.unit_measure}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      ${Number(item.unit_price).toLocaleString('es-MX', { minimumFractionDigits: 2 })}
                    </td>
                    <td style={{ textAlign: 'right', fontWeight: '500' }}>
                      ${Number(item.total_value).toLocaleString('es-MX', { minimumFractionDigits: 2 })}
                    </td>
                    <td>
                      {item.is_low_stock ? (
                        <span className="badge badge-warning">⚠ Stock bajo</span>
                      ) : (
                        <span className="badge badge-success">✓ Normal</span>
                      )}
                    </td>
                    <td>
                      <button className="btn btn-sm btn-secondary"
                        onClick={() => navigate(`/kardex/${item.product_id}`)}
                        id={`btn-kardex-${item.sku}`}
                      >
                        Ver Kardex
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">📦</div>
            <h3>Sin productos</h3>
            <p>Agrega productos para ver el stock actual</p>
          </div>
        )}
      </div>
    </div>
  );
}
