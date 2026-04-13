/**
 * pages/MovementsPage.jsx
 * Página de registro y listado de movimientos de inventario.
 * 
 * Permite registrar entradas (COMPRA, DEVOLUCIÓN) y salidas
 * (VENTA, MERMA). Muestra la lista de movimientos recientes
 * con badges de dirección IN/OUT.
 */
import { useState, useEffect } from 'react';
import { HiOutlinePlus, HiOutlineXMark, HiOutlineArrowDownTray, HiOutlineArrowUpTray } from 'react-icons/hi2';
import { movementsApi, productsApi } from '../api/inventory';
import { useToast } from '../context/ToastContext';

export default function MovementsPage() {
  const [movements, setMovements] = useState([]);
  const [products, setProducts] = useState([]);
  const [movementTypes, setMovementTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({
    product_id: '', movement_type_id: '', quantity: '', unit_cost: '', reference_number: '', notes: '',
  });
  const { showSuccess, showError } = useToast();

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [movs, prods, types] = await Promise.all([
        movementsApi.getAll(),
        productsApi.getAll(),
        movementsApi.getTypes(),
      ]);
      setMovements(movs);
      setProducts(prods);
      setMovementTypes(types);
    } catch { showError('Error cargando datos'); }
    finally { setLoading(false); }
  };

  const openCreate = () => {
    setForm({ product_id: '', movement_type_id: '', quantity: '', unit_cost: '', reference_number: '', notes: '' });
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await movementsApi.create({
        ...form,
        quantity: parseFloat(form.quantity),
        unit_cost: parseFloat(form.unit_cost || '0'),
      });
      showSuccess('Movimiento registrado');
      setShowModal(false);
      loadData();
    } catch (err) {
      showError(err.response?.data?.detail || 'Error al registrar');
    }
  };

  // Agrupar tipos por dirección para el select
  const typesIn = movementTypes.filter(t => t.direction === 'IN');
  const typesOut = movementTypes.filter(t => t.direction === 'OUT');

  if (loading) return <div className="loading-center"><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header">
        <div><h1>Movimientos</h1><p>Registro de entradas y salidas de inventario</p></div>
        <button className="btn btn-primary" onClick={openCreate} id="btn-new-movement"><HiOutlinePlus /> Nuevo Movimiento</button>
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Producto</th>
              <th>Tipo</th>
              <th>Dirección</th>
              <th style={{ textAlign: 'right' }}>Cantidad</th>
              <th style={{ textAlign: 'right' }}>Costo Unit.</th>
              <th style={{ textAlign: 'right' }}>Total</th>
              <th>Referencia</th>
            </tr>
          </thead>
          <tbody>
            {movements.length === 0 ? (
              <tr><td colSpan="8"><div className="empty-state"><div className="empty-icon">📋</div><h3>Sin movimientos</h3><p>Registra tu primer movimiento</p></div></td></tr>
            ) : movements.map((m) => (
              <tr key={m.id}>
                <td style={{ whiteSpace: 'nowrap' }}>
                  {new Date(m.movement_date).toLocaleString('es-MX', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                </td>
                <td style={{ fontWeight: '500', color: 'var(--text-primary)' }}>
                  {m.product?.name || '—'}
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                    {m.product?.sku}
                  </div>
                </td>
                <td>{m.movement_type?.name?.replace(/_/g, ' ') || '—'}</td>
                <td>
                  {m.movement_type?.direction === 'IN' ? (
                    <span className="badge badge-in"><HiOutlineArrowDownTray /> Entrada</span>
                  ) : (
                    <span className="badge badge-out"><HiOutlineArrowUpTray /> Salida</span>
                  )}
                </td>
                <td style={{ textAlign: 'right' }} className={m.movement_type?.direction === 'IN' ? 'quantity-in' : 'quantity-out'}>
                  {m.movement_type?.direction === 'IN' ? '+' : '-'}{Number(m.quantity).toLocaleString()}
                </td>
                <td style={{ textAlign: 'right' }}>${Number(m.unit_cost).toFixed(2)}</td>
                <td style={{ textAlign: 'right', fontWeight: '500' }}>
                  ${(Number(m.quantity) * Number(m.unit_cost)).toLocaleString('es-MX', { minimumFractionDigits: 2 })}
                </td>
                <td style={{ fontSize: '0.82rem' }}>{m.reference_number || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Registrar Movimiento</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}><HiOutlineXMark /></button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Producto *</label>
                <select className="form-select" value={form.product_id} onChange={(e) => setForm({...form, product_id: e.target.value})} required id="select-movement-product">
                  <option value="">Seleccionar producto</option>
                  {products.map(p => <option key={p.id} value={p.id}>{p.sku} — {p.name}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Tipo de Movimiento *</label>
                <select className="form-select" value={form.movement_type_id} onChange={(e) => setForm({...form, movement_type_id: e.target.value})} required id="select-movement-type">
                  <option value="">Seleccionar tipo</option>
                  <optgroup label="📥 Entradas">
                    {typesIn.map(t => <option key={t.id} value={t.id}>{t.name.replace(/_/g, ' ')} — {t.description}</option>)}
                  </optgroup>
                  <optgroup label="📤 Salidas">
                    {typesOut.map(t => <option key={t.id} value={t.id}>{t.name.replace(/_/g, ' ')} — {t.description}</option>)}
                  </optgroup>
                </select>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Cantidad *</label>
                  <input className="form-input" type="number" step="0.0001" min="0.0001" value={form.quantity}
                    onChange={(e) => setForm({...form, quantity: e.target.value})} required placeholder="100" id="input-movement-qty" />
                </div>
                <div className="form-group">
                  <label className="form-label">Costo Unitario</label>
                  <input className="form-input" type="number" step="0.01" min="0" value={form.unit_cost}
                    onChange={(e) => setForm({...form, unit_cost: e.target.value})} placeholder="25.50" id="input-movement-cost" />
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">N° Referencia</label>
                <input className="form-input" value={form.reference_number} onChange={(e) => setForm({...form, reference_number: e.target.value})}
                  placeholder="FAC-2026-001" id="input-movement-ref" />
              </div>
              <div className="form-group">
                <label className="form-label">Notas</label>
                <textarea className="form-textarea" value={form.notes} onChange={(e) => setForm({...form, notes: e.target.value})}
                  placeholder="Observaciones del movimiento" id="input-movement-notes" />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancelar</button>
                <button type="submit" className="btn btn-primary" id="btn-save-movement">Registrar Movimiento</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
