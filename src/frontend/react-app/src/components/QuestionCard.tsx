import React from 'react';
import { 
  CheckCircle2, 
  ChevronDown, 
  ChevronUp,
  Tag
} from 'lucide-react';
import { cn } from '../lib/utils';

export interface Question {
  question: string;
  answer: string;
  explanation?: string;
  options?: string[];
  scenario?: string;
  concepts_tested?: string[];
}

interface QuestionCardProps {
  question: Question;
  index: number;
}

const QuestionCard: React.FC<QuestionCardProps> = ({ question, index }) => {
  const [showAnswer, setShowAnswer] = React.useState(false);

  return (
    <div 
      className="bg-surface rounded-xl border border-surface-border shadow-card overflow-hidden animate-slide-up"
      style={{ animationDelay: `${index * 60}ms`, animationFillMode: 'both' }}
    >
      {/* Top accent */}
      <div className="h-[2px]" style={{ background: 'linear-gradient(90deg, #D97757, #E8A48E)' }} />
      
      <div className="p-5 space-y-3">
        <div className="flex items-start gap-3">
          <div className="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs text-white bg-primary shadow-sm">
            {index}
          </div>
          <div className="flex-1 space-y-3 min-w-0">
            <h3 className="text-[15px] font-medium leading-relaxed text-text-main">
              {question.question}
            </h3>
            
            {question.scenario && (
              <div className="p-3 rounded-lg text-[13px] text-text-muted leading-relaxed bg-surface-secondary border border-surface-border italic">
                {question.scenario}
              </div>
            )}

            {question.options && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
                {question.options.map((option, idx) => (
                  <div key={idx} className="flex items-center gap-2.5 p-2.5 rounded-lg border border-surface-border bg-surface-secondary hover:border-primary/30 hover:bg-primary-faint transition-colors cursor-default">
                    <div className="w-6 h-6 rounded flex items-center justify-center text-[11px] font-bold text-primary bg-primary-faint border border-primary/15">
                      {String.fromCharCode(65 + idx)}
                    </div>
                    <span className="text-[13px] text-text-secondary">{option}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {question.concepts_tested && question.concepts_tested.length > 0 && (
          <div className="flex flex-wrap gap-1.5 pl-11">
            {question.concepts_tested.map((concept, idx) => (
              <span key={idx} className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider text-accent-blue bg-accent-blue/8 border border-accent-blue/15">
                <Tag className="w-2.5 h-2.5" />
                {concept}
              </span>
            ))}
          </div>
        )}

        <div className="pt-3 border-t border-surface-border ml-11">
          <button onClick={() => setShowAnswer(!showAnswer)}
            className="flex items-center gap-1.5 text-[13px] font-medium text-primary hover:text-primary-hover transition-colors"
          >
            {showAnswer ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            {showAnswer ? 'Hide Answer' : 'Reveal Answer'}
          </button>

          <div className={cn(
            "transition-all duration-300 overflow-hidden",
            showAnswer ? "max-h-[600px] opacity-100 mt-3" : "max-h-0 opacity-0"
          )}>
            <div className="p-3.5 rounded-lg bg-success-bg border border-success-border">
              <div className="flex items-center gap-1.5 mb-1.5 text-success-text">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span className="font-semibold text-[12px]">Correct Answer</span>
              </div>
              <p className="text-[13px] whitespace-pre-wrap text-success-text leading-relaxed">
                {question.answer}
              </p>
              {question.explanation && (
                <div className="mt-3 pt-3 border-t border-success-border">
                  <p className="text-[10px] font-semibold uppercase tracking-wider mb-1 text-success-text">Explanation</p>
                  <p className="text-[13px] text-success-text/80 leading-relaxed">{question.explanation}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuestionCard;
