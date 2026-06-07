import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { useApp } from '../context/AppContext';

const CFG = {
  success: { bg:'bg-white dark:bg-emerald-950/95 border-emerald-200 dark:border-emerald-700/50', text:'text-emerald-700 dark:text-emerald-300', msgText:'text-emerald-900 dark:text-white', icon:'check_circle', bar:'bg-emerald-500' },
  error:   { bg:'bg-white dark:bg-red-950/95 border-red-200 dark:border-red-700/50',             text:'text-red-600 dark:text-red-300',         msgText:'text-red-900 dark:text-white',     icon:'error',        bar:'bg-red-500'     },
  warning: { bg:'bg-white dark:bg-amber-950/95 border-amber-200 dark:border-amber-700/50',       text:'text-amber-600 dark:text-amber-300',     msgText:'text-amber-900 dark:text-white',   icon:'warning',      bar:'bg-amber-400'   },
  info:    { bg:'bg-white dark:bg-zinc-900/95 border-zinc-200 dark:border-zinc-700/50',           text:'text-accent-gold dark:text-zinc-300',    msgText:'text-zinc-800 dark:text-white',    icon:'info',         bar:'bg-accent-gold' },
} as const;

function ToastItem({ id, message, type }: { id:string; message:string; type:keyof typeof CFG }) {
  const { removeToast } = useApp();
  const c = CFG[type];
  useEffect(() => { const t = setTimeout(() => removeToast(id), 4500); return () => clearTimeout(t); }, [id, removeToast]);

  return (
    <motion.div
      layout
      initial={{ opacity:0, x:60, scale:0.9 }}
      animate={{ opacity:1, x:0, scale:1 }}
      exit={{ opacity:0, x:60, scale:0.9, transition:{ duration:0.2 } }}
      transition={{ type:'spring', stiffness:300, damping:24 }}
      className={`relative flex items-center gap-3 pl-4 pr-3 py-3 rounded-2xl border backdrop-blur-xl overflow-hidden max-w-[340px] w-full shadow-xl ${c.bg}`}
      role="alert"
    >
      {/* Progress bar */}
      <motion.div
        className={`absolute bottom-0 left-0 h-[2px] ${c.bar}`}
        initial={{ width:'100%' }} animate={{ width:'0%' }}
        transition={{ duration:4.2, ease:'linear' }}
      />
      <span className={`material-symbols-outlined text-[18px] shrink-0 ${c.text}`} style={{ fontVariationSettings:"'FILL' 1" }}>{c.icon}</span>
      <span className={`flex-1 text-xs font-medium leading-relaxed ${c.msgText}`}>{message}</span>
      <button onClick={() => removeToast(id)} className="text-slate-400 dark:text-white/40 hover:text-primary dark:hover:text-white transition-colors cursor-pointer shrink-0 ml-1">
        <span className="material-symbols-outlined text-[14px]">close</span>
      </button>
    </motion.div>
  );
}

export default function ToastStack() {
  const { toasts } = useApp();
  return (
    <div className="fixed top-5 right-5 z-[9999] flex flex-col gap-2 pointer-events-none">
      <AnimatePresence mode="popLayout">
        {toasts.map(t => (
          <div key={t.id} className="pointer-events-auto">
            <ToastItem {...t} />
          </div>
        ))}
      </AnimatePresence>
    </div>
  );
}
