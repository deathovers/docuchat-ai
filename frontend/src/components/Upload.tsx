"use client";

import { useState, useEffect } from 'react';

export default function Upload({ sessionId }: { sessionId: string }) {
  const [files, setFiles] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);

  const fetchFiles = async () => {
    const res = await fetch(`http://localhost:8000/v1/files?session_id=${sessionId}`);
    const data = await res.json();
    setFiles(data);
  };

  useEffect(() => { fetchFiles(); }, [sessionId]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.[0]) return;
    setUploading(true);

    const formData = new FormData();
    formData.append('file', e.target.files[0]);
    formData.append('session_id', sessionId);

    try {
      await fetch('http://localhost:8000/v1/upload', {
        method: 'POST',
        body: formData,
      });
      fetchFiles();
    } catch (err) {
      alert("Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="border-2 border-dashed rounded-lg p-4 text-center">
        <input
          type="file"
          accept=".pdf"
          onChange={handleUpload}
          className="hidden"
          id="file-upload"
          disabled={uploading}
        />
        <label htmlFor="file-upload" className="cursor-pointer text-blue-600 hover:underline">
          {uploading ? 'Processing...' : 'Upload PDF'}
        </label>
      </div>
      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-gray-500 uppercase">Your Documents</h3>
        {files.map((f, i) => (
          <div key={i} className="text-sm p-2 bg-gray-100 rounded truncate">
            {f.filename}
          </div>
        ))}
      </div>
    </div>
  );
}
