"use client";

import { useState, useEffect, useRef } from "react";
import { Send, FileUp, Loader2 } from "lucide-react";

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<{role: 'user' | 'ai', content: string, citations?: any[]}[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const id = localStorage.getItem("docuchat_session") || Math.random().toString(36).substring(7);
    localStorage.setItem("docuchat_session", id);
    setSessionId(id);
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.[0] || !sessionId) return;
    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", e.target.files[0]);

    try {
      await fetch("http://localhost:8000/api/v1/upload", {
        method: "POST",
        headers: { "x-session-id": sessionId },
        body: formData,
      });
      alert("File uploaded! Processing in background...");
    } catch (err) {
      console.error(err);
    } finally {
      setIsUploading(false);
    }
  };

  const handleChat = async () => {
    if (!query || !sessionId) return;
    
    const userMsg = query;
    setQuery("");
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setIsTyping(true);

    const response = await fetch("http://localhost:8000/api/v1/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: userMsg, session_id: sessionId }),
    });

    const reader = response.body?.getReader();
    if (!reader) return;

    let aiContent = "";
    let citations: any[] = [];
    setMessages(prev => [...prev, { role: 'ai', content: "" }]);

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = new TextDecoder().decode(value);
      const lines = chunk.split("\n");
      
      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.slice(6));
            if (data.type === "text") {
              aiContent += data.content;
              setMessages(prev => {
                const last = prev[prev.length - 1];
                return [...prev.slice(0, -1), { ...last, content: aiContent }];
              });
            } else if (data.type === "citations") {
              citations = data.content;
              setMessages(prev => {
                const last = prev[prev.length - 1];
                return [...prev.slice(0, -1), { ...last, citations }];
              });
            }
          } catch (e) {}
        }
      }
    }
    setIsTyping(false);
  };

  return (
    <main className="flex flex-col h-screen max-w-4xl mx-auto p-4">
      <header className="flex justify-between items-center mb-8 border-b pb-4">
        <h1 className="text-2xl font-bold">DocuChat AI</h1>
        <label className="cursor-pointer bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700 transition">
          {isUploading ? <Loader2 className="animate-spin" /> : <FileUp size={20} />}
          Upload PDF
          <input type="file" className="hidden" accept=".pdf" onChange={handleUpload} disabled={isUploading} />
        </label>
      </header>

      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-4 rounded-2xl ${m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
              <p className="whitespace-pre-wrap">{m.content}</p>
              {m.citations && m.citations.length > 0 && (
                <div className="mt-3 pt-2 border-t border-gray-300 text-xs italic">
                  Sources: {m.citations.map((c, ci) => (
                    <span key={ci} className="mr-2">[{c.filename}, p.{c.page}]</span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={scrollRef} />
      </div>

      <div className="flex gap-2">
        <input
          className="flex-1 border rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Ask a question about your documents..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleChat()}
        />
        <button 
          onClick={handleChat}
          disabled={isTyping || !query}
          className="bg-blue-600 text-white p-3 rounded-xl hover:bg-blue-700 disabled:opacity-50"
        >
          <Send size={24} />
        </button>
      </div>
    </main>
  );
}
