"use client";

import { useState, useEffect } from 'react';
import Chat from '@/components/Chat';
import Upload from '@/components/Upload';
import { v4 as uuidv4 } from 'uuid';

export default function Home() {
  const [sessionId, setSessionId] = useState<string>('');

  useEffect(() => {
    const id = localStorage.getItem('session_id') || uuidv4();
    localStorage.setItem('session_id', id);
    setSessionId(id);
  }, []);

  if (!sessionId) return null;

  return (
    <main className="flex h-screen bg-gray-50">
      <div className="w-1/4 border-r bg-white p-4 overflow-y-auto">
        <h1 className="text-xl font-bold mb-6">DocuChat AI</h1>
        <Upload sessionId={sessionId} />
      </div>
      <div className="flex-1 flex flex-col">
        <Chat sessionId={sessionId} />
      </div>
    </main>
  );
}

// Mock uuidv4 since we don't want to install it just for this demo
function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}
