// Display helpers shared by the components.

export function countdownLabel(item) {
  const days = item.days_until_expiry
  if (days === null || days === undefined) return 'No date'
  if (days === 0) return 'Today'
  if (days === 1) return 'Tomorrow'
  if (days === -1) return 'Yesterday'
  if (days < 0) return `${Math.abs(days)} days ago`
  return `${days} days`
}

export function statusText(item) {
  switch (item.expiry_status) {
    case 'expired':
      return 'Expired'
    case 'expiring':
      return 'Use soon'
    case 'fresh':
      return 'Fresh'
    default:
      return 'No expiry date'
  }
}

export function formatQuantity(quantity, unit) {
  const value = Number.isInteger(quantity) ? quantity : Number(quantity.toFixed(2))
  return `${value} ${unit}`
}

export function formatDate(iso) {
  if (!iso) return '—'
  const [year, month, day] = iso.split('-').map(Number)
  return new Date(year, month - 1, day).toLocaleDateString(undefined, {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}
