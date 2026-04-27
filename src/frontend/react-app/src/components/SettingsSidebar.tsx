import React from 'react';
import { 
  Settings2, 
  HelpCircle,
} from 'lucide-react';
import { cn } from '../lib/utils';
import type { TabType } from '../App';

interface SettingsSidebarProps {
  type: string;
  setType: (val: string) => void;
  difficulty: string;
  setDifficulty: (val: string) => void;
  count: number;
  setCount: (val: number) => void;
  isOpen: boolean;
  currentTab: TabType;
}

const SettingsSidebar: React.FC<SettingsSidebarProps> = ({ 
  type, setType, 
  difficulty, setDifficulty, 
  count, setCount, 
  isOpen,
  currentTab,
}) => {
  if (!isOpen) return null;

  return (
    <aside className="w-64 shrink-0 border-r border-surface-border bg-surface h-[calc(100vh-3rem)] flex flex-col sticky top-12 overflow-y-auto">
      {/* Header */}
      <div className="px-4 py-3 border-b border-surface-border flex items-center gap-2">
        <Settings2 className="text-text-muted w-4 h-4" />
        <h2 className="font-semibold text-[13px] text-text-main">
          Configuration
        </h2>
      </div>

      {/* Settings */}
      <div className="p-4 space-y-5 flex-1">
        <label className="text-[10px] font-semibold text-text-muted uppercase tracking-[0.12em]">Settings</label>
        
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <label className="text-[11px] font-semibold text-text-secondary uppercase tracking-wide">Type</label>
            <HelpCircle className="w-3 h-3 text-text-faint cursor-help" />
          </div>
          <select id="question-type-select" className="input text-[13px] h-9" value={type} onChange={(e) => setType(e.target.value)}>
            <option value="multiple_choice">Multiple Choice</option>
            <option value="true_false">True / False</option>
            {currentTab !== 'exam' && (
              <>
                <option value="short_answer">Short Answer</option>
                <option value="essay">Essay</option>
                <option value="scenario_based">Scenario Based</option>
              </>
            )}
          </select>
        </div>

        <div className="space-y-1.5">
          <label className="text-[11px] font-semibold text-text-secondary uppercase tracking-wide">Difficulty</label>
          <div className="grid grid-cols-3 gap-1.5">
            {(['easy', 'medium', 'hard'] as const).map((d) => (
              <button key={d} id={`difficulty-${d}-btn`} onClick={() => setDifficulty(d)}
                className={cn(
                  "py-1.5 text-[11px] rounded-md border transition-colors font-medium capitalize",
                  difficulty === d
                    ? "bg-primary-faint text-primary border-primary/25"
                    : "border-surface-border text-text-muted hover:text-text-secondary hover:bg-surface-secondary"
                )}
              >
                {d}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-[11px] font-semibold text-text-secondary uppercase tracking-wide">Count</label>
            <span className="text-[12px] font-bold text-primary">{count}</span>
          </div>
          <input id="question-count-slider" type="range" min="1" max="50" value={count} onChange={(e) => setCount(parseInt(e.target.value))} />
        </div>
      </div>

      <div className="px-4 py-2.5 border-t border-surface-border">
        <p className="text-[10px] text-text-faint text-center">Powered by Ollama</p>
      </div>
    </aside>
  );
};

export default SettingsSidebar;
