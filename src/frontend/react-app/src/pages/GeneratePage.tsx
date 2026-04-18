import React, { useState } from 'react';
import { Upload, FileText, Loader2, AlertCircle, Type, FileUp, Sparkles } from 'lucide-react';
import { uploadFile } from '../lib/api';
import QuestionCard from '../components/QuestionCard';
import type { Question } from '../components/QuestionCard';
import { cn } from '../lib/utils';

interface GeneratePageProps {
  questions: Question[];
  loading: boolean;
  error: string | null;
  filePath: string | null;
  setFilePath: (path: string | null) => void;
  rawText: string;
  setRawText: (text: string) => void;
}

type InputMethod = 'file' | 'text';

const GeneratePage: React.FC<GeneratePageProps> = ({
  questions, loading, error, filePath, setFilePath, rawText, setRawText,
}) => {
  const [fileName, setFileName] = useState<string | null>(null);
  const [inputMethod, setInputMethod] = useState<InputMethod>('file');

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFileName(selectedFile.name);
      try { const data = await uploadFile(selectedFile); setFilePath(data.file_path); } catch { console.error('Failed to upload file'); }
    }
  };

  return (
    <div className="space-y-6 p-6 lg:p-8 max-w-4xl mx-auto w-full">
      <header>
        <h2 className="text-2xl font-bold tracking-tight text-text-main">Generate Questions</h2>
        <p className="text-text-muted mt-1 text-[14px]">Choose your source and create professional assessment sets instantly.</p>
      </header>

      {/* Toggle */}
      <div className="flex justify-center">
        <div className="inline-flex p-0.5 rounded-lg border border-surface-border bg-surface-secondary shadow-sm">
          <button id="input-method-file-btn" onClick={() => setInputMethod('file')}
            className={cn("flex items-center gap-1.5 px-4 py-1.5 rounded-md text-[13px] font-medium transition-colors",
              inputMethod === 'file' ? "bg-surface text-text-main shadow-card" : "text-text-muted hover:text-text-main"
            )}
          >
            <FileUp className="w-3.5 h-3.5" />Document Source
          </button>
          <button id="input-method-text-btn" onClick={() => setInputMethod('text')}
            className={cn("flex items-center gap-1.5 px-4 py-1.5 rounded-md text-[13px] font-medium transition-colors",
              inputMethod === 'text' ? "bg-surface text-text-main shadow-card" : "text-text-muted hover:text-text-main"
            )}
          >
            <Type className="w-3.5 h-3.5" />Text Input
          </button>
        </div>
      </div>

      {/* Input */}
      <div className="max-w-2xl mx-auto w-full">
        {inputMethod === 'file' ? (
          <div className="card">
            <h3 className="font-semibold text-[11px] uppercase tracking-widest text-primary mb-4 text-center">Upload Document</h3>
            <label id="file-upload-zone" className="group flex flex-col items-center justify-center w-full h-40 border border-dashed border-surface-border-hover rounded-xl hover:border-primary/40 hover:bg-primary-faint transition-colors cursor-pointer bg-surface-secondary">
              <div className="flex flex-col items-center text-center px-4">
                <div className="w-11 h-11 rounded-xl flex items-center justify-center mb-3 bg-primary-faint border border-primary/10 group-hover:scale-105 transition-transform">
                  <Upload className="w-5 h-5 text-text-muted group-hover:text-primary transition-colors" />
                </div>
                <p className="text-[14px] font-medium text-text-secondary group-hover:text-text-main">{fileName || 'Drag & Drop your file here'}</p>
                <p className="text-[11px] text-text-faint mt-1">Supports PDF, DOCX, TXT up to 20MB</p>
              </div>
              <input type="file" className="hidden" onChange={handleFileUpload} accept=".pdf,.docx,.txt" />
            </label>
            {filePath && (
              <div className="mt-3 p-2 rounded-lg flex items-center gap-2 text-[11px] font-semibold justify-center uppercase tracking-wider bg-success-bg border border-success-border text-success-text">
                <FileText className="w-3.5 h-3.5" />File Ready
              </div>
            )}
          </div>
        ) : (
          <div className="card">
            <h3 className="font-semibold text-[11px] uppercase tracking-widest text-primary mb-4 text-center">Manual Entry</h3>
            <textarea id="text-input-area" placeholder="Paste your study material, lecture notes, or key concepts here..."
              className="input min-h-[180px] text-[14px] resize-none p-4 leading-relaxed border-dashed shadow-inner"
              value={rawText} onChange={(e) => setRawText(e.target.value)}
            />
            <div className="mt-2 flex justify-end">
              <span className="text-[10px] text-text-muted font-medium">{rawText.length} characters</span>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="flex items-center gap-2 p-3 rounded-lg text-[13px] font-medium max-w-2xl mx-auto animate-slide-up bg-danger-bg border border-danger-border text-danger-text">
          <AlertCircle className="w-4 h-4 shrink-0" />{error}
        </div>
      )}

      {/* Results */}
      <div>
        {loading ? (
          <div className="flex flex-col items-center justify-center h-48 space-y-4">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
            <div className="text-center">
              <p className="text-[14px] font-semibold text-text-main">Processing...</p>
              <p className="text-[13px] text-text-muted mt-0.5">Analyzing context and generating questions</p>
            </div>
          </div>
        ) : questions.length > 0 ? (
          <div className="space-y-4">
            <div className="flex items-center gap-2.5 pb-3 border-b border-surface-border">
              <div className="w-7 h-7 rounded-md flex items-center justify-center text-[11px] text-white font-bold bg-primary shadow-sm">{questions.length}</div>
              <h3 className="font-semibold text-[15px] text-text-main">Generated Results</h3>
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
            <h4 className="text-lg font-semibold text-text-main">Awaiting Input</h4>
            <p className="text-text-muted max-w-sm mt-1.5 text-center text-[13px]">Choose an input method and configure settings to start generating.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default GeneratePage;
