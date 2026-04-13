/**
 * pages/KardexPage.jsx
 * Página de visualización del Kardex.
 * 
 * Muestra el Kardex completo de un producto seleccionado:
 * - Header con nombre del producto y stock actual
 * - Tabla con todos los movimientos y balance acumulado
 * - Filtros de fecha opcionales
 * - Selector de producto si no viene por URL
 * 
 * El balance acumulado (running balance) muestra cómo
 * evoluciona el inventario con cada movimiento.
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  HiOutlineArrowDownTray, HiOutlineArrowUpTray,
  HiOutlineMagnifyingGlass, HiOutlineFunnel,
} from 'react-icons/hi2';
import { kardexApi, productsApi } from '../api/inventory';
import { useToast } from '../context/ToastContext';

export default function KardexPage() {
  const { productId } = useParams();
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(productId || '');
  const [kardex, setKardex] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const { showError } = useToast();

  // Cargar lista de productos al montar
  useEffect(() => {
    productsApi.getAll().then(setProducts).catch(() => {});
  }, []);

  // Cargar kardex cuando cambia el producto seleccionado
  useEffect(() => {
    if (productId) {
      setSelectedProduct(productId);
      loadKardex(productId);
    }
  }, [productId]);

  const loadKardex = async (pid, params = {}) => {
    if (!pid) return;
    setLoading(true);
    try {
      const data = await kardexApi.getKardex(pid, params);
      setKardex(data);
    } catch (err) {
      showError(err.response?.data?.detail || 'Error cargando kardex');
      setKardex(null);
    } finally {
      setLoading(false);
    }
  };

  const handleProductChange = (pid) => {
    setSelectedProduct(pid);
    if (pid) {
      navigate(`/kardex/${pid}`);
      loadKardex(pid);
    } else {
      setKardex(null);
    }
  };

  const handleFilter = () => {
    const params = {};
    if (dateFrom) params.date_from = new Date(dateFrom).toISOString();
    if (dateTo) params.date_to = new Date(dateTo).toISOString();
    loadKardex(selectedProduct, params);
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Kardex</h1>
          <p>Registro histórico de movimientos por producto</p>
        </div>
      </div>

      {/* Selector de producto y filtros */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
          <div style={{ flex: '1', minWidth: '250px' }}>
            <label className="form-label">
              <HiOutlineMagnifyingGlass style={{ verticalAlign: 'middle', marginRight: '6px' }} />
              Seleccionar Producto
            </label>
            <select className="form-select" value={selectedProduct}
              onChange={(e) => handleProductChange(e.target.value)} id="select-kardex-product"
            >
              <option value="">— Seleccionar un producto —</option>
              {products.map(p => (
                <option key={p.id} value={p.id}>{p.sku} — {p.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="form-label">Desde</label>
            <input className="form-input" type="date" value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)} id="input-kardex-from" />
          </div>
          <div>
            <label className="form-label">Hasta</label>
            <input className="form-input" type="date" value={dateTo}
              onChange={(e) => setDateTo(e.target.value)} id="input-kardex-to" />
          </div>
          <button className="btn btn-secondary" onClick={handleFilter}
            disabled={!selectedProduct} id="btn-kardex-filter"
          >
            <HiOutlineFunnel /> Filtrar
          </button>
        </div>
      </div>

      {/* Loading */}
      {loading && <div className="loading-center"><div className="spinner" /></div>}

      {/* Sin producto seleccionado */}
      {!loading && !kardex && !selectedProduct && (
        <div className="card">
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <h3>Selecciona un producto</h3>
            <p>Elige un producto del selector para ver su Kardex</p>
          </div>
        </div>
      )}

      {/* Kardex del producto */}
      {!loading && kardex && (
        <>
          {/* Header con info del producto */}
          <div className="kardex-header">
            <div className="kardex-product-info">
              <h2>{kardex.product_name}</h2>
              <span className="sku">SKU: {kardex.sku} · {kardex.unit_measure}</span>
            </div>
            <div className="kardex-stock">
              <div className="stock-value">{Number(kardex.current_stock).toLocaleString()}</div>
              <div className="stock-label">Stock Actual</div>
            </div>
          </div>

          {/* Tabla del Kardex */}
          <div className="table-container" style={{ borderTopLeftRadius: 0, borderTopRightRadius: 0 }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Tipo</th>
                  <th>Dirección</th>
                  <th style={{ textAlign: 'right' }}>Cantidad</th>
                  <th style={{ textAlign: 'right' }}>Costo Unit.</th>
                  <th style={{ textAlign: 'right' }}>Costo Total</th>
                  <th style={{ textAlign: 'right' }}>Balance</th>
                  <th>Referencia</th>
                  <th>Registrado por</th>
                </tr>
              </thead>
              <tbody>
                {kardex.entries.length === 0 ? (
                  <tr>
                    <td colSpan="9">
                      <div className="empty-state" style={{ padding: '40px' }}>
                        <h3>Sin movimientos</h3>
                        <p>Este producto aún no tiene movimientos registrados</p>
                      </div>
                    </td>
                  </tr>
                ) : kardex.entries.map((entry, idx) => (
                  <tr key={entry.movement_id}>
                    <td style={{ whiteSpace: 'nowrap', fontSize: '0.82rem' }}>
                      {new Date(entry.movement_date).toLocaleString('es-MX', {
                        day: '2-digit', month: '2-digit', year: 'numeric',
                        hour: '2-digit', minute: '2-digit',
                      })}
                    </td>
                    <td style={{ fontWeight: '500' }}>
                      {entry.movement_type.replace(/_/g, ' ')}
                    </td>
                    <td>
                      {entry.direction === 'IN' ? (
                        <span className="badge badge-in">
                          <HiOutlineArrowDownTray /> Entrada
                        </span>
                      ) : (
                        <span className="badge badge-out">
                          <HiOutlineArrowUpTray /> Salida
                        </span>
                      )}
                    </td>
                    <td style={{ textAlign: 'right' }}
                      className={entry.direction === 'IN' ? 'quantity-in' : 'quantity-out'}
                    >
                      {entry.direction === 'IN' ? '+' : '-'}
                      {Number(entry.quantity).toLocaleString()}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      ${Number(entry.unit_cost).toFixed(2)}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      ${Number(entry.total_cost).toLocaleString('es-MX', { minimumFractionDigits: 2 })}
                    </td>
                    <td style={{
                      textAlign: 'right', fontWeight: '700',
                      color: Number(entry.running_balance) > 0 ? 'var(--text-primary)' : 'var(--danger)',
                      fontSize: '0.95rem',
                    }}>
                      {Number(entry.running_balance).toLocaleString()}
                    </td>
                    <td style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                      {entry.reference_number || '—'}
                    </td>
                    <td style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                      {entry.registered_by || '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Resumen */}
          {kardex.entries.length > 0 && (
            <div style={{
              display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
              gap: '16px', marginTop: '20px',
            }}>
              <div className="card" style={{ textAlign: 'center', padding: '20px' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
                  Total Movimientos
                </div>
                <div style={{ fontSize: '1.5rem', fontWeight: '800' }}>{kardex.entries.length}</div>
              </div>
              <div className="card" style={{ textAlign: 'center', padding: '20px' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
                  Entradas
                </div>
                <div style={{ fontSize: '1.5rem', fontWeight: '800', color: 'var(--color-in)' }}>
                  {kardex.entries.filter(e => e.direction === 'IN').length}
                </div>
              </div>
              <div className="card" style={{ textAlign: 'center', padding: '20px' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
                  Salidas
                </div>
                <div style={{ fontSize: '1.5rem', fontWeight: '800', color: 'var(--color-out)' }}>
                  {kardex.entries.filter(e => e.direction === 'OUT').length}
                </div>
              </div>
              <div className="card" style={{ textAlign: 'center', padding: '20px' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
                  Stock Final
                </div>
                <div style={{ fontSize: '1.5rem', fontWeight: '800', color: 'var(--accent-primary)' }}>
                  {Number(kardex.current_stock).toLocaleString()}
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
