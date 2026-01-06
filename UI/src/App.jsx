import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, X, Send, User, Bot, Loader2, Landmark, ShieldCheck, FileText } from 'lucide-react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([{ role: 'bot', text: 'Hello! I am your banking assistant. How can I help you today?' }]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);
  const [userId] = useState(() => "user_" + Math.random().toString(36).substr(2, 9));

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMsg = { role: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await axios.post('http://localhost:8000/chat', { user_id: userId, text: input });
      setMessages(prev => [...prev, { role: 'bot', text: res.data.response }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', text: "Error: Is your Python backend running?" }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      {isOpen && (
        <div className="bg-white w-80 sm:w-96 h-[500px] rounded-2xl shadow-2xl border flex flex-col mb-4 overflow-hidden border-blue-100">
          {/* Header */}
          <div className="bg-blue-600 p-4 text-white flex justify-between items-center">
            <div>
              <h3 className="font-bold">Banking Support</h3>
              <p className="text-[10px] opacity-80">Online | Verified Agent</p>
            </div>
            <button onClick={() => setIsOpen(false)}><X size={20} /></button>
          </div>

          {/* Messages Area */}
          <div ref={scrollRef} className="flex-1 p-4 overflow-y-auto space-y-4 bg-gray-50">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`p-3 rounded-2xl text-sm max-w-[85%] shadow-sm ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white rounded-tr-none' 
                    : 'bg-white border border-gray-100 text-gray-800 rounded-tl-none'
                }`}>
                  
                  {/* FIX: Move className to a wrapper div, NOT on ReactMarkdown itself */}
                  <div className="markdown-container break-words leading-relaxed">
                    <ReactMarkdown 
                      components={{
                        // Tailwind resets styles, so we manually define bold and spacing
                        strong: ({node, ...props}) => <span className="font-bold text-blue-900" {...props} />,
                        ul: ({node, ...props}) => <ul className="list-disc ml-4 my-2" {...props} />,
                        li: ({node, ...props}) => <li className="mb-1" {...props} />,
                        p: ({node, ...props}) => <p className="mb-2 last:mb-0" {...props} />
                      }}
                    >
                      {msg.text}
                    </ReactMarkdown>
                  </div>

                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white border p-3 rounded-2xl animate-pulse flex items-center gap-2">
                  <Loader2 className="animate-spin text-blue-600" size={16} />
                  <span className="text-xs text-gray-400">Typing...</span>
                </div>
              </div>
            )}
          </div>

          {/* Input Area */}
          <form onSubmit={sendMessage} className="p-4 border-t bg-white flex gap-2">
            <input 
              value={input} 
              onChange={e => setInput(e.target.value)} 
              placeholder="Type here..." 
              className="flex-1 bg-gray-100 rounded-lg px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-blue-500" 
            />
            <button type="submit" className="bg-blue-600 text-white p-2 rounded-lg transition-transform active:scale-95">
              <Send size={18} />
            </button>
          </form>
        </div>
      )}
      <button onClick={() => setIsOpen(!isOpen)} className="bg-blue-600 text-white p-4 rounded-full shadow-xl hover:scale-105 transition-transform active:scale-95">
        {isOpen ? <X size={28} /> : <MessageCircle size={28} />}
      </button>
    </div>
  );
};

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b px-8 py-4 flex justify-between items-center sticky top-0 z-10">
        <div className="flex items-center gap-2 text-blue-600 font-bold text-xl"><Landmark /> SecureBank</div>
        <div className="hidden md:flex gap-8 text-gray-600 text-sm font-medium">
          <a href="#">Accounts</a><a href="#">Loans</a><a href="#">Insurance</a>
        </div>
        <button className="bg-blue-600 text-white px-5 py-2 rounded-full text-sm font-semibold">My Account</button>
      </nav>

      <main className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h1 className="text-6xl font-black text-gray-900 mb-6">Banking made <span className="text-blue-600">Personal.</span></h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">Get verified instantly and apply for our low-interest loans using our smart assistant.</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {[
            { icon: <ShieldCheck className="text-blue-600" />, title: "Secure ID", desc: "Two-factor OTP verification for your security." },
            { icon: <FileText className="text-blue-600" />, title: "Quick Apply", desc: "Upload docs and get your loan data auto-filled." },
            { icon: <Landmark className="text-blue-600" />, title: "Low Rates", desc: "Competitive rates starting as low as 3.5% APR." }
          ].map((item, i) => (
            <div key={i} className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="mb-4">{item.icon}</div>
              <h3 className="text-xl font-bold mb-2">{item.title}</h3>
              <p className="text-gray-500">{item.desc}</p>
            </div>
          ))}
        </div>
      </main>
      <ChatWidget />
    </div>
  );
}