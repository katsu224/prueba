/**
 * pages/ProductsPage.jsx
 * Página de gestión de productos con CRUD completo.
 * 
 * Muestra una tabla de productos con acciones de crear,
 * editar y desactivar. Incluye un modal para el formulario.
 */
import { useState, useEffect } from 'react';
import { HiOutlinePlus, HiOutlinePencil, HiOutlineTrash, HiOutlineXMark } from 'react-icons/hi2';
import { productsApi, categoriesApi } from '../api/inventory';
import { useToast } from '../context/ToastContext';

export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({
    sku: '', name: '', description: '', unit_price: '',
    unit_measure: 'unidad', reorder_point: '10', category_id: '',
  });
  const { showSuccess, showError } = useToast();

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [prods, cats] = await Promise.all([
        productsApi.getAll(),
        categoriesApi.getAll(),
      ]);
      setProducts(prods);
      setCategories(cats);
    } catch (err) {
      showError('Error cargando datos');
    } finally {
      setLoading(false);
    }
  };

  const openCreate = () => {
    setEditing(null);
    setForm({ sku: '', name: '', description: '', unit_price: '', unit_measure: 'unidad', reorder_point: '10', category_id: '' });
    setShowModal(true);
  };

  const openEdit = (product) => {
    setEditing(product);
    setForm({
      sku: product.sku, name: product.name,
      description: product.description || '',
      unit_price: String(product.unit_price),
      unit_measure: product.unit_measure,
      reorder_point: String(product.reorder_point),
      category_id: product.category_id || '',
    });
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...form,
        unit_price: parseFloat(form.unit_price),
        reorder_point: parseInt(form.reorder_point),
        category_id: form.category_id || null,
      };

      if (editing) {
        const { sku, ...updateData } = payload;
        await productsApi.update(editing.id, updateData);
        showSuccess('Producto actualizado');
      } else {
        await productsApi.create(payload);
        showSuccess('Producto creado');
      }
      setShowModal(false);
      loadData();
    } catch (err) {
      showError(err.response?.data?.detail || 'Error al guardar');
    }
  };

  const handleDeactivate = async (product) => {
    if (!confirm(`¿Desactivar "${product.name}"?`)) return;
    try {
      await productsApi.deactivate(product.id);
      showSuccess('Producto desactivado');
      loadData();
    } catch (err) {
      showError(err.response?.data?.detail || 'Error al desactivar');
    }
  };

  if (loading) return <div className="loading-center"><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Productos</h1>
          <p>Gestión del catálogo de productos</p>
        </div>
        <button className="btn btn-primary" onClick={openCreate} id="btn-new-product">
          <HiOutlinePlus /> Nuevo Producto
        </button>
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>SKU</th>
              <th>Nombre</th>
              <th>Categoría</th>
              <th style={{ textAlign: 'right' }}>Precio Unit.</th>
              <th>Unidad</th>
              <th style={{ textAlign: 'right' }}>Reorden</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {products.length === 0 ? (
              <tr><td colSpan="8"><div className="empty-state"><div className="empty-icon">📦</div><h3>Sin productos</h3></div></td></tr>
            ) : products.map((p) => (
              <tr key={p.id}>
                <td style={{ fontFamily: 'monospace', color: 'var(--text-accent)' }}>{p.sku}</td>
                <td style={{ fontWeight: '500', color: 'var(--text-primary)' }}>{p.name}</td>
                <td>{p.category?.name || '—'}</td>
                <td style={{ textAlign: 'right' }}>${Number(p.unit_price).toFixed(2)}</td>
                <td>{p.unit_measure}</td>
                <td style={{ textAlign: 'right' }}>{p.reorder_point}</td>
                <td>
                  <span className={`badge ${p.is_active ? 'badge-success' : 'badge-danger'}`}>
                    {p.is_active ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
                <td>
                  <div style={{ display: 'flex', gap: '6px' }}>
                    <button className="btn btn-icon btn-secondary" onClick={() => openEdit(p)} title="Editar">
                      <HiOutlinePencil />
                    </button>
                    {p.is_active && (
                      <button className="btn btn-icon btn-danger" onClick={() => handleDeactivate(p)} title="Desactivar">
                        <HiOutlineTrash />
                      </button>
                    )}
                  </div>
                </td>
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
              <h2>{editing ? 'Editar Producto' : 'Nuevo Producto'}</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}><HiOutlineXMark /></button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">SKU *</label>
                  <input className="form-input" name="sku" value={form.sku} onChange={(e) => setForm({...form, sku: e.target.value})}
                    required disabled={!!editing} placeholder="PROD-001" id="input-product-sku" />
                </div>
                <div className="form-group">
                  <label className="form-label">Categoría</label>
                  <select className="form-select" value={form.category_id} onChange={(e) => setForm({...form, category_id: e.target.value})} id="select-product-category">
                    <option value="">Sin categoría</option>
                    {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Nombre *</label>
                <input className="form-input" value={form.name} onChange={(e) => setForm({...form, name: e.target.value})}
                  required placeholder="Nombre del producto" id="input-product-name" />
              </div>
              <div className="form-group">
                <label className="form-label">Descripción</label>
                <textarea className="form-textarea" value={form.description} onChange={(e) => setForm({...form, description: e.target.value})}
                  placeholder="Descripción opcional" id="input-product-description" />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Precio Unitario *</label>
                  <input className="form-input" type="number" step="0.01" min="0" value={form.unit_price}
                    onChange={(e) => setForm({...form, unit_price: e.target.value})} required placeholder="0.00" id="input-product-price" />
                </div>
                <div className="form-group">
                  <label className="form-label">Unidad de Medida</label>
                  <select className="form-select" value={form.unit_measure} onChange={(e) => setForm({...form, unit_measure: e.target.value})} id="select-product-unit">
                    <option value="unidad">Unidad</option>
                    <option value="kg">Kilogramo</option>
                    <option value="litro">Litro</option>
                    <option value="metro">Metro</option>
                    <option value="caja">Caja</option>
                    <option value="paquete">Paquete</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Punto de Reorden</label>
                  <input className="form-input" type="number" min="0" value={form.reorder_point}
                    onChange={(e) => setForm({...form, reorder_point: e.target.value})} id="input-product-reorder" />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancelar</button>
                <button type="submit" className="btn btn-primary" id="btn-save-product">
                  {editing ? 'Guardar Cambios' : 'Crear Producto'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
