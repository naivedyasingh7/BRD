import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';

interface Props {
  onFileAccepted: (file: File, text: string) => void;
  onError: (msg: string) => void;
}

const ALLOWED = ['mp3', 'wav', 'm4a', 'txt', 'pdf', 'docx'];
const MAX_BYTES = 128 * 1024 * 1024;

export default function UploadZone({ onFileAccepted, onError }: Props) {
  const [dragActive, setDragActive] = useState(false);
  const [progress, setProgress] = useState<number | null>(null);
  const [fileName, setFileName] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const process = (file: File) => {
    const ext = file.name.split('.').pop()?.toLowerCase() ?? '';
    if (!ALLOWED.includes(ext)) { onError(`Unsupported format (.${ext}). Allowed: ${ALLOWED.join(', ').toUpperCase()}`); return; }
    if (file.size > MAX_BYTES) { onError(`File too large (${(file.size / 1024 / 1024).toFixed(1)} MB). Max 128 MB.`); return; }
    setFileName(file.name);
    let p = 0; setProgress(0);
    const iv = setInterval(() => {
      p += 20; setProgress(Math.min(p, 100));
      if (p >= 100) {
        clearInterval(iv);
        setTimeout(() => {
          setProgress(null);
          if (ext === 'txt' || ext === 'pdf' || ext === 'docx') {
            const reader = new FileReader();
            reader.onload = e => onFileAccepted(file, e.target?.result as string);
            reader.readAsText(file);
          } else {
            onFileAccepted(file, '');
          }
        }, 350);
      }
    }, 90);
  };

  const onDrag = (e: React.DragEvent) => {
    e.preventDefault(); e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };
  const onDrop = (e: React.DragEvent) => {
    e.preventDefault(); setDragActive(false);
    if (e.dataTransfer.files[0]) process(e.dataTransfer.files[0]);
  };

  return (
    <div>
      <input ref={inputRef} type="file" className="hidden" accept={ALLOWED.map(e => `.${e}`).join(',')} onChange={e => e.target.files?.[0] && process(e.target.files[0])} />
      <AnimatePresence mode="wait">
        {progress !== null ? (
          <motion.div key="uploading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="border border-accent-gold/30 bg-bg-cream dark:bg-zinc-900/40 p-8 text-center flex flex-col items-center justify-center min-h-[185px] gap-3"
          >
            <span className="material-symbols-outlined text-4xl animate-spin text-accent-gold">sync</span>
            <p className="font-sans font-semibold text-xs text-primary dark:text-white font-bold">Uploading {fileName}…</p>
            <p className="text-[10px] uppercase tracking-widest font-mono text-slate-450 dark:text-zinc-500">Analyzing format &amp; hashes</p>
            <div className="w-full max-w-xs">
              <div className="w-full h-1 bg-black/10 dark:bg-white/10 overflow-hidden">
                <motion.div className="bg-accent-gold h-full" animate={{ width: `${progress}%` }} transition={{ duration: 0.08 }} />
              </div>
              <div className="flex justify-between text-[9px] font-mono text-slate-450 dark:text-zinc-500 mt-1 uppercase tracking-wider font-bold">
                <span>Transmitting</span><span>{progress}%</span>
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onDragEnter={onDrag} onDragOver={onDrag} onDragLeave={onDrag} onDrop={onDrop}
            onClick={() => inputRef.current?.click()}
            className={`relative p-10 text-center flex flex-col items-center justify-center cursor-pointer min-h-[220px] transition-all duration-400 rounded-xl overflow-hidden ${
              dragActive
                ? 'border-2 border-accent-gold bg-accent-gold/5 scale-[1.02] shadow-2xl'
                : 'border border-black/10 dark:border-white/10 bg-surface dark:bg-zinc-900/50 hover:bg-bg-cream dark:hover:bg-zinc-900 hover:border-accent-gold/60 shadow-sm hover:shadow-lg'
            }`}
          >
            <div className="h-12 w-12 bg-surface dark:bg-zinc-900 border border-black/5 dark:border-white/10 flex items-center justify-center mb-4 shadow-sm">
              <span className="material-symbols-outlined text-xl text-accent-gold" style={{ fontVariationSettings: "'FILL' 1" }}>cloud_upload</span>
            </div>
            <h4 className="font-serif font-bold text-sm italic text-primary dark:text-white mb-1">Drag &amp; drop transcripts or recordings</h4>
            <p className="text-[11px] text-slate-655 dark:text-zinc-400 max-w-xs mb-4 leading-relaxed font-sans font-normal">
              Accepts MP3, WAV, M4A, TXT, PDF, DOCX — up to 128 MB
            </p>
            <button type="button" onClick={e => { e.stopPropagation(); inputRef.current?.click(); }}
              className="bg-white dark:bg-zinc-900 border border-black/10 dark:border-white/10 px-4 py-2 text-[10px] font-bold uppercase tracking-widest text-primary dark:text-white hover:bg-bg-cream dark:hover:bg-zinc-800 transition-all shadow-sm"
            >
              Browse local documents
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
