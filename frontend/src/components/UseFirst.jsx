import { countdownLabel, formatQuantity } from '../format.js'

// The "use these first" shelf: everything expired or close to expiry, soonest first,
// drawn as jar labels so the most urgent food is the first thing you see.
export default function UseFirst({ items, loading, onConsume }) {
  return (
    <section className="use-first" aria-labelledby="use-first-heading">
      <h2 id="use-first-heading">Use these first</h2>
      {loading ? (
        <p className="muted">Checking dates…</p>
      ) : items.length === 0 ? (
        <p className="use-first-empty">Nothing is close to its date. Add expiry dates to new items to keep this shelf useful.</p>
      ) : (
        <ol className="shelf">
          {items.map((item) => (
            <li key={item.id} className={`jar jar-${item.expiry_status}`}>
              <span className="jar-lid" aria-hidden="true" />
              <span className="jar-countdown">{countdownLabel(item)}</span>
              <span className="jar-name">{item.name}</span>
              <span className="jar-meta">
                {item.location}, {formatQuantity(item.quantity, item.unit)}
              </span>
              {item.quantity > 0 && (
                <button type="button" className="jar-action" onClick={() => onConsume(item)}>
                  Use 1
                </button>
              )}
            </li>
          ))}
        </ol>
      )}
    </section>
  )
}
