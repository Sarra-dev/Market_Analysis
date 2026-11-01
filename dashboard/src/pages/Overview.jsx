import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, PieChart, Pie, Cell, ResponsiveContainer, Legend } from 'recharts';
import { getOverview, getByCountry, getTopSkills, getByContract } from '../api';
import KpiCard from '../components/KpiCard';

const COLORS = ['#38bdf8','#818cf8','#34d399','#fb923c','#f472b6'];

export default function Overview() {
  const [overview, setOverview]   = useState(null);
  const [countries, setCountries] = useState([]);
  const [skills, setSkills]       = useState([]);
  const [contracts, setContracts] = useState([]);

  useEffect(() => {
    getOverview().then(r => setOverview(r.data));
    getByCountry().then(r => setCountries(r.data));
    getTopSkills().then(r => setSkills(r.data.slice(0, 10)));
    getByContract().then(r => setContracts(r.data));
  }, []);

  return (
    <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <h1 style={{ fontSize: '22px', fontWeight: 700 }}>Market Overview</h1>

      {/* KPI Cards */}
      <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
        <KpiCard label="Total Jobs"     value={overview?.total_jobs}      color="#38bdf8" />
        <KpiCard label="Companies"      value={overview?.total_companies}  color="#818cf8" />
        <KpiCard label="Countries"      value={overview?.total_countries}  color="#34d399" />
        <KpiCard label="Senior Roles"   value={overview?.senior_roles}     color="#fb923c" />
        <KpiCard label="Remote Roles"   value={overview?.remote_roles}     color="#f472b6" />
      </div>

      {/* Charts Row */}
      <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>

        {/* Top Skills Bar Chart */}
        <div style={{ background: '#1e293b', borderRadius: '12px', padding: '20px', flex: 2, minWidth: '300px' }}>
          <h2 style={{ fontSize: '15px', marginBottom: '16px', color: '#94a3b8' }}>Top 10 Skills</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={skills} layout="vertical">
              <XAxis type="number" stroke="#475569" />
              <YAxis dataKey="skill" type="category" stroke="#475569" width={100} tick={{ fontSize: 12 }} />
              <Tooltip contentStyle={{ background: '#0f172a', border: 'none' }} />
              <Bar dataKey="count" fill="#38bdf8" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Jobs by Country Pie */}
        <div style={{ background: '#1e293b', borderRadius: '12px', padding: '20px', flex: 1, minWidth: '250px' }}>
          <h2 style={{ fontSize: '15px', marginBottom: '16px', color: '#94a3b8' }}>Jobs by Country</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={countries} dataKey="count" nameKey="country"
                cx="50%" cy="50%" outerRadius={100} label>
                {countries.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={{ background: '#0f172a', border: 'none' }} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

      </div>

      {/* Contract Types */}
      <div style={{ background: '#1e293b', borderRadius: '12px', padding: '20px' }}>
        <h2 style={{ fontSize: '15px', marginBottom: '16px', color: '#94a3b8' }}>Contract Types</h2>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={contracts}>
            <XAxis dataKey="contrat" stroke="#475569" />
            <YAxis stroke="#475569" />
            <Tooltip contentStyle={{ background: '#0f172a', border: 'none' }} />
            <Bar dataKey="count" fill="#818cf8" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}