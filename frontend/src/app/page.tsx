'use client';

import { useState, useEffect, useRef } from 'react';
import { Mic, BarChart3, Settings as SettingsIcon, ShieldCheck, ChevronRight, Play } from 'lucide-react';

export default function Home() {
  const [activeTab, setActiveTab] = useState('voice');
  const [isRecording, setIsRecording] = useState(false);
  const [language, setLanguage] = useState('eng');
  const [responses, setResponses] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [period, setPeriod] = useState('today');
  const [readAloud, setReadAloud] = useState(true);
  const [isListeningForWakeWord, setIsListeningForWakeWord] = useState(false);

  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn('SpeechRecognition API not supported in this browser.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => setIsListeningForWakeWord(true);
    recognition.onend = () => {
      setIsListeningForWakeWord(false);
      if (activeTab === 'voice') {
        try { recognition.start(); } catch (e) {}
      }
    };

    recognition.onresult = (event: any) => {
      const current = event.resultIndex;
      const transcript = event.results[current][0].transcript.toLowerCase();
      
      if (transcript.includes('casjoe') || transcript.includes('hey casjoe') || transcript.includes('hey siri')) {
        let query = transcript.replace(/.*(hey casjoe|casjoe|hey siri)/, '').trim();
        if (!query) query = "What were my sales today?";
        handleSimulateRecording(query);
      }
    };

    recognitionRef.current = recognition;

    if (activeTab === 'voice') {
      try { recognition.start(); } catch (e) {}
    }

    return () => {
      if (recognitionRef.current) recognitionRef.current.stop();
    };
  }, [activeTab]);

  const speakResponse = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      window.speechSynthesis.speak(utterance);
    }
  };

  const handleSimulateRecording = async (transcriptText?: string | any) => {
    const textToProcess = (typeof transcriptText === 'string' && transcriptText) ? transcriptText : 'What were my sales today?';
    
    setLoading(true);
    setIsRecording(true);
    try {
      const mockFormData = new FormData();
      mockFormData.append('language', language);
      mockFormData.append('transcript', textToProcess);
      
      const res = await fetch('http://localhost:8000/api/v1/text_query', {
        method: 'POST',
        body: mockFormData,
      });
      
      const data = await res.json();
      const responseWithQuery = { ...data, _userQuery: textToProcess };
      setResponses(prev => [responseWithQuery, ...prev]);

      if (readAloud) {
        if (data.audio_url) {
          const audio = new Audio(`http://localhost:8000${data.audio_url}`);
          audio.play().catch(e => {
            console.error('Audio playback failed:', e);
            if (data.response_text) speakResponse(data.response_text);
          });
        } else if (data.response_text) {
          speakResponse(data.response_text);
        }
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
      setIsRecording(false);
    }
  };

  const renderVoiceTab = () => (
    <div className="flex flex-col h-full relative pb-32">
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {responses.length === 0 ? (
          <div className="text-center mt-8">
            <h2 className="text-xl font-bold text-gray-800 mb-2">Tap to speak</h2>
            <p className="text-gray-500 mb-6 text-sm">Ask about your sales, customers, expenses or finances.</p>
            <div className="space-y-3 text-left">
              <div className="bg-gray-50 border border-gray-100 p-4 rounded-xl shadow-sm cursor-pointer hover:bg-gray-100 transition flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">"How much did I sell today?"</span>
                <ChevronRight size={16} className="text-gray-400" />
              </div>
              <div className="bg-gray-50 border border-gray-100 p-4 rounded-xl shadow-sm cursor-pointer hover:bg-gray-100 transition flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">"Who owes me money?"</span>
                <ChevronRight size={16} className="text-gray-400" />
              </div>
              <div className="bg-gray-50 border border-gray-100 p-4 rounded-xl shadow-sm cursor-pointer hover:bg-gray-100 transition flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">"What is profit?"</span>
                <ChevronRight size={16} className="text-gray-400" />
              </div>
            </div>
          </div>
        ) : (
          responses.map((r, i) => (
            <div key={i} className="flex flex-col space-y-3 mb-4">
              <div className="self-end bg-green-100 text-green-900 px-4 py-3 rounded-2xl max-w-[85%] rounded-tr-sm shadow-sm">
                <span className="text-[10px] uppercase font-bold text-green-700/60 block mb-1">You</span>
                <span className="text-sm">"{r._userQuery || "What were my sales today?"}"</span>
              </div>
              <div className="self-start bg-white border border-gray-100 text-gray-800 px-4 py-3 rounded-2xl max-w-[85%] rounded-tl-sm shadow-sm">
                <span className="text-[10px] uppercase font-bold text-gray-400 block mb-1">Casjoe VoiceBiz</span>
                {r.detail ? (
                  <div className="text-red-600 text-sm">
                    <span className="font-bold">System Error:</span> {r.detail}
                  </div>
                ) : (
                  <>
                    <span className="inline-block px-2 py-1 bg-green-50 text-green-700 rounded text-[10px] font-bold tracking-wider mb-2 border border-green-100">
                      {r.intent || 'UNKNOWN'} {r.confidence !== undefined ? `(${(r.confidence * 100).toFixed(0)}%)` : ''}
                    </span>
                    <p className="text-sm leading-relaxed">
                      {r.response_text || "I found your data! Sales today are ₦45,000."}
                    </p>
                    <button onClick={() => speakResponse(r.response_text || "I found your data! Sales today are ₦45,000.")} className="mt-3 flex items-center space-x-1 text-green-600 bg-green-50 px-3 py-1.5 rounded-full text-xs font-semibold hover:bg-green-100 transition-colors">
                      <Play size={12} className="fill-current" />
                      <span>Play</span>
                    </button>
                  </>
                )}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="self-start bg-white border border-gray-100 text-gray-800 px-4 py-3 rounded-2xl max-w-[80%] rounded-tl-sm shadow-sm">
             <div className="flex space-x-1.5 my-1">
              <div className="w-2 h-2 bg-green-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-green-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-green-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        )}
      </div>

      {/* Voice Action Button */}
      <div className="absolute bottom-24 w-full p-6 bg-gradient-to-t from-gray-50 via-gray-50 to-transparent flex justify-center pb-8 pointer-events-none">
        <button 
          onClick={handleSimulateRecording}
          className={`w-16 h-16 rounded-full flex items-center justify-center shadow-xl transition-all transform active:scale-95 pointer-events-auto ${
            isRecording ? 'bg-red-500 animate-pulse ring-4 ring-red-200' : 'bg-green-600 hover:bg-green-700 ring-4 ring-green-100'
          }`}
        >
          <Mic size={28} className="text-white" />
        </button>
      </div>
    </div>
  );

  const renderDashboardTab = () => (
    <div className="p-4 overflow-y-auto pb-24 h-full">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-lg font-bold text-gray-800">Business Summary</h2>
        <select 
          className="bg-white border border-gray-200 text-gray-700 text-xs px-2 py-1 rounded shadow-sm outline-none focus:ring-1 focus:ring-green-500"
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
        >
          <option value="today">Today</option>
          <option value="week">This Week</option>
          <option value="month">This Month</option>
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
          <span className="text-gray-500 text-xs font-semibold uppercase tracking-wider">Sales</span>
          <p className="text-2xl font-bold text-gray-900 mt-1">₦48,500</p>
          <span className="text-green-600 text-xs font-medium flex items-center mt-2">
             ↑ 12% vs last {period}
          </span>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
          <span className="text-gray-500 text-xs font-semibold uppercase tracking-wider">Expenses</span>
          <p className="text-2xl font-bold text-gray-900 mt-1">₦12,300</p>
          <span className="text-red-500 text-xs font-medium flex items-center mt-2">
             ↑ 5% vs last {period}
          </span>
        </div>
        <div className="col-span-2 bg-gradient-to-r from-green-600 to-green-800 p-5 rounded-xl shadow-md text-white">
          <span className="text-green-100 text-xs font-semibold uppercase tracking-wider">Gross Profit</span>
          <p className="text-3xl font-bold mt-1">₦36,200</p>
          <div className="mt-4 flex justify-between items-end">
            <div>
              <p className="text-xs text-green-200 mb-0.5">Top Product</p>
              <p className="text-sm font-semibold">Ankara Fabric (6 Yards)</p>
            </div>
            <button className="bg-white/20 hover:bg-white/30 px-3 py-1.5 rounded-full text-xs font-medium backdrop-blur-sm transition">
              Ask AI
            </button>
          </div>
        </div>
      </div>

      <h3 className="text-sm font-bold text-gray-800 mb-3 uppercase tracking-wider">Receivables (Credit)</h3>
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden mb-6">
        <div className="p-4 border-b border-gray-50 flex justify-between items-center">
          <div>
            <p className="font-semibold text-gray-800 text-sm">Amaka Stores</p>
            <p className="text-xs text-gray-500">Due in 2 days</p>
          </div>
          <p className="font-bold text-red-600">₦15,000</p>
        </div>
        <div className="p-4 flex justify-between items-center">
          <div>
            <p className="font-semibold text-gray-800 text-sm">Emeka Logistics</p>
            <p className="text-xs text-red-400">Overdue (5 days)</p>
          </div>
          <p className="font-bold text-red-600">₦42,000</p>
        </div>
      </div>
    </div>
  );

  const renderSettingsTab = () => (
    <div className="p-4 h-full bg-gray-50">
      <h2 className="text-lg font-bold text-gray-800 mb-6">Settings</h2>
      
      <div className="space-y-6">
        <div>
          <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 ml-1">Preferences</h3>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="p-4 border-b border-gray-50 flex justify-between items-center">
              <span className="text-sm font-medium text-gray-800">Spoken Language</span>
              <select 
                className="bg-gray-50 border border-gray-200 text-gray-700 text-xs px-2 py-1 rounded outline-none focus:ring-1 focus:ring-green-500"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
              >
                <option value="eng">Nigerian English</option>
                <option value="ibo">Igbo</option>
                <option value="yor">Yoruba</option>
                <option value="hau">Hausa</option>
              </select>
            </div>
            <div className="p-4 flex justify-between items-center">
              <span className="text-sm font-medium text-gray-800">Read Answers Aloud</span>
              <div onClick={() => setReadAloud(!readAloud)} className={`w-10 h-5 rounded-full relative cursor-pointer transition-colors ${readAloud ? 'bg-green-500' : 'bg-gray-300'}`}>
                <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow-sm transition-all ${readAloud ? 'right-1' : 'left-1'}`}></div>
              </div>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 ml-1">Account & Privacy</h3>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="p-4 border-b border-gray-50 flex items-center text-red-600 cursor-pointer">
              <span className="text-sm font-medium">Clear Voice History</span>
            </div>
            <div className="p-4 flex items-center justify-between cursor-pointer">
              <span className="text-sm font-medium text-gray-800">Privacy Policy</span>
              <ChevronRight size={16} className="text-gray-400" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <main className="min-h-screen bg-gray-900 flex flex-col items-center justify-center p-4">
      {/* Phone container wrapper to simulate mobile view on desktop */}
      <div className="w-full max-w-[400px] h-[800px] max-h-[95vh] bg-gray-50 rounded-[2.5rem] shadow-2xl overflow-hidden flex flex-col relative ring-8 ring-gray-800">
        
        {/* Status bar mock */}
        <div className="h-7 w-full bg-green-800 flex justify-center items-center">
          <div className="w-20 h-4 bg-black rounded-b-xl absolute top-0"></div>
        </div>

        {/* Header */}
        <header className="bg-green-700 text-white p-5 flex justify-between items-center shadow-md z-10">
          <div>
            <h1 className="text-xl font-bold tracking-tight">Casjoe VoiceBiz</h1>
            <p className="text-xs text-green-200 font-medium">Adaeze Fashion House</p>
          </div>
          <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center border-2 border-green-400">
            <span className="text-xs font-bold">AF</span>
          </div>
        </header>

        {/* Main Content Area */}
        <div className="flex-1 overflow-hidden relative bg-gray-50">
          {activeTab === 'voice' && renderVoiceTab()}
          {activeTab === 'dashboard' && renderDashboardTab()}
          {activeTab === 'settings' && renderSettingsTab()}
        </div>

        {/* Bottom Navigation */}
        <nav className="absolute bottom-0 w-full bg-white border-t border-gray-200 px-6 py-4 flex justify-between items-center pb-8 z-20">
          <button 
            onClick={() => setActiveTab('dashboard')}
            className={`flex flex-col items-center space-y-1 transition-colors ${activeTab === 'dashboard' ? 'text-green-600' : 'text-gray-400 hover:text-gray-600'}`}
          >
            <BarChart3 size={22} strokeWidth={activeTab === 'dashboard' ? 2.5 : 2} />
            <span className="text-[10px] font-medium">Summary</span>
          </button>
          
          <button 
            onClick={() => setActiveTab('voice')}
            className={`flex flex-col items-center space-y-1 transition-colors ${activeTab === 'voice' ? 'text-green-600' : 'text-gray-400 hover:text-gray-600'}`}
          >
            <Mic size={22} strokeWidth={activeTab === 'voice' ? 2.5 : 2} />
            <span className="text-[10px] font-medium">Voice AI</span>
          </button>
          
          <button 
            onClick={() => setActiveTab('settings')}
            className={`flex flex-col items-center space-y-1 transition-colors ${activeTab === 'settings' ? 'text-green-600' : 'text-gray-400 hover:text-gray-600'}`}
          >
            <SettingsIcon size={22} strokeWidth={activeTab === 'settings' ? 2.5 : 2} />
            <span className="text-[10px] font-medium">Settings</span>
          </button>
        </nav>
      </div>
    </main>
  );
}

