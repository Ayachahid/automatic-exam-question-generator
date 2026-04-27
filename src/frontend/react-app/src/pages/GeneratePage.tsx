import React, { useState } from 'react';
import { Upload, FileText, Loader2, AlertCircle, Type, FileUp, Sparkles, Database, Search } from 'lucide-react';
import { uploadFile } from '../lib/api';
import QuestionCard from '../components/QuestionCard';
import type { Question } from '../components/QuestionCard';
import { cn } from '../lib/utils';

interface GeneratePageProps {
  onGenerate: () => void;
  questions: Question[];
  loading: boolean;
  error: string | null;
  filePath: string | null;
  setFilePath: (path: string | null) => void;
  rawText: string;
  setRawText: (text: string) => void;
  kbQuery: string;
  setKbQuery: (query: string) => void;
  inputMethod: 'file' | 'text' | 'kb';
  setInputMethod: (val: 'file' | 'text' | 'kb') => void;
}

const GeneratePage: React.FC<GeneratePageProps> = ({
  onGenerate, questions, loading, error, filePath, setFilePath, rawText, setRawText, kbQuery, setKbQuery, inputMethod, setInputMethod
}) => {
  const [fileName, setFileName] = useState<string | null>(null);
  
  const [exportName, setExportName] = useState('exam_questions');
  const [exportFormat, setExportFormat] = useState('pdf');
  const [exporting, setExporting] = useState(false);

  const handleExport = async () => {
    setExporting(true);
    try {
      const { exportQuestions } = await import('../lib/api');
      const blob = await exportQuestions({ questions, format: exportFormat, filename: exportName || 'exam_questions' });
      const url = window.URL.createObjectURL(new Blob([blob]));
      const a = document.createElement('a'); a.href = url; a.download = `${exportName || 'exam_questions'}.${exportFormat}`; a.click();
    } catch (e) {
      console.error('Export failed', e);
    } finally {
      setExporting(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFileName(selectedFile.name);
      try { const data = await uploadFile(selectedFile); setFilePath(data.file_path); } catch { console.error('Failed to upload file'); }
    }
  };

  return (
    <div className="space-y-6 p-6 lg:p-8 max-w-4xl mx-auto w-full">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold tracking-tight text-text-main">Generation</h2>
        
        {/* Toggle */}
        <div className="inline-flex p-0.5 rounded-lg border border-surface-border bg-surface-secondary shadow-sm">
          <button id="input-method-file-btn" onClick={() => setInputMethod('file')}
            className={cn("flex items-center gap-1.5 px-3 py-1 rounded-md text-[12px] font-medium transition-colors",
              inputMethod === 'file' ? "bg-surface text-text-main shadow-card" : "text-text-muted hover:text-text-main"
            )}
          >
            <FileUp className="w-3.5 h-3.5" />Document
          </button>
          <button id="input-method-text-btn" onClick={() => setInputMethod('text')}
            className={cn("flex items-center gap-1.5 px-3 py-1 rounded-md text-[12px] font-medium transition-colors",
              inputMethod === 'text' ? "bg-surface text-text-main shadow-card" : "text-text-muted hover:text-text-main"
            )}
          >
            <Type className="w-3.5 h-3.5" />Text
          </button>
          <button id="input-method-kb-btn" onClick={() => setInputMethod('kb')}
            className={cn("flex items-center gap-1.5 px-3 py-1 rounded-md text-[12px] font-medium transition-colors",
              inputMethod === 'kb' ? "bg-surface text-text-main shadow-card" : "text-text-muted hover:text-text-main"
            )}
          >
            <Database className="w-3.5 h-3.5" />Knowledge Base
          </button>
        </div>
      </div>

      {/* Input */}
      <div className="w-full">
        {inputMethod === 'file' ? (
          <div className="card p-4">
            <label id="file-upload-zone" className="group flex flex-col items-center justify-center w-full h-32 border border-dashed border-surface-border-hover rounded-xl hover:border-primary/40 hover:bg-primary-faint transition-colors cursor-pointer bg-surface-secondary">
              <div className="flex flex-col items-center text-center px-4">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-2 bg-primary-faint border border-primary/10 group-hover:scale-105 transition-transform">
                  <Upload className="w-4 h-4 text-text-muted group-hover:text-primary transition-colors" />
                </div>
                <p className="text-[13px] font-medium text-text-secondary group-hover:text-text-main">{fileName || 'Choose a file to upload'}</p>
              </div>
              <input type="file" className="hidden" onChange={handleFileUpload} accept=".pdf,.docx,.txt" />
            </label>
            {filePath && (
              <div className="mt-3 p-2 rounded-lg flex items-center gap-2 text-[11px] font-semibold justify-center uppercase tracking-wider bg-success-bg border border-success-border text-success-text">
                <FileText className="w-3.5 h-3.5" />Ready
              </div>
            )}
          </div>
        ) : inputMethod === 'text' ? (
          <div className="card p-0 overflow-hidden">
            <textarea id="text-input-area" placeholder="Paste material here..."
              className="w-full min-h-[160px] text-[14px] resize-none p-4 leading-relaxed outline-none bg-surface"
              value={rawText} onChange={(e) => setRawText(e.target.value)}
            />
          </div>
        ) : (
          <div className="card p-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-faint" />
              <input id="kb-search-input" type="text" placeholder="Search knowledge base topics..."
                className="input pl-9 h-11 text-[14px] font-medium w-full shadow-sm" value={kbQuery} onChange={(e) => setKbQuery(e.target.value)}
              />
            </div>
            <p className="text-[12px] text-text-muted mt-3 ml-1">
              The system will search your uploaded documents to create questions.
            </p>
          </div>
        )}
      </div>

      {error && (
        <div className="flex items-center gap-2 p-3 rounded-lg text-[13px] font-medium animate-slide-up bg-danger-bg border border-danger-border text-danger-text pb-4">
          <AlertCircle className="w-4 h-4 shrink-0" />{error}
        </div>
      )}

      {/* Action */}
      <div className="flex justify-end pt-2">
        <button 
          onClick={onGenerate} 
          disabled={loading || 
            (inputMethod !== 'kb' && !filePath && !rawText.trim()) ||
            (inputMethod === 'kb' && !kbQuery.trim())
          }
          className="btn-primary flex items-center justify-center gap-2 text-[14px] h-10 px-6 shadow-sm w-full sm:w-auto"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
          <span className="font-semibold">Generate Questions</span>
        </button>
      </div>

      {/* Results */}
      <div>
        {loading ? (
          <div className="flex flex-col items-center justify-center h-40 space-y-3">
            <Loader2 className="w-6 h-6 animate-spin text-primary" />
            <p className="text-[13px] font-medium text-text-main">Generating...</p>
          </div>
        ) : questions.length > 0 ? (
          <div className="space-y-4">
            <div className="flex items-center gap-2.5 pb-2 border-b border-surface-border">
              <div className="w-6 h-6 rounded flex items-center justify-center text-[10px] text-white font-bold bg-primary shadow-sm">{questions.length}</div>
              <h3 className="font-semibold text-[14px] text-text-main">Results</h3>
            </div>
            <div className="grid grid-cols-1 gap-3">
              {questions.map((q, i) => <QuestionCard key={i} question={q} index={i + 1} />)}
            </div>
            
            {/* Export Actions */}
            <div className="mt-8 pt-6 border-t border-surface-border animate-fade-in flex flex-col sm:flex-row items-end gap-3 bg-surface-secondary p-4 rounded-xl border">
              <div className="flex-1 w-full space-y-1.5">
                <label className="text-[11px] font-semibold text-text-secondary uppercase tracking-wide">Filename</label>
                <input 
                  type="text" 
                  id="export-filename"
                  className="input h-9 text-[13px] w-full" 
                  value={exportName} 
                  onChange={(e) => setExportName(e.target.value)}
                  placeholder="exam_questions"
                />
              </div>
              
              <div className="w-full sm:w-32 space-y-1.5">
                <label className="text-[11px] font-semibold text-text-secondary uppercase tracking-wide">Format</label>
                <select 
                  id="export-format"
                  className="input h-9 text-[13px] w-full"
                  value={exportFormat}
                  onChange={(e) => setExportFormat(e.target.value)}
                >
                  <option value="pdf">PDF</option>
                  <option value="txt">TXT</option>
                  <option value="json">JSON</option>
                </select>
              </div>

              <button 
                onClick={handleExport}
                disabled={exporting}
                className="btn-primary h-9 px-6 flex items-center justify-center gap-2 text-[13px] w-full sm:w-auto shadow-sm shrink-0"
              >
                {exporting ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileUp className="w-4 h-4" />}
                <span className="font-semibold">Export File</span>
              </button>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-10">
            <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-3 bg-surface-secondary border border-surface-border animate-float">
              <Sparkles className="w-5 h-5 text-text-faint" />
            </div>
            <p className="text-text-muted text-[13px]">Ready to generate</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default GeneratePage;
