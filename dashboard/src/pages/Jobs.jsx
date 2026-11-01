import { useEffect, useState } from 'react';
import { getJobs } from '../api';

export default function Jobs() {
  const [jobs, setJobs]       = useState([]);
  const [total, setTotal]     = useState(0);
  const [search, setSearch]   = useState('');
  const [country, setCountry] = useState('');
  const [offset, setOffset]   = useState(0);
  const [loading, setLoading] = useState(false);
  const limit = 50;

  const fetchJobs = () => {
    setLoading(true);
    getJobs({ search, country, limit, offset })
      .then(r => {
        setJobs(r.data.items);   // <-- was r.data, now r.data.items
        setTotal(r.data.total);  // <-- new: total count for pagination
      })
      .finally(() => setLoading(false));
  };

  // re-fetch whenever offset changes (pagination), and once on mount
  useEffect(() => { fetchJobs(); }, [offset]);

  const handleSearch = () => {
    setOffset(0);       // reset to first page on a new search
    fetchJobs();
  };

  return (
    <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <h1 style={{ fontSize: '22px', fontWeight: 700 }}>Job Listings</h1>

      {/* Filters */}
      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
        <input
          placeholder="Search jobs..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ padding: '10px 14px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#e2e8f0', flex: 1 }}
        />
        <select value={country} onChange={e => setCountry(e.target.value)}
          style={{ padding: '10px 14px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#e2e8f0' }}>
          <option value="">All Countries</option>
          <option value="USA">USA</option>
          <option value="United Kingdom">United Kingdom</option>
          <option value="Canada">Canada</option>
          <option value="Australia">Australia</option>
          <option value="Germany">Germany</option>
        </select>
        <button onClick={handleSearch}
          style={{ padding: '10px 20px', borderRadius: '8px', background: '#38bdf8', color: '#0f172a', fontWeight: 700, border: 'none', cursor: 'pointer' }}>
          Search
        </button>
      </div>

      {/* Results count */}
      {!loading && (
        <p style={{ color: '#64748b', fontSize: '13px' }}>
          Showing {jobs.length ? offset + 1 : 0}–{offset + jobs.length} of {total} jobs
        </p>
      )}

      {/* Table */}
      {loading ? <p style={{ color: '#64748b' }}>Loading...</p> : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ background: '#1e293b', color: '#64748b' }}>
                {['Title', 'Company', 'Location', 'Contract', 'Experience', 'Country', 'Date'].map(h => (
                  <th key={h} style={{ padding: '12px 16px', textAlign: 'left', borderBottom: '1px solid #334155' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {jobs.map(job => (
                <tr key={job.id} style={{ borderBottom: '1px solid #1e293b' }}
                  onMouseEnter={e => e.currentTarget.style.background = '#1e293b'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
                  <td style={{ padding: '12px 16px', color: '#38bdf8', fontWeight: 600 }}>{job.titre}</td>
                  <td style={{ padding: '12px 16px' }}>{job.entreprise}</td>
                  <td style={{ padding: '12px 16px', color: '#94a3b8' }}>{job.localisation}</td>
                  <td style={{ padding: '12px 16px' }}>{job.contrat ?? 'N/A'}</td>
                  <td style={{ padding: '12px 16px' }}>{job.experience ?? 'N/A'}</td>
                  <td style={{ padding: '12px 16px', color: '#34d399' }}>{job.source}</td>
                  <td style={{ padding: '12px 16px', color: '#64748b' }}>{job.date_publication}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination controls */}
      {!loading && total > limit && (
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', alignItems: 'center' }}>
          <button
            disabled={offset === 0}
            onClick={() => setOffset(Math.max(0, offset - limit))}
            style={{ padding: '8px 16px', borderRadius: '8px', border: '1px solid #334155', background: offset === 0 ? '#1e293b' : '#38bdf8', color: offset === 0 ? '#64748b' : '#0f172a', cursor: offset === 0 ? 'not-allowed' : 'pointer' }}>
            Previous
          </button>
          <span style={{ color: '#94a3b8', fontSize: '13px' }}>
            Page {Math.floor(offset / limit) + 1} of {Math.ceil(total / limit)}
          </span>
          <button
            disabled={offset + limit >= total}
            onClick={() => setOffset(offset + limit)}
            style={{ padding: '8px 16px', borderRadius: '8px', border: '1px solid #334155', background: offset + limit >= total ? '#1e293b' : '#38bdf8', color: offset + limit >= total ? '#64748b' : '#0f172a', cursor: offset + limit >= total ? 'not-allowed' : 'pointer' }}>
            Next
          </button>
        </div>
      )}
    </div>
  );
}