import React from 'react';
import { Database, Upload, Trash2, X, FileText, Loader2 } from 'lucide-react';

interface DocumentsPageProps {
  kbFiles: string[];
  onIndexFiles: (files: FileList) => void;
  resetKBAction: () => void;
  indexing: boolean;
}

const DocumentsPage: React.FC<DocumentsPageProps> = ({
  kbFiles, onIndexFiles, resetKBAction, indexing
}) => {
  return (
    <div className="p-6 lg:p-8 max-w-4xl mx-auto space-y-6 w-full">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-text-main">Document Library</h2>
        </div>
        
        <div className="flex gap-2">
            <label className="btn-primary flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[12px] h-9 cursor-pointer shadow-sm">
              {indexing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
              <span>Add Documents</span>
              <input type="file" className="hidden" multiple onChange={(e) => e.target.files && onIndexFiles(e.target.files)} />
            </label>
            <button 
              onClick={resetKBAction}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-danger-border bg-danger-bg text-danger-text hover:bg-danger/10 transition-colors text-[12px] font-semibold h-9 shadow-sm"
              title="Clear all documents"
            >
              <Trash2 className="w-4 h-4" />
              <span>Clear All</span>
            </button>
        </div>
      </div>

      <div className="card min-h-[400px]">
         <div className="flex items-center justify-between mb-4 border-b border-surface-border pb-3">
             <h3 className="text-[13px] font-semibold text-text-main">Indexed Files</h3>
             <span className="text-[11px] font-bold text-primary bg-primary-faint px-2 py-0.5 rounded-full">{kbFiles.length} files</span>
         </div>
         {kbFiles.length > 0 ? (
          <div className="space-y-2">
            {kbFiles.map((file, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 rounded-lg border border-surface-border bg-surface-secondary shadow-sm">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-md bg-surface border border-surface-border flex items-center justify-center">
                    <FileText className="w-4 h-4 text-primary" />
                  </div>
                  <span className="text-[13px] text-text-main font-medium">{file}</span>
                </div>
                <button 
                  onClick={() => alert('Individual file deletion coming soon via backend api update')} 
                  className="p-1.5 text-text-muted hover:text-danger hover:bg-danger/10 rounded-md transition-colors"
                  title="Remove file"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
         ) : (
           <div className="flex flex-col items-center justify-center h-[300px] text-center border-dashed border-2 border-surface-border rounded-lg bg-surface">
             <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-3 bg-surface-secondary border border-surface-border">
               <Database className="w-5 h-5 text-text-faint" />
             </div>
             <p className="text-[14px] font-medium text-text-main">No documents indexed</p>
             <p className="text-[12px] text-text-muted mt-1">Upload materials using the button above.</p>
           </div>
         )}
      </div>
    </div>
  );
};

export default DocumentsPage;
