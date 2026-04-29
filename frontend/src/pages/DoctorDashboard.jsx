import React, { useEffect, useState } from 'react';
import api from '../services/api';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const DoctorDashboard = () => {
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [readings, setReadings] = useState([]);
  const [prescriptions, setPrescriptions] = useState([]);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [orderType, setOrderType] = useState('CT_SCAN');
  const [departments, setDepartments] = useState([]);
  const [selectedDept, setSelectedDept] = useState('');
  const [message, setMessage] = useState('');
  const [docFile, setDocFile] = useState(null);
  const [docType, setDocType] = useState('MEDICAL_RECORD');

  useEffect(() => {
    fetchPatients();
    fetchDepartments();
  }, []);

  const fetchPatients = async () => {
    try {
      const res = await api.get('/patients/');
      setPatients(res.data.results || res.data);
    } catch {}
  };

  const fetchDepartments = async () => {
    try {
      const res = await api.get('/orders/departments/');
      setDepartments(res.data.results || res.data);
      if (res.data.results?.length) setSelectedDept(res.data.results[0].id);
      else if (res.data.length) setSelectedDept(res.data[0].id);
    } catch {}
  };

  const selectPatient = async (p) => {
    setSelectedPatient(p);
    try {
      const r = await api.get(`/patients/${p.id}/readings/`);
      setReadings(r.data.results || r.data);
      const pr = await api.get(`/doctors/prescriptions/?patient=${p.id}`);
      setPrescriptions(pr.data.results || pr.data);
    } catch {}
  };

  const handlePrescription = async (e) => {
    e.preventDefault();
    if (!selectedPatient) return;
    try {
      await api.post('/doctors/prescriptions/', {
        patient: selectedPatient.id,
        title,
        content,
      });
      setMessage('Prescription saved.');
      setTitle('');
      setContent('');
      const pr = await api.get(`/doctors/prescriptions/?patient=${selectedPatient.id}`);
      setPrescriptions(pr.data.results || pr.data);
    } catch {
      setMessage('Failed to save prescription.');
    }
  };

  const handleOrder = async (e) => {
    e.preventDefault();
    if (!selectedPatient || !selectedDept) return;
    try {
      await api.post('/orders/', {
        patient: selectedPatient.id,
        department: selectedDept,
        order_type: orderType,
      });
      setMessage('Order created.');
    } catch {
      setMessage('Failed to create order.');
    }
  };

  const handleDocUpload = async (e) => {
    e.preventDefault();
    if (!docFile) return;
    const formData = new FormData();
    formData.append('file', docFile);
    formData.append('document_type', docType);
    try {
      await api.post('/documents/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setMessage('Document uploaded securely.');
      setDocFile(null);
    } catch {
      setMessage('Document upload failed.');
    }
  };

  const chartData = readings.map((r) => ({
    name: new Date(r.timestamp).toLocaleDateString(),
    heart_rate: r.heart_rate,
    sys: r.blood_pressure_sys,
    dia: r.blood_pressure_dia,
    temp: r.temperature,
  })).reverse();

  const computeTrend = (values) => {
    if (values.length < 3) return null;
    const early = values.slice(0, 3).reduce((a, b) => a + b, 0) / 3;
    const late = values.slice(-3).reduce((a, b) => a + b, 0) / 3;
    return { early, late };
  };

  const trendBadge = (label, value, low, high) => {
    if (!value) return null;
    const { early, late } = value;
    const earlyDist = Math.min(Math.abs(early - low), Math.abs(early - high));
    const lateDist = Math.min(Math.abs(late - low), Math.abs(late - high));
    let text = 'Stable';
    let color = 'bg-gray-100 text-gray-700';
    if (lateDist < earlyDist) {
      text = 'Improving';
      color = 'bg-green-100 text-green-700';
    } else if (lateDist > earlyDist) {
      text = 'Worsening';
      color = 'bg-red-100 text-red-700';
    }
    return (
      <span className={`text-xs font-semibold px-2 py-1 rounded ${color}`}>
        {label}: {text}
      </span>
    );
  };

  const hrTrend = computeTrend(readings.map((r) => r.heart_rate).filter(Boolean));
  const sysTrend = computeTrend(readings.map((r) => r.blood_pressure_sys).filter(Boolean));
  const diaTrend = computeTrend(readings.map((r) => r.blood_pressure_dia).filter(Boolean));

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold mb-4">Doctor Dashboard</h1>
      {message && <div className="bg-green-100 text-green-700 p-2 rounded mb-4">{message}</div>}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
        <div className="bg-white p-4 rounded shadow lg:col-span-1">
          <h2 className="font-semibold mb-2">Patients</h2>
          <ul className="divide-y max-h-96 overflow-auto">
            {patients.map((p) => (
              <li key={p.id} className="py-2 cursor-pointer hover:bg-gray-50" onClick={() => selectPatient(p)}>
                <div className="font-medium">{p.user}</div>
                <div className="text-xs text-gray-500">Blood: {p.blood_type || 'N/A'}</div>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-white p-4 rounded shadow lg:col-span-2">
          {selectedPatient ? (
            <>
              <h2 className="font-semibold mb-2">{selectedPatient.user} — Readings</h2>
              {chartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="heart_rate" stroke="#8884d8" />
                    <Line type="monotone" dataKey="sys" stroke="#82ca9d" />
                    <Line type="monotone" dataKey="dia" stroke="#ffc658" />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-gray-500">No readings.</p>
              )}

              {readings.length >= 3 && (
                <div className="flex flex-wrap gap-2 mt-3 mb-3">
                  {trendBadge('Heart Rate', hrTrend, 60, 100)}
                  {trendBadge('BP Systolic', sysTrend, 90, 120)}
                  {trendBadge('BP Diastolic', diaTrend, 60, 80)}
                </div>
              )}

              <h3 className="font-semibold mt-4 mb-2">Prescriptions</h3>
              <ul className="divide-y mb-4">
                {prescriptions.map((pr) => (
                  <li key={pr.id} className="py-2 text-sm">
                    <span className="font-medium">{pr.title}</span>: {pr.content}
                  </li>
                ))}
              </ul>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <form onSubmit={handlePrescription} className="bg-gray-50 p-3 rounded">
                  <h4 className="font-medium mb-2">Write Prescription</h4>
                  <input className="w-full border rounded px-2 py-1 mb-2" placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} required />
                  <textarea className="w-full border rounded px-2 py-1 mb-2" placeholder="Content" value={content} onChange={(e) => setContent(e.target.value)} required />
                  <button className="bg-indigo-600 text-white px-3 py-1 rounded hover:bg-indigo-700">Save</button>
                </form>

                <form onSubmit={handleOrder} className="bg-gray-50 p-3 rounded">
                  <h4 className="font-medium mb-2">Create Order</h4>
                  <select className="w-full border rounded px-2 py-1 mb-2" value={orderType} onChange={(e) => setOrderType(e.target.value)}>
                    <option value="CT_SCAN">CT Scan</option>
                    <option value="PET_SCAN">PET Scan</option>
                    <option value="MRI">MRI</option>
                    <option value="BLOODWORK">Bloodwork</option>
                    <option value="X_RAY">X-Ray</option>
                    <option value="ULTRASOUND">Ultrasound</option>
                    <option value="OTHER">Other</option>
                  </select>
                  <select className="w-full border rounded px-2 py-1 mb-2" value={selectedDept} onChange={(e) => setSelectedDept(e.target.value)}>
                    {departments.map((d) => (
                      <option key={d.id} value={d.id}>{d.name}</option>
                    ))}
                  </select>
                  <button className="bg-indigo-600 text-white px-3 py-1 rounded hover:bg-indigo-700">Order</button>
                </form>
              </div>
            </>
          ) : (
            <p className="text-gray-500">Select a patient to view details.</p>
          )}
        </div>
      </div>

      <div className="bg-white p-4 rounded shadow max-w-xl">
        <h2 className="font-semibold mb-2">Upload Document</h2>
        <form onSubmit={handleDocUpload} className="flex flex-col sm:flex-row items-start sm:items-end gap-2">
          <select
            className="border rounded px-2 py-1 text-sm"
            value={docType}
            onChange={(e) => setDocType(e.target.value)}
          >
            <option value="MEDICAL_RECORD">Medical Record</option>
            <option value="PRESCRIPTION">Prescription</option>
            <option value="RESULT">Result</option>
            <option value="IDENTITY">Identity</option>
            <option value="OTHER">Other</option>
          </select>
          <input type="file" onChange={(e) => setDocFile(e.target.files[0])} />
          <button className="bg-indigo-600 text-white px-3 py-1 rounded hover:bg-indigo-700">Upload</button>
        </form>
      </div>
    </div>
  );
};

export default DoctorDashboard;
