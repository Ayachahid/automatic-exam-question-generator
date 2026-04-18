import { useState, useEffect } from 'react';
import SettingsSidebar from './components/SettingsSidebar';
import GeneratePage from './pages/GeneratePage';
import KnowledgeBasePage from './pages/KnowledgeBasePage';
import DocumentsPage from './pages/DocumentsPage';
import { 
  Search, 
  SlidersHorizontal,
  BrainCircuit,
  Database,
  Library,
  Sparkles
} from 'lucide-react';
import { cn } from './lib/utils';
import { generateQuestions, generateRAGQuestions, listKBFiles, uploadFile, indexDocuments, resetKB } from './lib/api';
import type { Question } from './components/QuestionCard';

export type TabType = 'generate' | 'kb' | 'docs';

function App() {
  const [currentTab, setCurrentTab] = useState<TabType>('generate');
  const [showSettings, setShowSettings] = useState(true);
  
  const [type, setType] = useState('multiple_choice');
  const [difficulty, setDifficulty] = useState('medium');
  const [count, setCount] = useState(5);
  const [loading, setLoading] = useState(false);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [error, setError] = useState<string | null>(null);

  const [kbFiles, setKbFiles] = useState<string[]>([]);
  const [indexing, setIndexing] = useState(false);
  const [kbStatus, setKbStatus] = useState<string | null>(null);

  const [filePath, setFilePath] = useState<string | null>(null);
  const [rawText, setRawText] = useState('');
  const [kbQuery, setKbQuery] = useState('');

  useEffect(() => { fetchKBFiles(); }, []);

  const fetchKBFiles = async () => {
    try { const data = await listKBFiles(); setKbFiles(data); } catch { console.error('Failed to fetch KB files'); }
  };

  const handleIndexFiles = async (files: FileList) => {
    setIndexing(true); setKbStatus('Uploading and indexing...');
    try {
      // Parallel upload for speed
      const uploadPromises = Array.from(files).map((file) => uploadFile(file));
      const uploadResults = await Promise.all(uploadPromises);
      const filePaths = uploadResults.map((data) => data.file_path);
      const newFileNames = Array.from(files).map((f) => f.name);

      // Optimistic UI update so files show up instantly
      setKbFiles((prev) => [...new Set([...prev, ...newFileNames])].sort());

      // Start background indexing API
      await indexDocuments(filePaths); 
      
      setKbStatus('Success: Documents added!'); 
      setTimeout(() => setKbStatus(null), 3000);
    } catch { 
      setKbStatus('Error analyzing files'); 
      setTimeout(() => setKbStatus(null), 3000);
    } finally { 
      setIndexing(false); 
    }
  };

  const handleResetKB = async () => {
    if (!window.confirm('Wipe Knowledge Base? This cannot be undone.')) return;
    try { await resetKB(); setKbFiles([]); setQuestions([]); setKbStatus('Library cleared'); setTimeout(() => setKbStatus(null), 3000); } catch { setKbStatus('Reset failed'); }
  };

  const handleGlobalGenerate = async () => {
    setLoading(true); setError(null); setQuestions([]);
    try {
      if (currentTab === 'generate') {
        if (!filePath && !rawText.trim()) { setError('Please upload a file or paste text first.'); setLoading(false); return; }
        const payload = { question_type: type, difficulty, num_questions: count, file_path: filePath, text: rawText.trim() || undefined };
        const data = await generateQuestions(payload);
        const mappedQuestions = data.questions.map((q: any) => ({ ...q, question_type: type }));
        setQuestions(mappedQuestions);
      } else if (currentTab === 'kb') {
        if (!kbQuery.trim()) { setError('Please enter a subject or topic for the Knowledge Base.'); setLoading(false); return; }
        const payload = { query: kbQuery.trim(), question_type: type, difficulty, num_questions: count, n_results: 3 };
        const data = await generateRAGQuestions(payload);
        const mappedQuestions = data.questions.map((q: any) => ({ ...q, question_type: type }));
        setQuestions(mappedQuestions);
      }
    } catch { setError('Generation failed. Ensure backend is running.'); } finally { setLoading(false); }
  };

  const navItems = [
    { id: 'generate', label: 'Generation', icon: BrainCircuit },
    { id: 'kb', label: 'Knowledge Base', icon: Database },
    { id: 'docs', label: 'Library', icon: Library },
  ];

  const renderContent = () => {
    switch (currentTab) {
      case 'generate':
        return <GeneratePage questions={questions} loading={loading} error={error} filePath={filePath} setFilePath={setFilePath} rawText={rawText} setRawText={setRawText} />;
      case 'kb':
        return <KnowledgeBasePage questions={questions} loading={loading} query={kbQuery} setQuery={setKbQuery} status={kbStatus} />;
      case 'docs':
        return <DocumentsPage kbFiles={kbFiles} onIndexFiles={handleIndexFiles} resetKBAction={handleResetKB} indexing={indexing} />;
      default:
        return null;
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-background">
      {/* Header */}
      <header className="h-12 flex items-center justify-between px-4 sticky top-0 z-30 border-b border-surface-border bg-surface shrink-0">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-md flex items-center justify-center bg-primary">
              <Sparkles className="text-white w-3.5 h-3.5" />
            </div>
            <h1 className="font-bold text-sm tracking-tight text-text-main">ExamGen</h1>
          </div>

          <nav className="flex items-center gap-0.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  id={`nav-${item.id}`}
                  onClick={() => { setCurrentTab(item.id as TabType); setQuestions([]); setError(null); }}
                  className={cn(
                    "flex items-center gap-1.5 px-3 py-1 rounded-md text-[13px] font-medium transition-colors duration-150",
                    isActive
                      ? "bg-surface-tertiary text-text-main"
                      : "text-text-muted hover:text-text-main hover:bg-surface-secondary"
                  )}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {item.label}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="flex items-center gap-2">
          <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-md border border-surface-border bg-surface-secondary w-48 focus-within:border-primary/40 transition-colors">
            <Search className="w-3.5 h-3.5 text-text-faint" />
            <input type="text" placeholder="Search..." className="bg-transparent border-none outline-none w-full text-[12px] text-text-main placeholder:text-text-faint" id="global-search-input" />
          </div>
          <button id="settings-toggle-btn" onClick={() => setShowSettings(!showSettings)}
            className={cn("p-1.5 rounded-md transition-colors", showSettings ? "bg-primary-faint text-primary" : "text-text-muted hover:text-text-main hover:bg-surface-secondary")}
          >
            <SlidersHorizontal className="w-4 h-4" />
          </button>
          <div className="h-4 w-px bg-surface-border" />
          <div className="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-semibold text-primary bg-primary-faint">AT</div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden w-full">
        {/* Sidebar */}
        {showSettings && currentTab !== 'docs' && (
          <SettingsSidebar
            type={type} setType={setType}
            difficulty={difficulty} setDifficulty={setDifficulty}
            count={count} setCount={setCount}
            onGenerate={handleGlobalGenerate}
            loading={loading}
            isOpen={showSettings}
            currentTab={currentTab}
          />
        )}

        {/* Main */}
        <main className="flex-1 overflow-y-auto overflow-x-hidden min-w-0">
          {renderContent()}
        </main>
      </div>
    </div>
  );
}

export default App;
