import React, { useState } from 'react';
import { Upload, FileText, Loader2, AlertCircle, Type, FileUp, Sparkles, GraduationCap, CheckCircle2, RotateCcw, Database, Search, XCircle } from 'lucide-react';
import { uploadFile, generateQuestions, generateRAGQuestions } from '../lib/api';
import QuestionCard from '../components/QuestionCard';
import type { Question } from '../components/QuestionCard';
import { cn } from '../lib/utils';

interface ExamModePageProps {
  type: string;
  difficulty: string;
  count: number;
}

type InputMethod = 'file' | 'text' | 'kb';
type ExamState = 'setup' | 'generating' | 'taking' | 'review';

const ExamModePage: React.FC<ExamModePageProps> = ({ type, difficulty, count }) => {
  const [examState, setExamState] = useState<ExamState>('setup');
  
  const [inputMethod, setInputMethod] = useState<InputMethod>('file');
  const [fileName, setFileName] = useState<string | null>(null);
  const [filePath, setFilePath] = useState<string | null>(null);
  const [rawText, setRawText] = useState('');
  const [kbQuery, setKbQuery] = useState('');
  
  const [questions, setQuestions] = useState<Question[]>([]);
  const [error, setError] = useState<string | null>(null);

  type AnswerRecord = { isCorrect: boolean; selectedText: string };
  const [answers, setAnswers] = useState<Record<number, AnswerRecord>>({});

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFileName(selectedFile.name);
      try {
        const data = await uploadFile(selectedFile);
        setFilePath(data.file_path);
      } catch {
        console.error('Failed to upload file');
      }
    }
  };

  const handleStartExam = async () => {
    if (inputMethod === 'file' || inputMethod === 'text') {
      if (!filePath && !rawText.trim()) {
        setError('Please upload a file or paste text first.');
        return;
      }
    } else if (inputMethod === 'kb') {
      if (!kbQuery.trim()) {
        setError('Please enter a subject or topic for the Knowledge Base.');
        return;
      }
    }
    
    setExamState('generating');
    setError(null);
    setAnswers({});
    
    try {
      let data;
      if (inputMethod === 'kb') {
        const payload = { 
          query: kbQuery.trim(), 
          question_type: type, 
          difficulty, 
          num_questions: count, 
          n_results: 3 
        };
        data = await generateRAGQuestions(payload);
      } else {
        const payload = { 
          question_type: type, 
          difficulty, 
          num_questions: count, 
          file_path: filePath, 
          text: rawText.trim() || undefined 
        };
        data = await generateQuestions(payload);
      }
      const mappedQuestions = data.questions.map((q: any) => ({ ...q, question_type: type }));
      
      setQuestions(mappedQuestions);
      setExamState('taking');
    } catch {
      setError('Generation failed. Ensure backend is running.');
      setExamState('setup');
    }
  };

  const handleSubmitExam = () => {
    setExamState('review');
  };

  const handleReset = () => {
    setExamState('setup');
    setQuestions([]);
    setAnswers({});
  };

  const handleSelectionChange = (index: number, isCorrect: boolean, selectedText: string) => {
    setAnswers((prev) => ({ ...prev, [index]: { isCorrect, selectedText } }));
  };

  const correctAnswersCount = Object.values(answers).filter(a => a.isCorrect).length;
  const scorePercentage = questions.length > 0 ? Math.round((correctAnswersCount / questions.length) * 100) : 0;

  const getDisplayAnswer = (q: Question) => {
    const rawAnswer = (q.answer || '').toString().trim();
    if (!q.options || q.options.length === 0) {
      const lower = rawAnswer.toLowerCase();
      if (lower === 't' || lower === '1') return 'True';
      if (lower === 'f' || lower === '0') return 'False';
      return rawAnswer;
    }

    const answerRawUpper = rawAnswer.toUpperCase();
    let cleanAnswer = '';
    if (answerRawUpper.length <= 3) {
      cleanAnswer = answerRawUpper.replace(/[^A-D]/g, '');
    }

    if (cleanAnswer.length === 1 && "ABCD".includes(cleanAnswer)) {
      const charCode = cleanAnswer.charCodeAt(0) - 65;
      if (charCode >= 0 && charCode < q.options.length) {
        return `${cleanAnswer}. ${q.options[charCode]}`;
      }
    }
    return rawAnswer;
  };

  return (
    <div className="space-y-6 p-6 lg:p-8 max-w-4xl mx-auto w-full">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold tracking-tight text-text-main flex items-center gap-2">
          <GraduationCap className="w-5 h-5 text-primary" />
          Exam Mode
        </h2>
        
        {examState === 'setup' && (
          <div className="inline-flex p-0.5 rounded-lg border border-surface-border bg-surface-secondary shadow-sm">
            <button id="exam-input-method-file" onClick={() => setInputMethod('file')}
              className={cn("flex items-center gap-1.5 px-3 py-1 rounded-md text-[12px] font-medium transition-colors",
                inputMethod === 'file' ? "bg-surface text-text-main shadow-card" : "text-text-muted hover:text-text-main"
              )}
            >
              <FileUp className="w-3.5 h-3.5" />Document
            </button>
            <button id="exam-input-method-text" onClick={() => setInputMethod('text')}
              className={cn("flex items-center gap-1.5 px-3 py-1 rounded-md text-[12px] font-medium transition-colors",
                inputMethod === 'text' ? "bg-surface text-text-main shadow-card" : "text-text-muted hover:text-text-main"
              )}
            >
              <Type className="w-3.5 h-3.5" />Text
            </button>
            <button id="exam-input-method-kb" onClick={() => setInputMethod('kb')}
              className={cn("flex items-center gap-1.5 px-3 py-1 rounded-md text-[12px] font-medium transition-colors",
                inputMethod === 'kb' ? "bg-surface text-text-main shadow-card" : "text-text-muted hover:text-text-main"
              )}
            >
              <Database className="w-3.5 h-3.5" />Knowledge Base
            </button>
          </div>
        )}
      </div>

      {examState === 'setup' && (
        <>
          <div className="w-full">
            {inputMethod === 'file' ? (
              <div className="card p-4">
                <label className="group flex flex-col items-center justify-center w-full h-32 border border-dashed border-surface-border-hover rounded-xl hover:border-primary/40 hover:bg-primary-faint transition-colors cursor-pointer bg-surface-secondary">
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
                <textarea placeholder="Paste material here..."
                  className="w-full min-h-[160px] text-[14px] resize-none p-4 leading-relaxed outline-none bg-surface"
                  value={rawText} onChange={(e) => setRawText(e.target.value)}
                />
              </div>
            ) : (
              <div className="card p-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-faint" />
                  <input id="exam-kb-search-input" type="text" placeholder="Search knowledge base topics..."
                    className="input pl-9 h-11 text-[14px] font-medium w-full shadow-sm" value={kbQuery} onChange={(e) => setKbQuery(e.target.value)}
                  />
                </div>
                <p className="text-[12px] text-text-muted mt-3 ml-1">
                  The system will search your uploaded documents to create this exam.
                </p>
              </div>
            )}
          </div>

          {error && (
            <div className="flex items-center gap-2 p-3 rounded-lg text-[13px] font-medium animate-slide-up bg-danger-bg border border-danger-border text-danger-text pb-4">
              <AlertCircle className="w-4 h-4 shrink-0" />{error}
            </div>
          )}

          <div className="flex justify-end pt-2">
            <button 
              onClick={handleStartExam} 
              disabled={
                (inputMethod !== 'kb' && !filePath && !rawText.trim()) ||
                (inputMethod === 'kb' && !kbQuery.trim())
              }
              className="btn-primary flex items-center justify-center gap-2 text-[14px] h-10 px-6 shadow-sm w-full sm:w-auto"
            >
              <Sparkles className="w-4 h-4" />
              <span className="font-semibold">Generate & Start Exam</span>
            </button>
          </div>
        </>
      )}

      {examState === 'generating' && (
        <div className="flex flex-col items-center justify-center py-20 space-y-4">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
          <p className="text-[14px] font-medium text-text-main">Preparing your exam...</p>
          <p className="text-[12px] text-text-muted">Analyzing context and formulating concepts.</p>
        </div>
      )}

      {examState === 'taking' && questions.length > 0 && (
        <div className="space-y-6">
          <div className="flex items-center gap-2.5 pb-2 border-b border-surface-border">
            <div className="w-6 h-6 rounded flex items-center justify-center text-[10px] text-white font-bold bg-primary shadow-sm">{questions.length}</div>
            <h3 className="font-semibold text-[14px] text-text-main">Answer all questions below</h3>
          </div>

          <div className="grid grid-cols-1 gap-4">
            {questions.map((q, i) => (
              <QuestionCard 
                key={i} 
                question={q} 
                index={i + 1} 
                isExamMode={true}
                forceShowResult={false}
                onSelectionChange={handleSelectionChange}
              />
            ))}
          </div>

          <div className="sticky bottom-4 z-40 bg-surface/80 backdrop-blur-md p-4 rounded-xl border border-surface-border shadow-card flex items-center justify-between animate-fade-in">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
              <span className="text-[13px] font-semibold text-text-secondary">Exam in progress</span>
            </div>
            <button 
              onClick={handleSubmitExam}
              className="btn-primary h-10 px-8 flex items-center justify-center gap-2 text-[14px] shadow-md hover:shadow-lg transition-all"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span className="font-semibold">Submit Exam</span>
            </button>
          </div>
        </div>
      )}

      {examState === 'review' && questions.length > 0 && (
        <div className="space-y-8 animate-fade-in py-4">
          <div className="card p-8 flex flex-col items-center justify-center gap-4 bg-surface text-center">
            <div className={cn("w-20 h-20 rounded-full flex items-center justify-center text-white shadow-md font-bold text-3xl", 
              scorePercentage >= 80 ? "bg-success" : scorePercentage >= 50 ? "bg-warning" : "bg-danger"
            )}>
              {scorePercentage}%
            </div>
            <div>
              <h3 className="text-xl font-bold text-text-main">Evaluation Results</h3>
              <p className="text-[14px] font-medium text-text-secondary mt-1.5">
                You correctly answered <span className={cn("font-bold", scorePercentage >= 50 ? "text-success" : "text-danger")}>{correctAnswersCount}</span> out of {questions.length} questions.
              </p>
            </div>
            <button 
              onClick={handleReset}
              className="btn-primary mt-4 text-[13px] font-semibold h-10 px-6 shadow-sm flex items-center gap-2"
            >
              <RotateCcw className="w-4 h-4" /> Take Another Exam
            </button>
          </div>

          <div className="space-y-4">
            <h3 className="font-bold text-[16px] text-text-main border-b border-surface-border pb-2 mb-4">Question Breakdown</h3>
            {questions.map((q, i) => {
              const userAns = answers[i];
              const isCorrect = userAns?.isCorrect;
              
              return (
                <div key={i} className={cn("card p-5 space-y-3 transition-colors", 
                  isCorrect === true ? "border-success/30 bg-success-bg/20" : 
                  isCorrect === false ? "border-danger/30 bg-danger-bg/20" : 
                  "border-surface-border"
                )}>
                  <div className="flex items-start gap-3">
                    <div className="shrink-0 pt-0.5">
                      {isCorrect === true ? (
                        <CheckCircle2 className="w-5 h-5 text-success" />
                      ) : isCorrect === false ? (
                        <XCircle className="w-5 h-5 text-danger" />
                      ) : (
                        <AlertCircle className="w-5 h-5 text-text-muted" />
                      )}
                    </div>
                    <div className="flex-1 space-y-2.5">
                      <h4 className="text-[15px] font-medium leading-relaxed text-text-main">
                        <span className="font-bold mr-2">{i + 1}.</span>{q.question}
                      </h4>
                      
                      <div className="text-[13px] p-2.5 rounded-lg border bg-surface-secondary">
                        <span className="font-semibold text-text-secondary mr-2">Your Answer:</span>
                        <span className={cn("font-medium", 
                          isCorrect === true ? "text-success" : 
                          isCorrect === false ? "text-danger" : 
                          "text-text-muted italic"
                        )}>
                          {userAns ? userAns.selectedText : "No answer provided"}
                        </span>
                      </div>

                      {isCorrect === false && (
                        <div className="text-[13px] p-2.5 rounded-lg border border-success/30 bg-success-bg">
                           <span className="font-semibold text-success-text mr-2">Correct Answer:</span>
                           <span className="font-medium text-text-main">{getDisplayAnswer(q)}</span>
                        </div>
                      )}

                      {q.explanation && (
                        <div className="mt-3 pt-3 border-t border-surface-border">
                          <p className="text-[10px] font-semibold uppercase tracking-wider mb-1 text-text-muted">Explanation</p>
                          <p className="text-[13px] leading-relaxed text-text-secondary">{q.explanation}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default ExamModePage;
