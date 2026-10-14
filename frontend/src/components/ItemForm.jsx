import { useEffect, useRef, useState } from 'react'

const FALLBACK = {
  categories: ['Produce', 'Dairy', 'Meat & Fish', 'Bakery', 'Grains & Pasta', 'Other'],
  locations: ['Fridge', 'Freezer', 'Pantry'],
  units: ['pcs', 'g', 'kg', 'ml', 'L', 'pack'],
}

function initialValues(item) {
  return {
    name: item.name ?? '',
    category: item.category ?? 'Other',
    location: item.location ?? 'Fridge',
    quantity: item.quantity ?? 1,
    unit: item.unit ?? 'pcs',
    min_quantity: item.min_quantity ?? 0,
    expiry_date: item.expiry_date ?? '',
    notes: item.notes ?? '',
  }
}

export default function ItemForm({ item, meta, onCancel, onSave }) {
  const dialogRef = useRef(null)
  const [values, setValues] = useState(() => initialValues(item))
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const options = meta ?? FALLBACK
  const isEdit = Boolean(item.id)

  useEffect(() => {
    const dialog = dialogRef.current
    if (dialog && !dialog.open) dialog.showModal()
  }, [])

  const update = (field) => (event) => setValues((current) => ({ ...current, [field]: event.target.value }))

  async function submit(event) {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      await onSave({
        ...values,
        name: values.name.trim(),
        quantity: Number(values.quantity),
        min_quantity: Number(values.min_quantity || 0),
        expiry_date: values.expiry_date || null,
        notes: values.notes.trim() || null,
      })
    } catch (saveError) {
      setError(saveError.message)
      setSaving(false)
    }
  }

  return (
    <dialog ref={dialogRef} className="sheet" onCancel={onCancel} aria-labelledby="item-form-title">
      <form onSubmit={submit}>
        <h2 id="item-form-title">{isEdit ? `Edit ${item.name}` : 'Add an item'}</h2>

        <label className="field field-wide">
          <span>Name</span>
          <input required maxLength={120} value={values.name} onChange={update('name')} autoFocus />
        </label>

        <label className="field">
          <span>Category</span>
          <select value={values.category} onChange={update('category')}>
            {options.categories.map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>Stored in</span>
          <select value={values.location} onChange={update('location')}>
            {options.locations.map((l) => (
              <option key={l}>{l}</option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>Quantity</span>
          <input type="number" min="0" step="any" required value={values.quantity} onChange={update('quantity')} />
        </label>

        <label className="field">
          <span>Unit</span>
          <select value={values.unit} onChange={update('unit')}>
            {options.units.map((u) => (
              <option key={u}>{u}</option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>Use by</span>
          <input type="date" value={values.expiry_date} onChange={update('expiry_date')} />
        </label>

        <label className="field">
          <span>Warn when at or below</span>
          <input type="number" min="0" step="any" value={values.min_quantity} onChange={update('min_quantity')} />
        </label>

        <label className="field field-wide">
          <span>Note</span>
          <textarea rows="2" maxLength={500} value={values.notes} onChange={update('notes')} />
        </label>

        {error && (
          <p className="form-error field-wide" role="alert">
            {error}
          </p>
        )}

        <div className="sheet-actions field-wide">
          <button type="button" className="button ghost" onClick={onCancel}>
            Cancel
          </button>
          <button type="submit" className="button primary" disabled={saving}>
            {saving ? 'Saving…' : isEdit ? 'Save changes' : 'Add item'}
          </button>
        </div>
      </form>
    </dialog>
  )
}
