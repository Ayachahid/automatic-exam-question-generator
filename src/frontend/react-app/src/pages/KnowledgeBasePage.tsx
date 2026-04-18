import React from 'react';
import { Database, Search, Loader2, CheckCircle2, Sparkles, Upload, Trash2 } from 'lucide-react';
import QuestionCard from '../components/QuestionCard';
import type { Question } from '../components/QuestionCard';

interface KnowledgeBasePageProps {
  questions: Question[];
  loading: boolean;
  query: string;
  setQuery: (query: string) => void;
  status: string | null;
  kbFiles: string[];
  onIndexFiles: (files: FileList) => void;
  resetKBAction: () => void;
  indexing: boolean;
}

const KnowledgeBasePage: React.FC<KnowledgeBasePageProps> = ({
  questions, loading, query, setQuery, status, kbFiles, onIndexFiles, resetKBAction, indexing
}) => {
  return (
    <div className="flex flex-col lg:flex-row h-full min-h-full">
      {/* Main Content (Left) */}
      <div className="flex-1 min-w-0 p-6 lg:p-8 border-r border-surface-border">
        <div className="max-w-3xl mx-auto space-y-6">
          <header>
            <h2 className="text-2xl font-bold tracking-tight text-text-main">Knowledge Base</h2>
            <p className="text-text-muted mt-1 text-[14px]">Generate targeted questions from your indexed material library.</p>
          </header>

          {status && (
            <div className="p-3 rounded-lg flex items-center gap-2 text-[13px] font-semibold animate-slide-up bg-primary-faint border border-primary/15 text-primary">
              <CheckCircle2 className="w-4 h-4" />{status}
            </div>
          )}

          <div className="space-y-5">
            <div className="card">
              <h3 className="font-semibold text-[11px] uppercase tracking-widest text-primary mb-4 text-center">Search Knowledge Base</h3>
              <div className="relative max-w-xl mx-auto">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-faint" />
                <input id="kb-search-input" type="text" placeholder="Ask about a specific topic (e.g. 'Backpropagation')..."
                  className="input pl-10 h-11 text-[14px] font-medium w-full shadow-inner" value={query} onChange={(e) => setQuery(e.target.value)}
                />
              </div>
              <p className="mt-3 text-[10px] text-text-faint font-medium flex items-center justify-center gap-1.5 uppercase tracking-wider">
                <Database className="w-3 h-3" />Context is retrieved from your documents automatically.
              </p>
            </div>

            <div>
              {loading ? (
                <div className="flex flex-col items-center justify-center h-48 space-y-4">
                  <Loader2 className="w-8 h-8 animate-spin text-primary" />
                  <div className="text-center">
                    <p className="text-[14px] font-semibold text-text-main">Retrieving Context</p>
                    <p className="text-[13px] text-text-muted mt-0.5">Searching documents and generating questions...</p>
                  </div>
                </div>
              ) : questions.length > 0 ? (
                <div className="space-y-4 animate-fade-in">
                  <div className="flex items-center gap-2.5 pb-3 border-b border-surface-border">
                    <div className="w-7 h-7 rounded-md flex items-center justify-center text-[11px] text-white font-bold bg-primary shadow-sm">{questions.length}</div>
                    <h3 className="font-semibold text-[15px] text-text-main">Retrieved Questions</h3>
                  </div>
                  <div className="grid grid-cols-1 gap-3">
                    {questions.map((q, i) => <QuestionCard key={i} question={q} index={i + 1} />)}
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-16 rounded-xl border border-dashed border-surface-border bg-surface">
                  <div className="w-14 h-14 rounded-xl flex items-center justify-center mb-4 bg-surface-secondary border border-surface-border animate-float">
                    <Sparkles className="w-6 h-6 text-text-faint" />
                  </div>
                  <h4 className="text-lg font-semibold text-text-main">Library Standby</h4>
                  <p className="text-text-muted max-w-sm mt-1.5 text-center text-[13px]">
                    Enter a topic above and use the panel on the right to manage your documents.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* KB Management Sidebar (Right) */}
      <div className="w-full lg:w-72 shrink-0 bg-surface flex flex-col h-[calc(100vh-3rem)] sticky top-12 border-l border-surface-border">
        <div className="px-4 py-3 border-b border-surface-border flex items-center gap-2 shrink-0 bg-surface">
          <Database className="text-text-muted w-4 h-4" />
          <h3 className="font-semibold text-[13px] text-text-main">KB Management</h3>
        </div>

        <div className="p-4 space-y-6 overflow-y-auto flex-1 custom-scrollbar">
          <div className="space-y-2 shrink-0">
            <label className="text-[10px] font-semibold text-primary uppercase tracking-[0.12em]">Actions</label>
            <div className="flex flex-col gap-2">
              <label className="flex items-center gap-2.5 p-2 rounded-lg border border-surface-border bg-primary-faint text-primary hover:bg-primary/10 transition-colors cursor-pointer group shadow-sm">
                <div className="w-7 h-7 shrink-0 rounded-md flex items-center justify-center bg-white border border-primary/20">
                  {indexing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Upload className="w-3.5 h-3.5 group-hover:scale-110 transition-transform" />}
                </div>
                <span className="text-[12px] font-semibold">Add Documents</span>
                <input type="file" className="hidden" multiple onChange={(e) => e.target.files && onIndexFiles(e.target.files)} />
              </label>
              
              <button 
                id="kb-clear-btn"
                onClick={resetKBAction}
                className="flex items-center gap-2.5 p-2 rounded-lg border border-danger-border bg-danger-bg text-danger-text hover:bg-danger/10 transition-colors group shadow-sm text-left"
              >
                <div className="w-7 h-7 shrink-0 rounded-md flex items-center justify-center bg-white border border-danger/20">
                  <Trash2 className="w-3.5 h-3.5 group-hover:scale-110 transition-transform" />
                </div>
                <span className="text-[12px] font-semibold">Clear Knowledge Base</span>
              </button>
            </div>
          </div>
          
          <div className="space-y-2 pt-1 border-t border-surface-border">
            <div className="flex items-center justify-between shrink-0 pt-3">
              <label className="text-[10px] font-semibold text-text-muted uppercase tracking-[0.12em]">Indexed Files</label>
              <span className="text-[10px] font-bold text-primary bg-primary-faint px-1.5 py-0.5 rounded">{kbFiles.length}</span>
            </div>
            <div className="space-y-2">
              {kbFiles.length > 0 ? kbFiles.map((file, idx) => (
                <div key={idx} title={file} className="flex items-center gap-2 px-2.5 py-2 rounded-md text-[11px] text-text-secondary font-medium bg-surface-secondary border border-surface-border shadow-sm">
                  <Database className="w-3 h-3 text-primary shrink-0" />
                  <span className="truncate block leading-tight">{file}</span>
                </div>
              )) : (
                <div className="py-8 text-center border border-dashed border-surface-border rounded-lg bg-surface-secondary flex flex-col items-center justify-center gap-2">
                  <Database className="w-5 h-5 text-text-faint" />
                  <p className="text-[11px] text-text-muted">No documents indexed yet.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeBasePage;
