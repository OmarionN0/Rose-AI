import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Shield, Activity, Bell, Monitor, RefreshCw, Lock, LogOut } from 'lucide-react';
import './style.css';

function App() {
  const [token, setToken] = useState('');
  const [input, setInput] = useState('');
  const [summary, setSummary] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [events, setEvents] = useState([]);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  async function api(path, options={}) {
    const response = await fetch('/api'+path, { ...options, headers: { 'Authorization': 'Bearer '+token, 'Content-Type': 'application/json', ...(options.headers||{}) }, cache:'no-store' });
    if (!response.ok) throw new Error(response.status === 401 ? 'Authentication failed. Check your token.' : 'Request failed ('+response.status+')');
    return response.json();
  }
  async function refresh() {
    if (!token) return;
    setBusy(true);
    try {
      const [s,a,e] = await Promise.all([api('/summary'),api('/alerts'),api('/events?limit=100')]);
      setSummary(s);setAlerts(a);setEvents(e);setError('');
    } catch(err) {setError(err.message);} finally {setBusy(false);}
  }
  useEffect(()=>{ if(!token)return; refresh(); const timer=setInterval(refresh,15000);return()=>clearInterval(timer); },[token]);
  async function triage(id,status) { try {await api('/alerts/'+id,{method:'PATCH',body:JSON.stringify({status})});await refresh();} catch(e){setError(e.message);} }
  const metrics=events.filter(e=>e.event_type==='system_metrics').slice(0,10);
  return <div className="app">
    <aside><div className="brand"><Shield size={27}/> <span>R.O.S.E.<small>SECURITY CENTER</small></span></div><nav><a href="#overview"><Activity size={18}/> Overview</a><a href="#alerts"><Bell size={18}/> Alerts</a><a href="#hosts"><Monitor size={18}/> Hosts</a></nav><div className="foot">Local-first SOC Lab<br/>Read-only collectors</div></aside>
    <main><header><div><p className="eyebrow">SECURITY OPERATIONS</p><h1>Security overview</h1><p className="muted">Windows + WSL2 monitoring • local dashboard</p></div><div className="actions">{token&&<><button onClick={refresh}><RefreshCw size={16}/> {busy?'Loading':'Refresh'}</button><button onClick={()=>{setToken('');setInput('');setSummary(null);setAlerts([]);setEvents([]);}}><LogOut size={16}/> Lock</button></>}</div></header>
      {!token ? <section className="panel login"><Lock size={28}/><h2>Connect to local SOC API</h2><p className="muted">Enter your local ROSE_SOC_TOKEN. It stays in memory only, never localStorage or GitHub.</p><form onSubmit={e=>{e.preventDefault();setToken(input);setInput('');}}><input type="password" autoComplete="off" aria-label="API token" value={input} onChange={e=>setInput(e.target.value)} placeholder="Paste local API token" required/><button type="submit">Unlock dashboard</button></form></section> : <>
      {error&&<div role="alert" className="error">{error}</div>}
      <section className="stats" id="overview"><div className="panel"><span className="muted">Total events</span><strong>{summary?.events??'—'}</strong></div><div className="panel"><span className="muted">Open alerts</span><strong>{summary?.open_alerts??'—'}</strong></div><div className="panel"><span className="muted">Recent host metrics</span><strong>{metrics.length}</strong></div></section>
      <section className="panel" id="alerts"><div className="sectionhead"><h2>Security alerts</h2><span className="muted">Latest 100</span></div><div className="tablewrap"><table><thead><tr><th>ID</th><th>Rule</th><th>Severity</th><th>Status</th><th>Investigate</th></tr></thead><tbody>{alerts.length===0?<tr><td colSpan="5" className="muted">No alerts recorded</td></tr>:alerts.map(a=><tr key={a.id}><td>#{a.id}</td><td>{a.rule}</td><td><span className={'severity '+a.severity}>{a.severity}</span></td><td>{a.status}</td><td><select aria-label={'Status for alert '+a.id} value={a.status} onChange={e=>triage(a.id,e.target.value)}>{['open','investigating','resolved','false_positive'].map(x=><option key={x} value={x}>{x.replace('_',' ')}</option>)}</select></td></tr>)}</tbody></table></div></section>
      <section className="panel" id="hosts"><div className="sectionhead"><h2>Host health</h2><span className="muted">Last 10 reported samples</span></div>{metrics.length===0?<p className="muted">No live host samples yet. Start the Windows and WSL2 collectors.</p>:<div className="hostgrid">{metrics.map(m=>{let d={};try{d=JSON.parse(m.details)}catch{}return <div className="host" key={m.id}><div className="hosttitle"><Monitor size={18}/>{m.host}</div><p>CPU: <b>{d.cpu_percent??'—'}%</b> · RAM: <b>{d.memory_percent??'—'}%</b></p><p className="muted">{new Date(m.timestamp).toLocaleString()}</p></div>})}</div>}</section>
      <section className="panel"><div className="sectionhead"><h2>Recent events</h2><span className="muted">Last 100</span></div><div className="tablewrap"><table><thead><tr><th>Time</th><th>Host</th><th>Type</th><th>Source</th></tr></thead><tbody>{events.length===0?<tr><td colSpan="4" className="muted">No events yet</td></tr>:events.map(e=><tr key={e.id}><td>{new Date(e.timestamp).toLocaleString()}</td><td>{e.host}</td><td>{e.event_type}</td><td>{e.source}</td></tr>)}</tbody></table></div></section>
      </>}
      <footer>R.O.S.E. SOC Lab • Educational prototype • No automatic remediation</footer>
    </main></div>;
}
createRoot(document.getElementById('root')).render(<App/>);
