import { useEffect, useState } from 'react'
import { countdownLabel, formatDate, formatQuantity, statusText } from '../format.js'

export default function ItemList({ items, loading, filtered, onClearFilters, onAdd, onEdit, onConsume, onDelete }) {
  if (loading) {
    return <p className="muted list-message">Loading the inventory…</p>
  }
  if (items.length === 0) {
    return filtered ? (
      <div className="list-message">
        <p>No items match these filters.</p>
        <button type="button" className="button" onClick={onClearFilters}>
          Show all items
        </button>
      </div>
    ) : (
      <div className="list-message">
        <p>The pantry is empty. Add what you bought today and ShelfLife will tell you what to use first.</p>
        <button type="button" className="button primary" onClick={onAdd}>
          Add item
        </button>
      </div>
    )
  }

  return (
    <ul className="rows">
      {items.map((item) => (
        <ItemRow key={item.id} item={item} onEdit={onEdit} onConsume={onConsume} onDelete={onDelete} />
      ))}
    </ul>
  )
}

function ItemRow({ item, onEdit, onConsume, onDelete }) {
  const [confirming, setConfirming] = useState(false)

  useEffect(() => {
    if (!confirming) return undefined
    const timer = setTimeout(() => setConfirming(false), 4000)
    return () => clearTimeout(timer)
  }, [confirming])

  return (
    <li className={`row row-${item.expiry_status}`}>
      <div className="row-main">
        <span className="row-name">{item.name}</span>
        <span className="row-sub">
          {item.category} in the {item.location.toLowerCase()}
          {item.notes ? `. ${item.notes}` : ''}
        </span>
      </div>
      <div className="row-qty">
        <span>{formatQuantity(item.quantity, item.unit)}</span>
        {item.low_stock && <span className="flag-low">Running low</span>}
      </div>
      <div className="row-expiry">
        <span className={`pill pill-${item.expiry_status}`}>{statusText(item)}</span>
        <span className="row-date">
          {item.expiry_date ? `${formatDate(item.expiry_date)} (${countdownLabel(item).toLowerCase()})` : ''}
        </span>
      </div>
      <div className="row-actions">
        <button type="button" className="button small" onClick={() => onConsume(item)} disabled={item.quantity <= 0}>
          Use 1
        </button>
        <button type="button" className="button small ghost" onClick={() => onEdit(item)}>
          Edit
        </button>
        {confirming ? (
          <button type="button" className="button small danger" onClick={() => onDelete(item)}>
            Confirm remove
          </button>
        ) : (
          <button
            type="button"
            className="button small ghost"
            onClick={() => setConfirming(true)}
            aria-label={`Remove ${item.name}`}
          >
            Remove
          </button>
        )}
      </div>
    </li>
  )
}
