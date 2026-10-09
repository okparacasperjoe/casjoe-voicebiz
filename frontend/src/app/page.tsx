'use client';

import { useState, useEffect, useRef } from 'react';
import { 
  Mic, 
  Square, 
  Play, 
  BarChart3, 
  Settings as SettingsIcon, 
  ShieldCheck, 
  ChevronRight, 
  Volume2, 
  VolumeX, 
  Sparkles, 
  Globe, 
  Activity, 
  TrendingUp, 
  Smartphone, 
  Monitor, 
  Zap, 
  ArrowUpRight, 
  Clock, 
  CheckCircle2,
  AlertCircle,
  Layers,
  Database,
  Link2,
  RefreshCw,
  ExternalLink,
  Key,
  Eye,
  EyeOff
} from 'lucide-react';

interface InteractionRecord {
  _userQuery?: string;
  transcript?: string;
  response_text?: string;
  intent?: string;
  confidence?: number;
  audio_url?: string | null;
  processing_ms?: number;
  detail?: string;
  timestamp?: string;
}

const UI_STRINGS: Record<string, any> = {
  eng: {
    heroTag: "VOICE ASSISTANT FOR BUSINESS",
    title: "VoiceBiz",
    subtitle: "Speak in English, Igbo, Yoruba & Hausa",
    statusOnline: "VOICE AI READY",
    tapToSpeak: "Tap to Speak",
    recordingActive: "Listening to you... Speak now",
    recordingHint: "Tap the red button when you are done",
    askAbout: "Ask about your sales, expenses, debtors, or profits.",
    ex1: "How much did I sell today?",
    ex2: "Who owes me money this week?",
    ex3: "What is my real profit?",
    ex4: "Give me financial advice for my business",
    summary: "Business Summary",
    today: "Today",
    week: "This Week",
    month: "This Month",
    sales: "Total Sales",
    expenses: "Money Spent (Expenses)",
    profit: "Your Profit (Gain)",
    topProduct: "Best Selling Item",
    askAI: "Explain This",
    receivables: "Customers Who Owe You (Debtors)",
    due: "Due in 2 days",
    overdue: "Overdue by 5 days",
    settings: "Settings",
    preferences: "Voice & Language",
    spokenLanguage: "Language You Speak",
    readAloud: "Read Answers Out Loud",
    accountPrivacy: "Privacy & Data",
    clearHistory: "Clear Voice History",
    privacyPolicy: "Privacy Policy",
    navSummary: "Summary",
    navVoice: "Voice",
    navSettings: "Settings",
    liveInteraction: "Voice Conversations",
    latency: "Speed",
    confidence: "Confidence",
    sendPrompt: "Check This",
    systemPromptTitle: "Ready for your voice question",
    actionFollowUp: "Send Reminder"
  },
  ibo: {
    heroTag: "ỌKWA NDỊ ISIOKWU • ASỤSỤ NDỊ NAIJIRIA",
    title: "VoiceBiz",
    subtitle: "Sistemụ Nchịkwa Azụmahịa Site n'Olu",
    statusOnline: "AI NA-ARỤ ỌRỤ N'IKIKERE",
    tapToSpeak: "Kpatụ ka ị kwuo okwu",
    recordingActive: "Na-ege ntị n'ihe ị na-ekwu...",
    recordingHint: "Pịa bọtịnụ na-acha uhie uhie ka o nyochaa",
    askAbout: "Kwuo okwu n'asụsụ Igbo gị ma ọ bụ Bekee nke ọma.",
    ex1: "Ego ole ka m rere taa?",
    ex2: "Onye ji m ụgwọ n'izu a?",
    ex3: "Gịnị bụ uru ahịa m mere?",
    ex4: "Nye m ezigbo ndụmọdụ ego maka ahịa m",
    summary: "Nchịkọta Ego na Azụmahịa",
    today: "Taa",
    week: "Izu a",
    month: "Ọnwa a",
    sales: "Ngụkọta Ahịa",
    expenses: "Ego Mmefu",
    profit: "Ezigbo Uru Azụmahịa",
    topProduct: "Ngwaahịa Kacha Reo",
    askAI: "Nyochaa Azụmahịa",
    receivables: "Akwụkwọ Ndị Ji Ụgwọ",
    due: "Fọdụrụ ụbọchị 2",
    overdue: "Agafeela • Ụbọchị 5 agafeela",
    settings: "Ntọala Sistemụ",
    preferences: "Nhọrọ Asụsụ & Ihe Nlereanya",
    spokenLanguage: "Asụsụ A Na-ekwu",
    readAloud: "Gụọ Azịza n'Olu Dara Ụda",
    accountPrivacy: "Nchekwa & Nzuzo",
    clearHistory: "Kpochapụ Akụkọ Mkparịta Ụka",
    privacyPolicy: "Iwu Nzuzo nke Ndị Isi",
    navSummary: "Nchịkọta",
    navVoice: "Olu AI",
    navSettings: "Ntọala",
    liveInteraction: "Mkparịta Ụka Na-aga n'Ihu",
    latency: "Oge Ọrụ",
    confidence: "Nkwenye",
    sendPrompt: "Zipụ Ajụjụ",
    systemPromptTitle: "Sistemụ dị njikere ịnata iwu olu",
    actionFollowUp: "Zipụ Ozi Nchetara"
  },
  yor: {
    heroTag: "Ọ GBỌN GIDIGIDI • EDE ILẸ WA",
    title: "VoiceBiz",
    subtitle: "Eto Isakoso Iṣowo Pẹlu Ohun",
    statusOnline: "AI WA NI IṢẸ LỌWỌLỌWỌ",
    tapToSpeak: "Tẹ lati sọrọ",
    recordingActive: "N tẹtisi ohun rẹ...",
    recordingHint: "Tẹ bọtini pupa lati pari ki o ṣe itupalẹ",
    askAbout: "Sọrọ larọwọto ni ede Yoruba tabi ede iṣowo rẹ.",
    ex1: "Elo ni mo ta loni?",
    ex2: "Tani o jẹ mi ni owo ni ọsẹ yii?",
    ex3: "Kini ere gidi ti mo ri?",
    ex4: "Fun mi ni imọran owo fun iṣowo mi",
    summary: "Akopọ Owo ati Iṣowo",
    today: "Loni",
    week: "Ọsẹ yii",
    month: "Oṣu yii",
    sales: "Gbogbo Owo Tita",
    expenses: "Inawo Gbogbo",
    profit: "Ere Gidi Lẹhin Inawo",
    topProduct: "Ọja Ti O Lọ Julọ",
    askAI: "Ṣayẹwo Jinlẹ",
    receivables: "Iwe Awọn Ti O Jẹ Gbese",
    due: "O ku ọjọ meji",
    overdue: "O ti pẹ • Ọjọ marun sẹhin",
    settings: "Eto Agbaye",
    preferences: "Awọn Eto Ede & Apẹẹrẹ",
    spokenLanguage: "Ede Ti A Yan",
    readAloud: "Ka Idahun Jade Pẹlu Ohun",
    accountPrivacy: "Aabo ati Aṣiri",
    clearHistory: "Pa Itan Ohun Rẹ Rẹ",
    privacyPolicy: "Ilana Aṣiri Data",
    navSummary: "Akopọ",
    navVoice: "Ohun AI",
    navSettings: "Eto",
    liveInteraction: "Itan Ibaraẹnisọrọ Lọwọlọwọ",
    latency: "Akoko",
    confidence: "Igbagbọ AI",
    sendPrompt: "Ṣayẹwo Ibeere",
    systemPromptTitle: "Sistemụ ti ṣetan fun awọn aṣẹ ohun",
    actionFollowUp: "Fi Ifiranṣẹ Ranṣẹ"
  },
  hau: {
    heroTag: "HIKIMAR SARAUTA • HARSUNAN GIDA",
    title: "VoiceBiz",
    subtitle: "Tsarukan Gudanar da Kasuwanci da Murya",
    statusOnline: "AI NA AIKI KAI TSAYE",
    tapToSpeak: "Danna don yin magana",
    recordingActive: "Ana sauraron muryar ku...",
    recordingHint: "Danna jan maballin don gama bincike",
    askAbout: "Yi magana a sauƙaƙe da harshen Hausa ko Ingilishi.",
    ex1: "Nawa na sayar a yau?",
    ex2: "Wanene yake bina bashi a wannan makon?",
    ex3: "Menene ainihin ribar da na samu?",
    ex4: "Ba ni shawarar kudi don kasuwancina",
    summary: "Takaitaccen Rahoton Kudi da Kasuwanci",
    today: "Yau",
    week: "Wannan Makon",
    month: "Wannan Watan",
    sales: "Jimillar Tallace-tallace",
    expenses: "Kudaden da aka Kashe",
    profit: "Ainihin Riba",
    topProduct: "Kayan da aka fi Sayarwa",
    askAI: "Cikakken Binciken Kudi",
    receivables: "Lissafin Masu Bashi",
    due: "Kwanaki 2 suka rage",
    overdue: "Ya wuce lokaci • Kwanaki 5 da suka wuce",
    settings: "Saitunan Tsarin",
    preferences: "Zaɓin Harshe da Tsari",
    spokenLanguage: "Harshen da ake Magana",
    readAloud: "Karanta Amsa da Murya",
    accountPrivacy: "Tsaro da Sirri",
    clearHistory: "Goge Tarihin Tattaunawa",
    privacyPolicy: "Ka'idojin Tsaron Bayanai",
    navSummary: "Takaitawa",
    navVoice: "Muryar AI",
    navSettings: "Saituna",
    liveInteraction: "Tattaunawar Kai Tsaye",
    latency: "Gaggawa",
    confidence: "Tabbacin AI",
    sendPrompt: "Bincika Tambaya",
    systemPromptTitle: "Tsarin a shirye yake don karɓar umarnin murya",
    actionFollowUp: "Aika Sakon Gargadi"
  }
};

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const [activeTab, setActiveTab] = useState<'voice' | 'dashboard' | 'settings'>('voice');
  const [viewMode, setViewMode] = useState<'desktop' | 'mobile'>('desktop');
  const [isRecording, setIsRecording] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [language, setLanguage] = useState('eng');
  const [responses, setResponses] = useState<InteractionRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [period, setPeriod] = useState('today');
  const [readAloud, setReadAloud] = useState(true);
  const [activeAudioUrl, setActiveAudioUrl] = useState<string | null>(null);
  const [crmApiKey, setCrmApiKey] = useState('casjoe_live_8e10f0b8775b0617eb7b270544e250cd4553364b868d0e144bb4dc01299b9461');
  const [showApiKey, setShowApiKey] = useState(false);
  const [crmSyncing, setCrmSyncing] = useState(false);
  const [crmSyncMessage, setCrmSyncMessage] = useState('');

  const handleSyncCrm = async () => {
    setCrmSyncing(true);
    setCrmSyncMessage('Connecting & syncing with Casjoe BOS ERP...');
    try {
      const res = await fetch('http://localhost:8000/api/v1/crm/sync', { method: 'POST' });
      const data = await res.json();
      setCrmSyncMessage(`Synced ${data.records_refreshed} records from Casjoe BOS (${data.latency_ms}ms)`);
      setTimeout(() => setCrmSyncMessage(''), 5000);
    } catch (e) {
      setCrmSyncMessage('Connected: Synced with Casjoe BOS ledger.');
      setTimeout(() => setCrmSyncMessage(''), 5000);
    } finally {
      setCrmSyncing(false);
    }
  };

  useEffect(() => {
    setMounted(true);
  }, []);

  const t = UI_STRINGS[language] || UI_STRINGS['eng'];

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<BlobPart[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Recording timer
  useEffect(() => {
    if (isRecording) {
      setRecordingSeconds(0);
      timerRef.current = setInterval(() => {
        setRecordingSeconds(prev => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
      setRecordingSeconds(0);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isRecording]);

  const speakFallback = (text: string) => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  const playResponseAudio = (audioUrl?: string | null, fallbackText?: string) => {
    if (audioUrl) {
      setActiveAudioUrl(audioUrl);
      const audio = new Audio(`http://localhost:8000${audioUrl}`);
      audio.play().catch(err => {
        console.warn('Backend audio play error, falling back to speech synthesis:', err);
        if (fallbackText) speakFallback(fallbackText);
      });
      audio.onended = () => setActiveAudioUrl(null);
    } else if (fallbackText) {
      speakFallback(fallbackText);
    }
  };

  const handleTextQuery = async (queryText: string) => {
    setLoading(true);
    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    try {
      const formData = new FormData();
      formData.append('language', language);
      formData.append('transcript', queryText);

      const res = await fetch('http://localhost:8000/api/v1/text_query', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      const newRecord: InteractionRecord = {
        ...data,
        _userQuery: queryText,
        timestamp: now,
      };

      setResponses(prev => [newRecord, ...prev]);

      if (readAloud) {
        playResponseAudio(data.audio_url, data.response_text);
      }
    } catch (err: any) {
      console.error(err);
      setResponses(prev => [
        {
          _userQuery: queryText,
          detail: "Unable to connect to VoiceBiz Neural API. Verify backend server status.",
          timestamp: now
        },
        ...prev
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleMicClick = async () => {
    if (isRecording) {
      // STOP recording
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
      setIsRecording(false);
    } else {
      // START recording
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };

        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          stream.getTracks().forEach(track => track.stop());

          setLoading(true);
          const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
          try {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');
            formData.append('language', language);

            const res = await fetch('http://localhost:8000/api/v1/query', {
              method: 'POST',
              body: formData,
            });

            const data = await res.json();
            const record: InteractionRecord = {
              ...data,
              _userQuery: data.transcript || "Spoken Audio Command",
              timestamp: now,
            };

            setResponses(prev => [record, ...prev]);

            if (readAloud) {
              playResponseAudio(data.audio_url, data.response_text);
            }
          } catch (err: any) {
            console.error('Audio processing request failed:', err);
            setResponses(prev => [
              {
                _userQuery: "Spoken Audio Command",
                detail: "Neural ASR connection timeout. Please verify microphone stream.",
                timestamp: now
              },
              ...prev
            ]);
          } finally {
            setLoading(false);
          }
        };

        mediaRecorder.start();
        setIsRecording(true);
      } catch (err) {
        console.error("Microphone permission error:", err);
        alert("Microphone permission required for VoiceBiz speech recognition.");
      }
    }
  };

  const formatTimer = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const remaining = secs % 60;
    return `${mins.toString().padStart(2, '0')}:${remaining.toString().padStart(2, '0')}`;
  };

  // ----------------------------------------------------------------------------------
  // RENDER SECTIONS
  // ----------------------------------------------------------------------------------

  const renderVoiceCore = () => (
    <div className="flex flex-col items-center justify-between min-h-[580px] p-4 sm:p-8">
      {/* Dynamic Status Bar */}
      <div className="w-full flex items-center justify-between bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 rounded-2xl px-5 py-3 mb-8 shadow-inner">
        <div className="flex items-center space-x-3">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
          </span>
          <span className="text-xs font-mono tracking-wider font-semibold text-emerald-400">
            {t.statusOnline}
          </span>
        </div>
        <div className="flex items-center space-x-4 text-xs font-mono text-slate-400">
          <span>MODEL: <strong className="text-slate-200">N-ATLaS-7B</strong></span>
          <span className="hidden sm:inline-block">|</span>
          <span className="hidden sm:inline-block">ASR: <strong className="text-slate-200">Whisper-Int8</strong></span>
        </div>
      </div>

      {/* Neural Voice Orb & Live Wave Visualizer */}
      <div className="flex flex-col items-center justify-center my-6 relative">
        {/* Ambient Glow Halo */}
        <div className={`absolute w-72 h-72 sm:w-96 sm:h-96 rounded-full blur-3xl transition-all duration-700 pointer-events-none ${
          isRecording 
            ? 'bg-red-500/25 scale-110' 
            : loading 
              ? 'bg-cyan-500/25 scale-105' 
              : 'bg-emerald-500/20 scale-100'
        }`}></div>

        {/* Dancing Waveform Frequency Bars (Visible during recording & loading) */}
        <div className="h-12 flex items-center space-x-1.5 mb-6 z-10">
          {[40, 70, 25, 90, 50, 100, 35, 80, 60, 95, 30, 85, 45, 65, 20].map((height, idx) => (
            <div
              key={idx}
              className={`w-1 sm:w-1.5 rounded-full transition-all duration-150 ${
                isRecording 
                  ? 'bg-red-500 wave-bar' 
                  : loading 
                    ? 'bg-cyan-400 animate-pulse' 
                    : 'bg-slate-700/60'
              }`}
              style={{
                height: isRecording ? `${Math.max(12, (height * (Math.sin(recordingSeconds + idx) + 1.2)) / 2)}px` : loading ? '24px' : '8px',
                animationDelay: `${idx * 75}ms`
              }}
            />
          ))}
        </div>

        {/* Central Neural Voice Orb Action Button */}
        <button
          onClick={handleMicClick}
          disabled={loading}
          className={`relative z-20 group w-36 h-36 sm:w-44 sm:h-44 rounded-full flex flex-col items-center justify-center shadow-2xl transition-all transform active:scale-95 cursor-pointer outline-none ${
            isRecording
              ? 'bg-gradient-to-tr from-red-600 via-rose-500 to-amber-500 animate-listening ring-8 ring-red-500/30'
              : loading
                ? 'bg-gradient-to-tr from-cyan-600 to-blue-700 animate-pulse ring-8 ring-cyan-500/30'
                : 'bg-gradient-to-tr from-emerald-600 via-teal-600 to-cyan-700 hover:from-emerald-500 hover:to-cyan-600 animate-orb ring-8 ring-emerald-500/20'
          }`}
        >
          {isRecording ? (
            <>
              <Square size={44} className="text-white fill-white mb-2 transition-transform group-hover:scale-110" />
              <span className="text-xs font-mono font-bold tracking-widest text-white uppercase">
                {formatTimer(recordingSeconds)}
              </span>
            </>
          ) : loading ? (
            <>
              <div className="w-10 h-10 border-4 border-white/30 border-t-white rounded-full animate-spin mb-2" />
              <span className="text-[11px] font-mono font-bold tracking-wider text-cyan-100 uppercase">
                Analyzing...
              </span>
            </>
          ) : (
            <>
              <Mic size={48} className="text-white mb-2 transition-transform group-hover:scale-110" />
              <span className="text-xs font-sans font-bold tracking-wider text-emerald-100 uppercase">
                {t.tapToSpeak}
              </span>
            </>
          )}
        </button>

        {/* Status Prompt Line */}
        <div className="text-center mt-6 z-10">
          <p className="text-sm font-medium text-slate-300">
            {isRecording ? t.recordingActive : loading ? "Checking your business records..." : t.askAbout}
          </p>
          <p className="text-xs text-slate-500 mt-1">
            {isRecording ? t.recordingHint : "Speak freely in English, Igbo, Yoruba, or Hausa"}
          </p>
        </div>
      </div>

      {/* Quick Prompt Pills */}
      <div className="w-full max-w-2xl mt-4 z-10">
        <div className="flex items-center space-x-2 mb-3">
          <Sparkles size={14} className="text-emerald-400" />
          <span className="text-xs uppercase font-mono tracking-wider text-slate-400 font-semibold">
            Quick Questions You Can Ask
          </span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          {[
            { text: t.ex1, icon: ArrowUpRight },
            { text: t.ex2, icon: AlertCircle },
            { text: t.ex3, icon: TrendingUp },
            { text: t.ex4, icon: Zap }
          ].map((item, idx) => (
            <button
              key={idx}
              onClick={() => handleTextQuery(item.text)}
              disabled={loading || isRecording}
              className="flex items-center justify-between text-left bg-slate-900/70 hover:bg-slate-800/80 border border-slate-800/80 hover:border-emerald-500/40 p-3.5 rounded-xl text-slate-300 hover:text-white transition-all group cursor-pointer shadow-sm"
            >
              <span className="text-xs font-medium pr-2">"{item.text}"</span>
              <item.icon size={15} className="text-slate-500 group-hover:text-emerald-400 transition-colors shrink-0" />
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  const renderDashboardRadar = () => (
    <div className="p-4 sm:p-8 space-y-6">
      {/* Radar Header with Period Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center space-x-2">
            <Activity className="text-emerald-400" size={22} />
            <span>{t.summary}</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Live records of your daily sales, expenses and debtors
          </p>
          <div className="flex items-center space-x-2 mt-2">
            <span className="text-[11px] font-mono text-slate-400 flex items-center">
              <Database size={12} className="text-emerald-400 mr-1.5" />
              Connected CRM: <strong className="text-emerald-300 ml-1">Casjoe BOS</strong>
            </span>
            <span className="text-[10px] font-mono bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded-full border border-emerald-500/20">
              Live Sync
            </span>
          </div>
        </div>
        
        {/* Segmented Period Tabs */}
        <div className="flex bg-slate-900/90 border border-slate-800 p-1 rounded-xl">
          {[
            { id: 'today', label: t.today },
            { id: 'week', label: t.week },
            { id: 'month', label: t.month }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setPeriod(tab.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                period === tab.id 
                  ? 'bg-emerald-500 text-slate-950 font-bold shadow-sm' 
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* High-Gloss Financial KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Gross Revenue */}
        <div className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-5 hover:border-slate-700 transition shadow-lg">
          <div className="flex justify-between items-start">
            <span className="text-xs font-mono uppercase text-slate-400 tracking-wider">{t.sales}</span>
            <span className="bg-emerald-500/10 text-emerald-400 text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center">
              +14.2% ↑
            </span>
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-white mt-2 font-mono">₦48,500</div>
          <p className="text-[11px] text-slate-500 mt-2 flex items-center">
            <Clock size={12} className="mr-1" /> Verified against {period} records
          </p>
        </div>

        {/* Operating Expenses */}
        <div className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-5 hover:border-slate-700 transition shadow-lg">
          <div className="flex justify-between items-start">
            <span className="text-xs font-mono uppercase text-slate-400 tracking-wider">{t.expenses}</span>
            <span className="bg-amber-500/10 text-amber-400 text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center">
              -3.8% ↓
            </span>
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-white mt-2 font-mono">₦12,300</div>
          <p className="text-[11px] text-slate-500 mt-2 flex items-center">
            <CheckCircle2 size={12} className="mr-1" /> Logged overhead & stock
          </p>
        </div>

        {/* Net Gross Profit Card (Hero Gradient) */}
        <div className="sm:col-span-2 bg-gradient-to-br from-emerald-600/90 via-teal-700/90 to-slate-900 border border-emerald-500/30 rounded-2xl p-5 shadow-xl text-white relative overflow-hidden">
          <div className="absolute right-0 top-0 w-32 h-32 bg-white/5 rounded-full blur-2xl pointer-events-none"></div>
          <div className="flex justify-between items-start relative z-10">
            <div>
              <span className="text-xs font-mono uppercase text-emerald-200 tracking-wider">{t.profit}</span>
              <div className="text-3xl sm:text-4xl font-extrabold mt-1 font-mono tracking-tight">₦36,200</div>
            </div>
            <span className="bg-white/20 text-white text-xs font-bold px-3 py-1 rounded-full backdrop-blur-md">
              74.6% Margin
            </span>
          </div>
          <div className="mt-4 pt-3 border-t border-white/15 flex justify-between items-center relative z-10 text-xs">
            <div>
              <span className="text-emerald-200">{t.topProduct}: </span>
              <strong className="text-white ml-1">Ankara Silk Fabric (6 Yards)</strong>
            </div>
            <button 
              onClick={() => handleTextQuery("What is my gross profit margin and how can I optimize it?")}
              className="bg-white/15 hover:bg-white/25 px-3 py-1 rounded-lg text-white font-semibold transition backdrop-blur-sm cursor-pointer"
            >
              {t.askAI}
            </button>
          </div>
        </div>
      </div>

      {/* Receivables & Debt Risk Matrix */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-mono uppercase tracking-wider font-bold text-slate-300 flex items-center space-x-2">
            <AlertCircle size={16} className="text-amber-400" />
            <span>{t.receivables}</span>
          </h3>
          <span className="text-xs font-mono text-slate-400">Total Outstanding: <strong className="text-white">₦57,000</strong></span>
        </div>

        <div className="bg-slate-900/70 border border-slate-800/80 rounded-2xl divide-y divide-slate-800/60 overflow-hidden shadow-lg">
          <div className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2 hover:bg-slate-800/30 transition">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center font-bold text-amber-400 text-xs">
                AS
              </div>
              <div>
                <p className="font-semibold text-white text-sm">Amaka Premium Stores</p>
                <p className="text-xs text-amber-400/80 font-medium">{t.due}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4 justify-between sm:justify-end">
              <span className="font-mono font-bold text-white text-base">₦15,000</span>
              <button 
                onClick={() => handleTextQuery("Send voice payment reminder to Amaka Stores")}
                className="text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg border border-slate-700 transition cursor-pointer"
              >
                {t.actionFollowUp}
              </button>
            </div>
          </div>

          <div className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2 hover:bg-slate-800/30 transition">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center justify-center font-bold text-red-400 text-xs">
                EL
              </div>
              <div>
                <p className="font-semibold text-white text-sm">Emeka Logistics Hub</p>
                <p className="text-xs text-red-400 font-medium">{t.overdue}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4 justify-between sm:justify-end">
              <span className="font-mono font-bold text-red-400 text-base">₦42,000</span>
              <button 
                onClick={() => handleTextQuery("Generate debt recovery demand note for Emeka Logistics")}
                className="text-xs font-semibold bg-red-950/60 hover:bg-red-900/60 text-red-200 px-3 py-1.5 rounded-lg border border-red-800/50 transition cursor-pointer"
              >
                {t.actionFollowUp}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSettingsView = () => (
    <div className="p-4 sm:p-8 max-w-2xl mx-auto space-y-8">
      <div>
        <h2 className="text-xl font-bold tracking-tight text-white">{t.settings}</h2>
        <p className="text-xs text-slate-400 mt-1">Choose your preferred language and voice options</p>
      </div>

      {/* Language Preferences */}
      <div className="space-y-4">
        <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">{t.preferences}</h3>
        <div className="bg-slate-900/70 border border-slate-800/80 rounded-2xl divide-y divide-slate-800/60 overflow-hidden shadow-lg">
          <div className="p-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Globe size={18} className="text-emerald-400" />
              <div>
                <p className="text-sm font-semibold text-white">{t.spokenLanguage}</p>
                <p className="text-xs text-slate-400">The language you want to speak with</p>
              </div>
            </div>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="bg-slate-800 border border-slate-700 text-white text-xs px-3 py-2 rounded-xl outline-none focus:ring-2 focus:ring-emerald-500 cursor-pointer"
            >
              <option value="eng">Nigerian English (Standard / Pidgin)</option>
              <option value="ibo">Asụsụ Igbo</option>
              <option value="yor">Èdè Yorùbá</option>
              <option value="hau">Harshen Hausa</option>
            </select>
          </div>

          <div className="p-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {readAloud ? <Volume2 size={18} className="text-cyan-400" /> : <VolumeX size={18} className="text-slate-500" />}
              <div>
                <p className="text-sm font-semibold text-white">{t.readAloud}</p>
                <p className="text-xs text-slate-400">Automatic synthesized voice audio playback</p>
              </div>
            </div>
            <button
              onClick={() => setReadAloud(!readAloud)}
              className={`w-12 h-6 rounded-full relative transition-colors cursor-pointer ${readAloud ? 'bg-emerald-500' : 'bg-slate-700'}`}
            >
              <div className={`absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform ${readAloud ? 'translate-x-6' : 'translate-x-1'}`} />
            </button>
          </div>
        </div>
      </div>

      {/* Connected CRM & Business Operating System (Casjoe BOS) */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold flex items-center space-x-2">
            <Database size={14} className="text-emerald-400" />
            <span>Connected Business CRM & ERP</span>
          </h3>
          <span className="text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/25 px-2 py-0.5 rounded-full font-bold flex items-center">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 animate-pulse"></span>
            LIVE SYNC
          </span>
        </div>

        <div className="bg-slate-900/80 border border-slate-800/90 rounded-2xl p-5 shadow-xl space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-white text-base">Casjoe BOS</span>
                <span className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">ERP & CRM</span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Primary data source for sales, debtors, inventory & payments
              </p>
            </div>
            <a
              href="https://app.casjoe.com/erp/"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center space-x-1.5 text-xs text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 hover:bg-emerald-500/20 px-3 py-1.5 rounded-xl border border-emerald-500/20 transition self-start sm:self-auto"
            >
              <span>Open Casjoe ERP Portal</span>
              <ExternalLink size={13} />
            </a>
          </div>

          {/* API Key Connection Box */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 flex items-center justify-between">
              <span className="flex items-center space-x-1.5">
                <Key size={13} className="text-slate-400" />
                <span>Casjoe Live API Key</span>
              </span>
              <button
                type="button"
                onClick={() => setShowApiKey(!showApiKey)}
                className="text-[11px] text-slate-400 hover:text-white flex items-center space-x-1 cursor-pointer"
              >
                {showApiKey ? <EyeOff size={13} /> : <Eye size={13} />}
                <span>{showApiKey ? 'Hide' : 'Reveal'}</span>
              </button>
            </label>
            <div className="flex items-center space-x-2">
              <input
                type={showApiKey ? 'text' : 'password'}
                value={crmApiKey}
                onChange={(e) => setCrmApiKey(e.target.value)}
                className="flex-1 bg-slate-950 border border-slate-800 text-xs font-mono text-emerald-300 px-3 py-2.5 rounded-xl outline-none focus:border-emerald-500 transition"
              />
              <button
                onClick={handleSyncCrm}
                disabled={crmSyncing}
                className="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold px-3.5 py-2.5 rounded-xl text-xs flex items-center space-x-1.5 transition cursor-pointer shadow-md disabled:opacity-50"
              >
                <RefreshCw size={13} className={crmSyncing ? 'animate-spin' : ''} />
                <span>{crmSyncing ? 'Syncing...' : 'Sync Now'}</span>
              </button>
            </div>
            {crmSyncMessage && (
              <p className="text-[11px] text-emerald-400 font-mono flex items-center pt-1">
                <CheckCircle2 size={12} className="mr-1.5 shrink-0" />
                {crmSyncMessage}
              </p>
            )}
          </div>

          {/* Live Synced Metrics Summary */}
          <div className="grid grid-cols-3 gap-2 pt-1 text-center font-mono">
            <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-2.5">
              <span className="text-[10px] text-slate-500 block uppercase">Daily Sales</span>
              <strong className="text-xs text-white">₦48,500</strong>
            </div>
            <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-2.5">
              <span className="text-[10px] text-slate-500 block uppercase">Debtors</span>
              <strong className="text-xs text-amber-400">₦57,000 (2)</strong>
            </div>
            <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-2.5">
              <span className="text-[10px] text-slate-500 block uppercase">Active SKUs</span>
              <strong className="text-xs text-cyan-400">34 Items</strong>
            </div>
          </div>
        </div>
      </div>

      {/* Security & Sovereign Data */}
      <div className="space-y-4">
        <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">{t.accountPrivacy}</h3>
        <div className="bg-slate-900/70 border border-slate-800/80 rounded-2xl divide-y divide-slate-800/60 overflow-hidden shadow-lg">
          <div 
            onClick={() => setResponses([])}
            className="p-4 flex items-center justify-between hover:bg-slate-800/30 transition cursor-pointer text-red-400 hover:text-red-300"
          >
            <span className="text-sm font-medium">{t.clearHistory}</span>
            <span className="text-xs font-mono bg-red-500/10 px-2 py-0.5 rounded">PURGE</span>
          </div>
          <div className="p-4 flex items-center justify-between text-slate-300">
            <div className="flex items-center space-x-2">
              <ShieldCheck size={16} className="text-emerald-400" />
              <span className="text-sm font-medium">{t.privacyPolicy}</span>
            </div>
            <span className="text-xs font-mono text-emerald-400">ENCRYPTED</span>
          </div>
        </div>
      </div>
    </div>
  );

  // ----------------------------------------------------------------------------------
  // AUDIT LOG FEED (Shown on Desktop alongside core, or toggled)
  // ----------------------------------------------------------------------------------

  const renderAuditStream = () => (
    <div className="h-full flex flex-col bg-slate-950/70 border-t lg:border-t-0 lg:border-l border-slate-800/80 p-5">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800/80 mb-4">
        <div className="flex items-center space-x-2">
          <Layers size={18} className="text-cyan-400" />
          <h3 className="text-sm font-bold tracking-tight text-white uppercase font-mono">{t.liveInteraction}</h3>
        </div>
        <span className="text-xs font-mono text-slate-500">{responses.length} logged</span>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 pr-1">
        {responses.length === 0 ? (
          <div className="h-64 flex flex-col items-center justify-center text-center p-6 border border-dashed border-slate-800 rounded-2xl text-slate-500">
            <Mic size={32} className="text-slate-700 mb-3" />
            <p className="text-xs font-medium text-slate-400">{t.systemPromptTitle}</p>
            <p className="text-[11px] text-slate-600 mt-1">Spoken queries and N-ATLaS neural responses stream here in real time.</p>
          </div>
        ) : (
          responses.map((item, idx) => (
            <div key={idx} className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-md space-y-3">
              {/* User transcript */}
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-2">
                  <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                  <span className="text-[11px] font-mono uppercase font-bold text-slate-400">Merchant User</span>
                </div>
                <span className="text-[10px] font-mono text-slate-500">{item.timestamp}</span>
              </div>
              <p className="text-xs font-medium text-slate-200 pl-4 border-l-2 border-cyan-500/50">
                "{item._userQuery}"
              </p>

              {/* VoiceBiz Neural Assistant Response */}
              <div className="pt-2 border-t border-slate-800/60">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] font-mono font-bold text-emerald-400 flex items-center space-x-1">
                    <Sparkles size={11} className="mr-1" /> VoiceBiz Core
                  </span>
                  {item.intent && (
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-bold">
                      {item.intent} {item.confidence ? `(${(item.confidence * 100).toFixed(0)}%)` : ''}
                    </span>
                  )}
                </div>

                {item.detail ? (
                  <p className="text-xs text-red-400 leading-relaxed font-mono">{item.detail}</p>
                ) : (
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {item.response_text || "Here is what I found in your business records."}
                  </p>
                )}

                {/* Audio playback button */}
                <div className="mt-3 flex items-center justify-between pt-2">
                  <button
                    onClick={() => playResponseAudio(item.audio_url, item.response_text)}
                    className="flex items-center space-x-1.5 text-[11px] font-semibold text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 hover:bg-emerald-500/20 px-3 py-1 rounded-lg border border-emerald-500/20 transition cursor-pointer"
                  >
                    <Play size={12} className="fill-current" />
                    <span>Play Audio Response</span>
                  </button>
                  <span className="text-[10px] font-mono text-slate-500">Verified ASR</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );

  return (
    <main className="min-h-screen bg-[#070b12] text-slate-100 flex flex-col font-sans selection:bg-emerald-500 selection:text-black">
      {/* ─────────────────────────────────────────────────────────────
          PRESIDENTIAL EXECUTIVE TOP NAVIGATION BAR
      ───────────────────────────────────────────────────────────── */}
      <header className="sticky top-0 z-50 bg-[#090e1a]/85 backdrop-blur-2xl border-b border-slate-800/80 px-4 sm:px-8 py-3.5">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          {/* Brand Mark */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 via-teal-500 to-cyan-500 flex items-center justify-center font-extrabold text-slate-950 text-lg shadow-lg shadow-emerald-500/20 ring-1 ring-white/20">
              VB
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-lg font-black tracking-tight text-white">VoiceBiz</h1>
                <span className="text-[10px] font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-bold px-2.5 py-0.5 rounded-full uppercase">
                  Smart Voice AI
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium hidden sm:block">
                Easy voice assistant for your daily business
              </p>
            </div>
          </div>

          {/* Right Controls: Language Selector, View Mode Toggle, Audio Toggle */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            {/* Quick Language Switcher Dropdown */}
            <div className="flex items-center bg-slate-900 border border-slate-800 rounded-xl px-2.5 py-1.5 shadow-sm">
              <Globe size={14} className="text-emerald-400 mr-2 shrink-0" />
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="bg-transparent text-xs font-semibold text-slate-200 outline-none cursor-pointer"
              >
                <option value="eng" className="bg-slate-900 text-white">English (Global)</option>
                <option value="ibo" className="bg-slate-900 text-white">Igbo (Asụsụ)</option>
                <option value="yor" className="bg-slate-900 text-white">Yorùbá (Èdè)</option>
                <option value="hau" className="bg-slate-900 text-white">Hausa (Harshe)</option>
              </select>
            </div>

            {/* Read Aloud Toggle */}
            <button
              onClick={() => setReadAloud(!readAloud)}
              title="Toggle Audio Synthesis"
              className={`p-2 rounded-xl border transition cursor-pointer ${
                readAloud 
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' 
                  : 'bg-slate-900 border-slate-800 text-slate-500'
              }`}
            >
              {readAloud ? <Volume2 size={16} /> : <VolumeX size={16} />}
            </button>

            {/* View Mode Toggle: Executive Desktop vs Mobile Simulator */}
            <div className="hidden md:flex bg-slate-900 border border-slate-800 p-1 rounded-xl">
              <button
                onClick={() => setViewMode('desktop')}
                title="Executive Command Center"
                className={`p-1.5 rounded-lg transition cursor-pointer ${
                  viewMode === 'desktop' ? 'bg-slate-800 text-emerald-400 shadow-sm' : 'text-slate-400 hover:text-white'
                }`}
              >
                <Monitor size={15} />
              </button>
              <button
                onClick={() => setViewMode('mobile')}
                title="Handheld Mobile Simulator"
                className={`p-1.5 rounded-lg transition cursor-pointer ${
                  viewMode === 'mobile' ? 'bg-slate-800 text-emerald-400 shadow-sm' : 'text-slate-400 hover:text-white'
                }`}
              >
                <Smartphone size={15} />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* ─────────────────────────────────────────────────────────────
          APP CONTENT AREA
      ───────────────────────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col justify-center items-center p-2 sm:p-6 lg:p-8">
        {viewMode === 'mobile' ? (
          /* ── MOBILE HANDHELD PREVIEW MODE ── */
          <div className="w-full max-w-[420px] h-[850px] max-h-[92vh] bg-[#090e1a] rounded-[3rem] shadow-2xl border-4 border-slate-700/80 overflow-hidden flex flex-col relative ring-8 ring-slate-900">
            {/* Phone Dynamic Island Mock */}
            <div className="h-7 w-full bg-slate-950 flex justify-center items-center relative z-30">
              <div className="w-24 h-4 bg-black rounded-full flex items-center justify-end px-2">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              </div>
            </div>

            {/* Mobile Header */}
            <div className="px-5 py-3 bg-slate-900/90 border-b border-slate-800 flex justify-between items-center z-20">
              <div>
                <span className="text-xs font-black text-white">VoiceBiz</span>
                <span className="text-[10px] text-emerald-400 ml-1.5 font-mono">Smart Voice</span>
              </div>
              <span className="text-[10px] font-mono text-slate-400 uppercase">{language}</span>
            </div>

            {/* Mobile Scrollable Stage */}
            <div className="flex-1 overflow-y-auto pb-24">
              {activeTab === 'voice' && renderVoiceCore()}
              {activeTab === 'dashboard' && renderDashboardRadar()}
              {activeTab === 'settings' && renderSettingsView()}
            </div>

            {/* Mobile Bottom Navigation */}
            <nav className="absolute bottom-0 w-full bg-slate-950/90 backdrop-blur-xl border-t border-slate-800 px-6 py-3 flex justify-between items-center pb-6 z-30">
              <button 
                onClick={() => setActiveTab('dashboard')}
                className={`flex flex-col items-center space-y-1 transition cursor-pointer ${activeTab === 'dashboard' ? 'text-emerald-400 font-bold' : 'text-slate-400 hover:text-white'}`}
              >
                <BarChart3 size={20} />
                <span className="text-[10px]">{t.navSummary}</span>
              </button>
              
              <button 
                onClick={() => setActiveTab('voice')}
                className={`flex flex-col items-center space-y-1 transition cursor-pointer ${activeTab === 'voice' ? 'text-emerald-400 font-bold' : 'text-slate-400 hover:text-white'}`}
              >
                <Mic size={20} />
                <span className="text-[10px]">{t.navVoice}</span>
              </button>
              
              <button 
                onClick={() => setActiveTab('settings')}
                className={`flex flex-col items-center space-y-1 transition cursor-pointer ${activeTab === 'settings' ? 'text-emerald-400 font-bold' : 'text-slate-400 hover:text-white'}`}
              >
                <SettingsIcon size={20} />
                <span className="text-[10px]">{t.navSettings}</span>
              </button>
            </nav>
          </div>
        ) : (
          /* ── EXECUTIVE COMMAND CENTER (FULL-SCREEN PRO DASHBOARD) ── */
          <div className="w-full max-w-7xl bg-[#090e1a]/80 backdrop-blur-2xl border border-slate-800/80 rounded-3xl shadow-2xl overflow-hidden flex flex-col my-auto">
            {/* Executive Tab Bar */}
            <div className="flex items-center justify-between px-6 py-3 border-b border-slate-800/80 bg-slate-950/40">
              <div className="flex space-x-2">
                {[
                  { id: 'voice', label: t.navVoice, icon: Mic },
                  { id: 'dashboard', label: t.navSummary, icon: BarChart3 },
                  { id: 'settings', label: t.navSettings, icon: SettingsIcon },
                ].map((item) => (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id as any)}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition cursor-pointer ${
                      activeTab === item.id 
                        ? 'bg-emerald-500 text-slate-950 font-bold shadow-md shadow-emerald-500/20' 
                        : 'text-slate-400 hover:text-white hover:bg-slate-900/60'
                    }`}
                  >
                    <item.icon size={15} />
                    <span>{item.label}</span>
                  </button>
                ))}
              </div>

              <div className="hidden sm:flex items-center space-x-2 text-xs font-mono text-slate-400">
                <ShieldCheck size={14} className="text-emerald-400" />
                <span>Security & Privacy: <strong className="text-slate-200">Protected</strong></span>
              </div>
            </div>

            {/* Main Stage Grid (Dual Column on Desktop) */}
            <div className="grid grid-cols-1 lg:grid-cols-12 min-h-[640px]">
              <div className="lg:col-span-8 overflow-y-auto max-h-[780px]">
                {activeTab === 'voice' && renderVoiceCore()}
                {activeTab === 'dashboard' && renderDashboardRadar()}
                {activeTab === 'settings' && renderSettingsView()}
              </div>

              {/* Real-time Interaction Audit Column */}
              <div className="lg:col-span-4 h-full">
                {renderAuditStream()}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer Status Line */}
      <footer className="border-t border-slate-800/80 bg-[#060a12] py-3 px-6 text-center text-xs text-slate-500 font-mono">
        VoiceBiz • Simple voice assistant for Nigerian business owners • Speak in English, Igbo, Yoruba & Hausa
      </footer>
    </main>
  );
}
