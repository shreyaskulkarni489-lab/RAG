'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { DocumentItem } from '@/types';
import { useRouter } from 'next/navigation';
import { Upload, FileText, Trash2, CheckCircle2, AlertCircle, Clock, Plus, Shield } from 'lucide-react';

export default function AdminPage() {
  const { user, token } = useAuth();
  const router = useRouter();

  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [department, setDepartment] = useState('');
  const [collection, setCollection] = useState('');
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (user && user.role !== 'admin') {
      router.push('/');
    }
  }, [user, router]);

  useEffect(() => {
    if (token) {
      fetchDocuments();
    }
  }, [token]);

  const fetchDocuments = async () => {
    try {
      const res = await fetch('/api/admin/documents', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setDocuments(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setMessage('');

    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);
    if (department) formData.append('department', department);
    if (collection) formData.append('collection', collection);

    try {
      const res = await fetch('/api/admin/documents/upload', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`
        },
        body: formData,
      });

      const responseText = await res.text();
      let data: any = {};
      try {
        data = JSON.parse(responseText);
      } catch {
        throw new Error(`Upload server error (${res.status}): ${responseText || 'Check backend logs'}`);
      }

      if (!res.ok) {
        throw new Error(data.detail || 'Upload failed');
      }

      setMessage('Document uploaded, parsed, and embedded successfully!');
      setFile(null);
      setTitle('');
      setDepartment('');
      setCollection('');
      fetchDocuments();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this document and all its vector chunks?')) return;
    try {
      const res = await fetch(`/api/admin/documents/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        fetchDocuments();
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-8">
      <div className="flex items-center justify-between border-b pb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <Shield className="w-6 h-6 text-purple-600" />
            Knowledge Base & Document Management
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Upload and manage institutional documents parsed and vectorized for CampusMind RAG.
          </p>
        </div>
      </div>

      {message && (
        <div
          className={`p-3 rounded-xl text-sm ${
            message.startsWith('Error')
              ? 'bg-red-50 text-red-700 border border-red-200'
              : 'bg-green-50 text-green-700 border border-green-200'
          }`}
        >
          {message}
        </div>
      )}

      {/* Upload Box */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <h2 className="text-base font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <Upload className="w-4 h-4 text-blue-600" />
          Upload New Document (PDF / DOCX / TXT)
        </h2>

        <form onSubmit={handleUpload} className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">
              Select File *
            </label>
            <input
              type="file"
              required
              accept=".pdf,.docx,.doc,.txt"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">
              Document Display Title (Optional)
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Admission Guidelines 2026"
              className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">
              Department (Optional)
            </label>
            <input
              type="text"
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              placeholder="e.g. CSE, Admissions, Hostel"
              className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">
              Collection (Optional)
            </label>
            <input
              type="text"
              value={collection}
              onChange={(e) => setCollection(e.target.value)}
              placeholder="e.g. Policies, Fees, Rules"
              className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="md:col-span-2">
            <button
              type="submit"
              disabled={uploading || !file}
              className="py-2.5 px-6 bg-blue-600 text-white rounded-xl text-xs font-medium hover:bg-blue-700 transition disabled:opacity-50 flex items-center gap-2"
            >
              {uploading ? 'Processing & Embedding...' : 'Ingest Document'}
            </button>
          </div>
        </form>
      </div>

      {/* Document Listing Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200">
          <h2 className="text-base font-semibold text-slate-800 flex items-center gap-2">
            <FileText className="w-4 h-4 text-blue-600" />
            Ingested Documents ({documents.length})
          </h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 font-semibold border-b">
              <tr>
                <th className="p-3">Title & File</th>
                <th className="p-3">Department</th>
                <th className="p-3">Collection</th>
                <th className="p-3">Status</th>
                <th className="p-3">Uploaded</th>
                <th className="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {documents.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-6 text-center text-slate-400">
                    No documents ingested yet.
                  </td>
                </tr>
              ) : (
                documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-50">
                    <td className="p-3">
                      <div className="font-semibold text-slate-800">{doc.title}</div>
                      <div className="text-[11px] text-slate-400 font-mono">{doc.filename}</div>
                    </td>
                    <td className="p-3 text-slate-600">{doc.department || '—'}</td>
                    <td className="p-3 text-slate-600">{doc.collection || '—'}</td>
                    <td className="p-3">
                      {doc.status === 'processed' && (
                        <span className="inline-flex items-center gap-1 text-green-700 bg-green-50 px-2 py-0.5 rounded-full border border-green-200">
                          <CheckCircle2 className="w-3 h-3" /> Processed
                        </span>
                      )}
                      {doc.status === 'processing' && (
                        <span className="inline-flex items-center gap-1 text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
                          <Clock className="w-3 h-3" /> Processing
                        </span>
                      )}
                      {doc.status === 'failed' && (
                        <span className="inline-flex items-center gap-1 text-red-700 bg-red-50 px-2 py-0.5 rounded-full border border-red-200">
                          <AlertCircle className="w-3 h-3" /> Failed
                        </span>
                      )}
                    </td>
                    <td className="p-3 text-slate-500">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() => handleDelete(doc.id)}
                        title="Delete Document"
                        className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
