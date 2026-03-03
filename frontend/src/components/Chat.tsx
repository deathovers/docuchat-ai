"use client";

import { useState } from 'react';

export default function Chat({ sessionId }: { sessionId: string }) {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { role: 'user', content: input };
    setMessages([...messages, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message: input }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.answer, sources: data.sources }]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col p-4">
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((m, i) => (
          <div key={i} className={`p-3 rounded-lg ${m.role === 'user' ? 'bg-blue-100 ml-auto max-w-[80%]' : 'bg-white border max-w-[80%]'}`}>
            <p className="text-sm">{m.content}</p>
            {m.sources && (
              <div className="mt-2 pt-2 border-t text-xs text-gray-500">
                Sources: {m.sources.map((s: any, idx: number) => (
                  <span key={idx} className="mr-2">[{s.file}, p.{s.page}]</span>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && <div className="text-gray-400 text-sm italic">AI is thinking...</div>}
      </div>
      <form onSubmit={sendMessage} className="flex gap-2">
        <input
          className="flex-1 border rounded-md px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about your documents..."
        />
        <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">Send</button>
      </form>
    </div>
  );
}
