import React, { useEffect, useState } from 'react';
import api from '../services/api';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const PatientDashboard = () => {
  const [profile, setProfile] = useState(null);
  const [readings, setReadings] = useState([]);
  const [prescriptions, setPrescriptions] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [file, setFile] = useState(null);
  const [docFile, setDocFile] = useState(null);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const profiles = await api.get('/patients/');
      const profileResults = profiles.data.results || profiles.data;
      const myProfile = profileResults[0];
      if (!myProfile) return;
      setProfile(myProfile);

      const r = await api.get(`/patients/${myProfile.id}/readings/`);
      setReadings(r.data.results || r.data);

      const p = await api.get(`/doctors/prescriptions/?patient=${myProfile.id}`);
      setPrescriptions(p.data.results || p.data);

      const d = await api.get('/documents/');
      setDocuments(d.data.results || d.data);
    } catch {
      // ignore
    }
  };

  const downloadDocument = async (doc) => {
    try {
      const res = await api.get(`/documents/${doc.id}/download/`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', doc.original_filename || 'document');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      setMessage('Document download failed.');
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file || !profile) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      await api.post(`/patients/${profile.id}/readings/upload/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setMessage('Readings uploaded successfully.');
      setFile(null);
      fetchData();
    } catch {
      setMessage('Upload failed.');
    }
  };

  const handleDocUpload = async (e) => {
    e.preventDefault();
    if (!docFile) return;
    const formData = new FormData();
    formData.append('file', docFile);
    formData.append('document_type', 'MEDICAL_RECORD');
    try {
      await api.post('/documents/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setMessage('Document uploaded securely.');
      setDocFile(null);
      fetchData();
    } catch {
      setMessage('Document upload failed.');
    }
  };

  const sortedReadings = [...readings].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

  const chartData = sortedReadings.map((r) => ({
    name: new Date(r.timestamp).toLocaleDateString(),
    heart_rate: r.heart_rate,
    sys: r.blood_pressure_sys,
    dia: r.blood_pressure_dia,
    temp: r.temperature,
  }));

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold mb-4">Patient Dashboard</h1>
      {message && <div className="bg-green-100 text-green-700 p-2 rounded mb-4">{message}</div>}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white p-4 rounded shadow">
          <h2 className="font-semibold mb-2">Health Readings</h2>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="heart_rate" stroke="#8884d8" name="Heart Rate" />
                <Line type="monotone" dataKey="sys" stroke="#82ca9d" name="BP Sys" />
                <Line type="monotone" dataKey="dia" stroke="#ffc658" name="BP Dia" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500">No readings yet.</p>
          )}
        </div>

        <div className="bg-white p-4 rounded shadow">
          <h2 className="font-semibold mb-2">Upload Device Data (CSV)</h2>
          <form onSubmit={handleUpload} className="flex items-center gap-2">
            <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files[0])} />
            <button className="bg-indigo-600 text-white px-3 py-1 rounded hover:bg-indigo-700">Upload</button>
          </form>
          <div className="mt-4">
            <h2 className="font-semibold mb-2">Upload Document</h2>
            <form onSubmit={handleDocUpload} className="flex items-center gap-2">
              <input type="file" onChange={(e) => setDocFile(e.target.files[0])} />
              <button className="bg-indigo-600 text-white px-3 py-1 rounded hover:bg-indigo-700">Upload</button>
            </form>
          </div>
        </div>
      </div>

      <div className="bg-white p-4 rounded shadow mb-6">
        <h2 className="font-semibold mb-2">Prescriptions</h2>
        {prescriptions.length === 0 ? (
          <p className="text-gray-500">No prescriptions yet.</p>
        ) : (
          <ul className="divide-y">
            {prescriptions.map((p) => (
              <li key={p.id} className="py-2">
                <div className="font-medium">{p.title}</div>
                <div className="text-sm text-gray-600">Dr. {p.doctor_name}</div>
                <div className="text-sm text-gray-700 mt-1">{p.content}</div>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="bg-white p-4 rounded shadow mb-6">
        <h2 className="font-semibold mb-2">Documents</h2>
        {documents.length === 0 ? (
          <p className="text-gray-500">No documents uploaded yet.</p>
        ) : (
          <ul className="divide-y">
            {documents.map((doc) => (
              <li key={doc.id} className="py-2 flex items-center justify-between gap-3">
                <div>
                  <div className="font-medium">{doc.original_filename}</div>
                  <div className="text-xs text-gray-500">
                    {doc.document_type.replace('_', ' ')} - {new Date(doc.uploaded_at).toLocaleDateString()}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => downloadDocument(doc)}
                  className="text-indigo-600 hover:underline text-sm"
                >
                  Download
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default PatientDashboard;
