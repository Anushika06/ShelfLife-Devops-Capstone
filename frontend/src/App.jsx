import { useCallback, useEffect, useMemo, useState } from 'react'
import { api } from './api.js'
import UseFirst from './components/UseFirst.jsx'
import ItemList from './components/ItemList.jsx'
import ItemForm from './components/ItemForm.jsx'

const EMPTY_FILTERS = { location: '', status: '', q: '' }

export default function App() {
  const [meta, setMeta] = useState(null)
  const [summary, setSummary] = useState(null)
  const [allItems, setAllItems] = useState([])
  const [items, setItems] = useState([])
  const [filters, setFilters] = useState(EMPTY_FILTERS)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')
  const [editing, setEditing] = useState(null) // null = closed, {} = new item, item = edit
  const [notice, setNotice] = useState('')

  const refresh = useCallback(async (activeFilters) => {
    try {
      const [summaryData, everything, filtered] = await Promise.all([
        api.summary(),
        api.listItems({ sort: 'expiry' }),
        api.listItems({ ...activeFilters, sort: 'expiry' }),
      ])
      setSummary(summaryData)
      setAllItems(everything)
      setItems(filtered)
      setLoadError('')
    } catch (error) {
      setLoadError(error.message || 'Could not reach the ShelfLife API.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    api
      .meta()
      .then(setMeta)
      .catch(() => setMeta(null))
  }, [])

  useEffect(() => {
    // Debounce typing in the search box; other filter changes apply immediately.
    const timer = setTimeout(() => refresh(filters), filters.q ? 250 : 0)
    return () => clearTimeout(timer)
  }, [filters, refresh])

  useEffect(() => {
    if (!notice) return undefined
    const timer = setTimeout(() => setNotice(''), 3500)
    return () => clearTimeout(timer)
  }, [notice])

  const useFirst = useMemo(
    () => allItems.filter((item) => item.expiry_status === 'expired' || item.expiry_status === 'expiring'),
    [allItems],
  )

  const setFilter = (key, value) => setFilters((current) => ({ ...current, [key]: value }))
  const toggleStatus = (status) => setFilter('status', filters.status === status ? '' : status)

  async function handleSave(values) {
    if (editing?.id) {
      await api.updateItem(editing.id, values)
      setNotice(`Saved changes to ${values.name}.`)
    } else {
      await api.createItem(values)
      setNotice(`Added ${values.name}.`)
    }
    setEditing(null)
    await refresh(filters)
  }

  async function handleConsume(item) {
    try {
      const updated = await api.consumeItem(item.id, 1)
      setNotice(
        updated.quantity === 0 ? `Used the last of ${item.name}.` : `Used 1 ${item.unit} of ${item.name}.`,
      )
      await refresh(filters)
    } catch (error) {
      setNotice(error.message)
    }
  }

  async function handleDelete(item) {
    try {
      await api.deleteItem(item.id)
      setNotice(`Removed ${item.name}.`)
      await refresh(filters)
    } catch (error) {
      setNotice(error.message)
    }
  }

  const locations = meta?.locations ?? ['Fridge', 'Freezer', 'Pantry']
  const warningDays = summary?.expiry_warning_days ?? meta?.expiry_warning_days ?? 3

  return (
    <div className="page">
      <header className="masthead">
        <div className="brand">
          <img src="/favicon.svg" alt="" width="36" height="36" />
          <div>
            <h1>ShelfLife</h1>
            <p className="tagline">What is in the kitchen, and what to use first.</p>
          </div>
        </div>
        <button type="button" className="button primary" onClick={() => setEditing({})}>
          Add item
        </button>
      </header>

      {summary && (
        <nav className="tallies" aria-label="Pantry status">
          <button
            type="button"
            className={`tally ${filters.status === '' ? 'is-active' : ''}`}
            onClick={() => setFilter('status', '')}
          >
            <strong>{summary.total}</strong> items
          </button>
          <button
            type="button"
            className={`tally tally-expired ${filters.status === 'expired' ? 'is-active' : ''}`}
            onClick={() => toggleStatus('expired')}
          >
            <strong>{summary.expired}</strong> expired
          </button>
          <button
            type="button"
            className={`tally tally-expiring ${filters.status === 'expiring' ? 'is-active' : ''}`}
            onClick={() => toggleStatus('expiring')}
          >
            <strong>{summary.expiring_soon}</strong> use within {warningDays} days
          </button>
          <button
            type="button"
            className={`tally tally-low ${filters.status === 'low-stock' ? 'is-active' : ''}`}
            onClick={() => toggleStatus('low-stock')}
          >
            <strong>{summary.low_stock}</strong> running low
          </button>
        </nav>
      )}

      {loadError && (
        <div className="banner banner-error" role="alert">
          <p>
            <strong>The pantry could not be loaded.</strong> {loadError}
          </p>
          <p>Check that the backend is running and reachable at /api, then retry.</p>
          <button type="button" className="button" onClick={() => refresh(filters)}>
            Retry
          </button>
        </div>
      )}

      <UseFirst items={useFirst} loading={loading} onConsume={handleConsume} />

      <section className="inventory" aria-labelledby="inventory-heading">
        <div className="inventory-head">
          <h2 id="inventory-heading">Inventory</h2>
          <div className="controls">
            <div className="segmented" role="group" aria-label="Storage location">
              {['', ...locations].map((location) => (
                <button
                  key={location || 'all'}
                  type="button"
                  aria-pressed={filters.location === location}
                  onClick={() => setFilter('location', location)}
                >
                  {location || 'All'}
                  {location && summary ? <span className="count">{summary.by_location[location] ?? 0}</span> : null}
                </button>
              ))}
            </div>
            <label className="search">
              <span className="visually-hidden">Search items</span>
              <input
                type="search"
                placeholder="Search by name or note"
                value={filters.q}
                onChange={(event) => setFilter('q', event.target.value)}
              />
            </label>
          </div>
        </div>

        <ItemList
          items={items}
          loading={loading}
          filtered={filters.location !== '' || filters.status !== '' || filters.q !== ''}
          onClearFilters={() => setFilters(EMPTY_FILTERS)}
          onAdd={() => setEditing({})}
          onEdit={setEditing}
          onConsume={handleConsume}
          onDelete={handleDelete}
        />
      </section>

      <footer className="footer">
        <span>
          {meta ? `${meta.service} ${meta.version}` : 'API version unknown'}
          {meta?.environment ? ` (${meta.environment})` : ''}
        </span>
        <a href="/api/docs" target="_blank" rel="noreferrer">
          API docs
        </a>
      </footer>

      {editing && (
        <ItemForm item={editing} meta={meta} onCancel={() => setEditing(null)} onSave={handleSave} />
      )}

      <div className="toast" role="status" aria-live="polite">
        {notice}
      </div>
    </div>
  )
}
