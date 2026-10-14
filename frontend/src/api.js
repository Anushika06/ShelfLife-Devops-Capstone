// Thin wrapper around the ShelfLife REST API. All paths are relative (/api/...),
// so the same build works behind Vite's dev proxy, Nginx, or a Kubernetes Ingress.

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (response.status === 204) return null
  const body = await response.json().catch(() => null)
  if (!response.ok) {
    throw new Error(describeError(response.status, body))
  }
  return body
}

function describeError(status, body) {
  const detail = body?.detail
  if (Array.isArray(detail) && detail.length > 0) {
    // FastAPI validation errors: [{loc: [..., "field"], msg: "..."}]
    return detail
      .map((d) => `${d.loc?.[d.loc.length - 1] ?? 'field'}: ${d.msg}`)
      .join('; ')
  }
  if (typeof detail === 'string') return detail
  if (status >= 500) return `The server could not complete the request (HTTP ${status}).`
  return `Request failed (HTTP ${status}).`
}

export const api = {
  meta: () => request('/api/meta'),
  summary: () => request('/api/summary'),
  listItems: (params = {}) => {
    const query = new URLSearchParams(
      Object.entries(params).filter(([, value]) => value !== '' && value != null),
    )
    const suffix = query.toString() ? `?${query}` : ''
    return request(`/api/items${suffix}`)
  },
  createItem: (item) => request('/api/items', { method: 'POST', body: JSON.stringify(item) }),
  updateItem: (id, item) => request(`/api/items/${id}`, { method: 'PUT', body: JSON.stringify(item) }),
  consumeItem: (id, amount = 1) =>
    request(`/api/items/${id}/consume`, { method: 'POST', body: JSON.stringify({ amount }) }),
  deleteItem: (id) => request(`/api/items/${id}`, { method: 'DELETE' }),
}
