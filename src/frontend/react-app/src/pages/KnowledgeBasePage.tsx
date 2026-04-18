import React from 'react';
import { Search, Loader2, CheckCircle2, Sparkles } from 'lucide-react';
import QuestionCard from '../components/QuestionCard';
import type { Question } from '../components/QuestionCard';

interface KnowledgeBasePageProps {
  questions: Question[];
  loading: boolean;
  query: string;
  setQuery: (query: string) => void;
  status: string | null;
}

const KnowledgeBasePage: React.FC<KnowledgeBasePageProps> = ({
  questions, loading, query, setQuery, status
}) => {
  return (
    <div className="p-6 lg:p-8 max-w-4xl mx-auto space-y-6 w-full">
      <h2 className="text-xl font-bold tracking-tight text-text-main">Knowledge Base</h2>

      {status && (
        <div className="p-3 rounded-lg flex items-center gap-2 text-[13px] font-semibold animate-slide-up bg-primary-faint border border-primary/15 text-primary">
          <CheckCircle2 className="w-4 h-4" />{status}
        </div>
      )}

      <div className="space-y-5">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-faint" />
          <input id="kb-search-input" type="text" placeholder="Search topics..."
            className="input pl-9 h-11 text-[14px] font-medium w-full shadow-sm" value={query} onChange={(e) => setQuery(e.target.value)}
          />
        </div>

        <div>
          {loading ? (
            <div className="flex flex-col items-center justify-center h-40 space-y-3">
              <Loader2 className="w-6 h-6 animate-spin text-primary" />
              <p className="text-[13px] font-medium text-text-main">Retrieving...</p>
            </div>
          ) : questions.length > 0 ? (
            <div className="space-y-4 animate-fade-in">
              <div className="flex items-center gap-2.5 pb-2 border-b border-surface-border">
                <div className="w-6 h-6 rounded flex items-center justify-center text-[10px] text-white font-bold bg-primary shadow-sm">{questions.length}</div>
                <h3 className="font-semibold text-[14px] text-text-main">Results</h3>
              </div>
              <div className="grid grid-cols-1 gap-3">
                {questions.map((q, i) => <QuestionCard key={i} question={q} index={i + 1} />)}
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-10">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-3 bg-surface-secondary border border-surface-border animate-float">
                <Sparkles className="w-5 h-5 text-text-faint" />
              </div>
              <p className="text-text-muted text-[13px]">Ready to search</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default KnowledgeBasePage;
