"use client";

import { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Upload, Send, FileText, Trash2, Loader2 } from 'lucide-react';

const API_BASE = "http://localhost:8000/v1";

export default function DocuChat() {
  const [sessionId, setSessionId] = useState('');
  const [files, setFiles] = useState<any[]>([]);
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    setSessionId(uuidv4());
  }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    setUploading(true);
    const formData = new FormData();
    formData.append('session_id', sessionId);
    Array.from(e.target.files).forEach(file => {
      formData.append('files', file);
    });

    try {
      const res = await fetch(`${API_BASE}/documents/upload`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setFiles([...files, ...data.files]);
    } catch (err) {
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    const userMsg = { role: 'user', content: query };
    setMessages([...messages, userMsg]);
    setQuery('');
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/chat/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, query }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.answer, 
        sources: data.sources 
      }]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const deleteFile = async (fileId: string) => {
    await fetch(`${API_BASE}/documents/${fileId}`, { method: 'DELETE' });
    setFiles(files.filter(f => f.file_id !== fileId));
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r p-4 flex flex-col">
        <h1 className="text-xl font-bold mb-6">DocuChat AI</h1>
        
        <div className="mb-4">
          <label className="flex items-center justify-center w-full h-12 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
            <div className="flex items-center space-x-2">
              {uploading ? <Loader2 className="animate-spin" /> : <Upload size={20} />}
              <span>Upload PDFs</span>
            </div>
            <input type="file" multiple accept=".pdf" className="hidden" onChange={handleUpload} disabled={uploading} />
          </label>
        </div>

        <div className="flex-1 overflow-y-auto">
          <h2 className="text-sm font-semibold text-gray-500 uppercase mb-2">Documents</h2>
          {files.map(file => (
            <div key={file.file_id} className="flex items-center justify-between p-2 hover:bg-gray-100 rounded group">
              <div className="flex items-center space-x-2 overflow-hidden">
                <FileText size={16} className="text-blue-500 shrink-0" />
                <span className="text-sm truncate">{file.name}</span>
              </div>
              <button onClick={() => deleteFile(file.file_id)} className="opacity-0 group-hover:opacity-100 text-red-500">
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="h-full flex items-center justify-center text-gray-400">
              Upload documents and start asking questions!
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-2xl p-4 rounded-lg ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border shadow-sm'}`}>
                <p className="whitespace-pre-wrap">{msg.content}</p>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <p className="text-xs font-bold text-gray-500 mb-1">SOURCES:</p>
                    <div className="flex flex-wrap gap-2">
                      {msg.sources.map((s: any, idx: number) => (
                        <span key={idx} className="text-[10px] bg-gray-100 px-2 py-1 rounded">
                          {s.file_name} (p. {s.page_number})
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white border p-4 rounded-lg shadow-sm">
                <Loader2 className="animate-spin text-blue-600" />
              </div>
            </div>
          )}
        </div>

        <form onSubmit={handleQuery} className="p-4 bg-white border-t">
          <div className="max-w-4xl mx-auto flex space-x-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question about your documents..."
              className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <Send size={20} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
