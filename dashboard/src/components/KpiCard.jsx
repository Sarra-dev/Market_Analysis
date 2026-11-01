export default function KpiCard({ label, value, color = '#38bdf8' }) {
  return (
    <div style={{
      background: '#1e293b', borderRadius: '12px',
      padding: '24px', flex: 1, minWidth: '150px'
    }}>
      <p style={{ color: '#64748b', fontSize: '13px', marginBottom: '8px' }}>
        {label}
      </p>
      <p style={{ color, fontSize: '32px', fontWeight: 700 }}>
        {value?.toLocaleString() ?? '...'}
      </p>
    </div>
  );
}