import React from 'react';
import { 
  CheckCircle2, 
  ChevronDown, 
  ChevronUp,
  Tag,
  XCircle
} from 'lucide-react';
import { cn } from '../lib/utils';

export interface Question {
  question: string;
  answer: string;
  explanation?: string;
  options?: string[];
  scenario?: string;
  concepts_tested?: string[];
  question_type?: string;
}

interface QuestionCardProps {
  question: Question;
  index: number;
}

const QuestionCard: React.FC<QuestionCardProps> = ({ question, index }) => {
  const [showAnswer, setShowAnswer] = React.useState(false);
  const [selectedAnswer, setSelectedAnswer] = React.useState<string | null>(null);
  const [isCorrect, setIsCorrect] = React.useState<boolean | null>(null);

  React.useEffect(() => {
    setShowAnswer(false);
    setSelectedAnswer(null);
    setIsCorrect(null);
  }, [question]);

  const normalizedTargetAnswer = (question.answer || '').toString().toLowerCase().trim();
  const qText = question.question.toLowerCase();
  
  // Broader check for True/False questions when options aren't explicitly provided
  const isTrueFalse = question.question_type === 'true_false' || (
    (!question.options || question.options.length === 0) && (
      ['true', 'false', 't', 'f', '1', '0'].includes(normalizedTargetAnswer) ||
      normalizedTargetAnswer.startsWith('true') ||
      normalizedTargetAnswer.startsWith('false') ||
      qText.includes('true or false') ||
      qText.includes('true/false') ||
      (normalizedTargetAnswer.length < 20 && (normalizedTargetAnswer.includes('true') || normalizedTargetAnswer.includes('false')))
    )
  );

  const displayOptions = (question.options && question.options.length > 0) ? question.options : (isTrueFalse ? ['True', 'False'] : undefined);

  let displayAnswer = question.answer;
  if (isTrueFalse) {
    const isTargetTrue = normalizedTargetAnswer.includes('true') || normalizedTargetAnswer === 't' || normalizedTargetAnswer === '1';
    const isTargetFalse = normalizedTargetAnswer.includes('false') || normalizedTargetAnswer === 'f' || normalizedTargetAnswer === '0';
    if (isTargetTrue && !isTargetFalse) displayAnswer = "True";
    else if (isTargetFalse && !isTargetTrue) displayAnswer = "False";
  }

  const handleSelectOption = (idx: number, optionText: string) => {
    setSelectedAnswer(optionText);

    const rawAns = (question.answer || '').toString().trim().toLowerCase();
    const userChoice = optionText.trim().toLowerCase();

    let isMatch = false;
    
    if (isTrueFalse) {
      // 1. T/F Logic from Python
      let correctAnswerStr = rawAns;
      
      if (['true', '1', 't', 'yes'].includes(rawAns)) {
        correctAnswerStr = 'true';
      } else if (['false', '0', 'f', 'no'].includes(rawAns)) {
        correctAnswerStr = 'false';
      } else {
        // Broad capture
        if (rawAns.startsWith('true') || rawAns.includes('true')) correctAnswerStr = 'true';
        else if (rawAns.startsWith('false') || rawAns.includes('false')) correctAnswerStr = 'false';
      }

      // User choice boolean extractor
      let resolvedUserChoice = userChoice;
      if (userChoice.includes('true') || userChoice === 't') resolvedUserChoice = 'true';
      else if (userChoice.includes('false') || userChoice === 'f') resolvedUserChoice = 'false';

      isMatch = resolvedUserChoice === correctAnswerStr;
      
    } else {
      // 2. MCQ Logic from Python
      const answerRawUpper = (question.answer || '').toString().trim().toUpperCase();
      let cleanAnswer = '';
      
      // Parse out A/B/C/D if short
      if (answerRawUpper.length <= 3) {
        cleanAnswer = answerRawUpper.replace(/[^A-D]/g, '');
      }

      const optionsList = question.options || [];
      let correctTextLower = rawAns;
      let usedLetterMatch = false;
      
      if (cleanAnswer.length === 1 && "ABCD".includes(cleanAnswer)) {
        const charCode = cleanAnswer.charCodeAt(0) - 65; // A=0
        if (charCode >= 0 && charCode < optionsList.length) {
          correctTextLower = optionsList[charCode].trim().toLowerCase();
          usedLetterMatch = true;
        }
      }

      isMatch = userChoice === correctTextLower;

      // Ultimate semantic fallback (ONLY if it wasn't a strict A/B/C/D letter intent)
      if (!isMatch && !usedLetterMatch && rawAns.length > 1) {
         isMatch = rawAns === userChoice || rawAns.includes(userChoice) || userChoice.includes(rawAns);
      }
    }

    setIsCorrect(isMatch);
    setShowAnswer(true);
  };

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

            {displayOptions && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
                {displayOptions.map((option, idx) => {
                  const letter = isTrueFalse ? null : String.fromCharCode(65 + idx);
                  const isSelected = selectedAnswer === option;
                  
                  let optionClass = "flex items-center gap-2.5 p-2.5 rounded-lg border transition-colors cursor-pointer text-left focus:outline-none ";
                  if (isSelected) {
                     if (isCorrect) {
                        optionClass += "border-success bg-success-bg";
                     } else {
                        optionClass += "border-danger bg-danger-bg";
                     }
                  } else if (selectedAnswer && !isSelected && isCorrect === false) {
                     optionClass += "border-surface-border bg-surface-secondary opacity-50";
                  } else {
                     optionClass += "border-surface-border bg-surface-secondary hover:border-primary/40 hover:bg-primary-faint";
                  }

                  return (
                    <button 
                      key={idx} 
                      onClick={() => handleSelectOption(idx, option)}
                      className={optionClass}
                    >
                      {!isTrueFalse && (
                        <div className={cn("shrink-0 w-6 h-6 rounded flex items-center justify-center text-[11px] font-bold border transition-colors",
                          isSelected && isCorrect ? "bg-success text-white border-success" :
                          isSelected && !isCorrect ? "bg-danger text-white border-danger" :
                          "text-primary bg-primary-faint border-primary/15"
                        )}>
                          {letter}
                        </div>
                      )}
                      <span className={cn("text-[13px] leading-snug", isSelected ? "text-text-main font-semibold" : "text-text-secondary")}>
                        {option}
                      </span>
                    </button>
                  );
                })}
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
            {showAnswer ? 'Hide Answer Details' : 'Reveal Answer Details'}
          </button>

          <div className={cn(
            "transition-all duration-300 overflow-hidden",
            showAnswer ? "max-h-[600px] opacity-100 mt-3" : "max-h-0 opacity-0"
          )}>
            <div className={cn(
              "p-3.5 rounded-lg border",
              isCorrect === true ? "bg-success-bg border-success-border text-success-text" :
              isCorrect === false ? "bg-danger-bg border-danger-border text-danger-text" :
              "bg-surface-secondary border-surface-border text-text-main"
            )}>
              <div className={cn("flex items-center gap-1.5 mb-1.5")}>
                {isCorrect === true && <CheckCircle2 className="w-4 h-4" />}
                {isCorrect === false && <XCircle className="w-4 h-4" />}
                {isCorrect === null && <CheckCircle2 className="w-4 h-4 text-success" />}
                <span className="font-semibold text-[13px]">
                   {isCorrect === true ? "Correct!" : 
                    isCorrect === false ? "Incorrect" : 
                    "Answer"}
                </span>
              </div>
              <p className="text-[13px] whitespace-pre-wrap leading-relaxed opacity-90">
                {isCorrect === false && <span className="font-medium mr-1.5">Correct Answer is:</span>}
                {displayAnswer}
              </p>
              {question.explanation && (
                <div className="mt-3 pt-3 border-t border-current/20">
                  <p className="text-[10px] font-semibold uppercase tracking-wider mb-1">Explanation</p>
                  <p className="text-[13px] leading-relaxed opacity-90">{question.explanation}</p>
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
