import { NavLink } from 'react-router-dom';

const links = [
  { to: '/',       label: '📊 Overview' },
  { to: '/jobs',   label: '💼 Jobs'     },
  { to: '/skills', label: '🔧 Skills'   },
];

export default function Sidebar() {
  return (
    <aside style={{
      width: '220px', minHeight: '100vh',
      background: '#1e293b', padding: '24px 16px',
      display: 'flex', flexDirection: 'column', gap: '8px'
    }}>
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ color: '#38bdf8', fontSize: '18px', fontWeight: 700 }}>
          Market Analyser
        </h2>
        <p style={{ color: '#64748b', fontSize: '12px' }}>IT Job Market 2026</p>
      </div>

      {links.map(link => (
        <NavLink key={link.to} to={link.to} end
          style={({ isActive }) => ({
            padding: '10px 14px', borderRadius: '8px',
            textDecoration: 'none', fontSize: '14px',
            background: isActive ? '#0f172a' : 'transparent',
            color: isActive ? '#38bdf8' : '#94a3b8',
          })}>
          {link.label}
        </NavLink>
      ))}

      <div style={{ marginTop: 'auto', fontSize: '12px', color: '#475569' }}>
        <a href="https://www.kaggle.com" target="_blank"
          style={{ color: '#38bdf8', textDecoration: 'none' }}>
          📓 View Kaggle Analysis
        </a>
      </div>
    </aside>
  );
}