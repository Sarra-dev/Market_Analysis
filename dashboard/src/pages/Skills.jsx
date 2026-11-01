import { useEffect, useState } from 'react';
import { getTopSkills } from '../api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function Skills() {
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTopSkills()
      .then(r => setSkills(r.data))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ padding: '24px' }}>
      <h1 style={{ fontSize: '22px', fontWeight: 700, color: '#e2e8f0', marginBottom: '16px' }}>
        Top Skills
      </h1>
      {loading ? (
        <p style={{ color: '#64748b' }}>Loading...</p>
      ) : (
        <BarChart width={800} height={500} data={skills} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis type="category" dataKey="skill" width={120} />
          <Tooltip />
          <Bar dataKey="count" fill="#38bdf8" />
        </BarChart>
      )}
    </div>
  );
}