/**
 * pages/CategoriesPage.jsx
 * Página de gestión de categorías con CRUD.
 */
import { useState, useEffect } from 'react';
import { HiOutlinePlus, HiOutlinePencil, HiOutlineTrash, HiOutlineXMark } from 'react-icons/hi2';
import { categoriesApi } from '../api/inventory';
import { useToast } from '../context/ToastContext';

export default function CategoriesPage() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ name: '', description: '' });
  const { showSuccess, showError } = useToast();

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      setCategories(await categoriesApi.getAll());
    } catch { showError('Error cargando categorías'); }
    finally { setLoading(false); }
  };

  const openCreate = () => { setEditing(null); setForm({ name: '', description: '' }); setShowModal(true); };

  const openEdit = (cat) => { setEditing(cat); setForm({ name: cat.name, description: cat.description || '' }); setShowModal(true); };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editing) {
        await categoriesApi.update(editing.id, form);
        showSuccess('Categoría actualizada');
      } else {
        await categoriesApi.create(form);
        showSuccess('Categoría creada');
      }
      setShowModal(false);
      loadData();
    } catch (err) { showError(err.response?.data?.detail || 'Error al guardar'); }
  };

  const handleDelete = async (cat) => {
    if (!confirm(`¿Eliminar "${cat.name}"?`)) return;
    try { await categoriesApi.delete(cat.id); showSuccess('Categoría eliminada'); loadData(); }
    catch (err) { showError(err.response?.data?.detail || 'Error al eliminar'); }
  };

  if (loading) return <div className="loading-center"><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header">
        <div><h1>Categorías</h1><p>Clasificación de productos</p></div>
        <button className="btn btn-primary" onClick={openCreate} id="btn-new-category"><HiOutlinePlus /> Nueva Categoría</button>
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead><tr><th>Nombre</th><th>Descripción</th><th>Fecha Creación</th><th>Acciones</th></tr></thead>
          <tbody>
            {categories.length === 0 ? (
              <tr><td colSpan="4"><div className="empty-state"><div className="empty-icon">🏷️</div><h3>Sin categorías</h3></div></td></tr>
            ) : categories.map((c) => (
              <tr key={c.id}>
                <td style={{ fontWeight: '500', color: 'var(--text-primary)' }}>{c.name}</td>
                <td>{c.description || '—'}</td>
                <td>{new Date(c.created_at).toLocaleDateString('es-MX')}</td>
                <td>
                  <div style={{ display: 'flex', gap: '6px' }}>
                    <button className="btn btn-icon btn-secondary" onClick={() => openEdit(c)}><HiOutlinePencil /></button>
                    <button className="btn btn-icon btn-danger" onClick={() => handleDelete(c)}><HiOutlineTrash /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editing ? 'Editar Categoría' : 'Nueva Categoría'}</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}><HiOutlineXMark /></button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Nombre *</label>
                <input className="form-input" value={form.name} onChange={(e) => setForm({...form, name: e.target.value})}
                  required placeholder="Nombre de la categoría" id="input-category-name" />
              </div>
              <div className="form-group">
                <label className="form-label">Descripción</label>
                <textarea className="form-textarea" value={form.description} onChange={(e) => setForm({...form, description: e.target.value})}
                  placeholder="Descripción opcional" id="input-category-description" />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancelar</button>
                <button type="submit" className="btn btn-primary" id="btn-save-category">{editing ? 'Guardar' : 'Crear'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
