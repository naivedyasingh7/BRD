import React, { useState } from 'react';
import { motion } from 'motion/react';
import Navbar from '../components/Navbar';
import ShowcaseCarousel from '../components/ShowcaseCarousel';
import { useApp } from '../context/AppContext';

const ACTIVITIES = [
  { id: 'a1', type: 'refinement', message: 'Genie refined 3 requirements in CRM Integration Framework', time: '12 mins ago' },
  { id: 'a2', type: 'share',      message: 'You shared Mobile App Onboarding Flow with Team Design',   time: '4 hours ago' },
  { id: 'a3', type: 'completed',  message: 'Subscription Billing Logic draft approved by compliance',   time: 'Yesterday'   },
  { id: 'a4', type: 'comment',    message: 'Alex commented on AuthZ Protocol Specs',                    time: '2 days ago'  },
];
const ACT_ICON: Record<string, string> = { refinement: 'auto_awesome', share: 'share', completed: 'check_circle', comment: 'comment' };

const STATUS_STYLE: Record<string, string> = {
  'Approved':     'bg-emerald-50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800',
  'AI Generated': 'bg-amber-50 dark:bg-amber-950/30 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800',
  'In Review':    'bg-sky-50 dark:bg-sky-950/30 text-sky-700 dark:text-sky-400 border-sky-200 dark:border-sky-800',
  'Draft':        'bg-slate-50 dark:bg-zinc-900 text-slate-600 dark:text-zinc-400 border-slate-200 dark:border-zinc-700',
};

const listVar = { hidden: { opacity: 0 }, visible: { opacity: 1, transition: { staggerChildren: 0.08, delayChildren: 0.1 } } };
const cardVar = { hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] as [number, number, number, number] } } };

export default function DashboardView() {
  const { projects, navigate, selectProject } = useApp();
  const [search, setSearch] = useState('');
  const [genieQuery, setGenieQuery] = useState('');
  const filtered = projects.filter(p => p.name.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="min-h-screen bg-bg-cream dark:bg-black text-primary dark:text-white pb-28 font-sans transition-colors duration-300">
      <Navbar active="dashboard" />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-12">

        {}
        <motion.section initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} className="mb-12">
          <span className="text-[10px] uppercase tracking-[0.22em] text-accent-gold font-bold font-mono">Workspace Portfolio</span>
          <h1 className="font-display text-4xl md:text-5xl text-primary dark:text-white font-semibold mt-1 mb-2 tracking-tight">Good morning, Sarah.</h1>
          <p className="font-editorial text-lg text-slate-655 dark:text-zinc-400 font-light italic mb-8">
            Manage requirements, refined documents, and track AI-assisted publication cycles.
          </p>
          <ShowcaseCarousel />
        </motion.section>

        {}
        <motion.section variants={listVar} initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-40px' }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12"
        >
          {[
            { icon: 'add_circle',  title: 'Create New BRD',    desc: 'Start from a clean slate or leverage structured templates to speed up requirements gathering.', view: 'workspace' as const, primary: true },
            { icon: 'description', title: 'Import Transcript', desc: 'Convert meeting recordings, voice memos, or chats into clean, formatted engineering specs.',   view: 'workspace' as const },
            { icon: 'mic',         title: 'Upload Audio',      desc: 'Let Genie transcribe your product briefs, isolate stakeholder arguments, and outline spec sheets.', view: 'workspace' as const },
          ].map(({ icon, title, desc, view, primary }) => (
            <motion.button key={title} variants={cardVar} onClick={() => navigate(view)} className={`p-8 flex flex-col items-start gap-4 text-left cursor-pointer active:scale-[0.99] transition-all group rounded-none ${
              primary
                ? 'bg-[#1A78C2] dark:bg-[#0D2137] text-white hover:bg-[#1569a8] dark:hover:bg-[#16213e] hover:shadow-[4px_4px_0_var(--color-accent-gold)]'
                : 'bg-surface dark:bg-[#111111] border border-black/5 dark:border-white/10 hover:border-accent-gold hover:shadow-[4px_4px_0_var(--color-accent-gold)]'
            }`}>
              <div className={`h-10 w-10 flex items-center justify-center ${primary ? 'bg-white text-[#0D2137]' : 'bg-bg-cream dark:bg-zinc-800 text-accent-gold border border-black/5 dark:border-white/10'}`}>
                <span className="material-symbols-outlined text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>{icon}</span>
              </div>
              <div>
                <h3 className={`font-display text-xl font-semibold mb-1 ${primary ? 'text-white' : 'text-primary dark:text-white'}`}>{title}</h3>
                <p className={`font-editorial text-xs leading-relaxed font-light italic ${primary ? 'text-white/70' : 'text-slate-655 dark:text-zinc-400'}`}>{desc}</p>
              </div>
            </motion.button>
          ))}
        </motion.section>

        {}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">

          {}
          <div className="lg:col-span-8">
            <div className="flex justify-between items-center mb-6 pb-3 border-b border-black/5 dark:border-white/10">
              <h2 className="font-display text-2xl text-primary dark:text-white font-semibold tracking-tight">Active Manuscripts</h2>
              <button onClick={() => navigate('workspace')} className="text-accent-gold font-semibold text-xs uppercase tracking-widest hover:text-primary dark:hover:text-white transition-colors flex items-center gap-1.5">
                New draft <span className="material-symbols-outlined text-sm">arrow_forward</span>
              </button>
            </div>

            {}
            <div className="relative mb-6">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-slate-400 text-[18px]">search</span>
              <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search projects…"
                className="w-full pl-9 pr-4 py-2.5 bg-surface dark:bg-[#111111] border border-black/10 dark:border-white/10 text-sm text-primary dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-accent-gold rounded-xl transition-shadow"
              />
            </div>

            {filtered.length === 0 ? (
              <div className="bg-surface dark:bg-[#111111] border border-black/5 dark:border-white/10 p-12 text-center text-slate-655 dark:text-zinc-400 font-editorial italic">
                No projects match your search.
              </div>
            ) : (
              <motion.div variants={listVar} initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-40px' }}
                className="grid grid-cols-1 md:grid-cols-2 gap-6"
              >
                {filtered.map(p => (
                  <motion.div key={p.id} variants={cardVar}
                    onClick={() => { selectProject(p.id); navigate('document'); }}
                    className="bg-surface dark:bg-[#111111] border border-black/5 dark:border-white/10 p-6 cursor-pointer group flex flex-col justify-between min-h-[185px] hover:border-accent-gold hover:shadow-[4px_4px_0_var(--color-accent-gold)] transition-all duration-300"
                  >
                    <div>
                      <div className="flex justify-between items-start mb-5">
                        <div className="h-10 w-10 bg-bg-cream dark:bg-zinc-800 border border-black/5 dark:border-white/10 flex items-center justify-center">
                          <span className="material-symbols-outlined text-lg text-slate-655 dark:text-zinc-400">{p.icon}</span>
                        </div>
                        <span className={`text-[10px] px-2.5 py-1 font-bold uppercase tracking-widest border ${STATUS_STYLE[p.status]}`}>{p.status}</span>
                      </div>
                      <h4 className="font-display text-lg font-semibold text-primary dark:text-white group-hover:text-accent-gold transition-colors duration-200 leading-tight">{p.name}</h4>
                    </div>
                    <div className="flex items-center gap-5 text-slate-450 dark:text-zinc-500 text-[11px] font-medium pt-4 border-t border-black/5 dark:border-white/10 font-mono">
                      <span className="flex items-center gap-1"><span className="material-symbols-outlined text-sm">language</span>{p.language}</span>
                      <span className="flex items-center gap-1"><span className="material-symbols-outlined text-sm">schedule</span>{p.timeAgo}</span>
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            )}
          </div>

          {}
          <div className="lg:col-span-4 space-y-6">
            <h2 className="font-display text-2xl text-primary dark:text-white font-semibold tracking-tight">Chronicle Log</h2>
            <motion.div variants={listVar} initial="hidden" whileInView="visible" viewport={{ once: true }}
              className="bg-surface dark:bg-[#111111] border border-black/5 dark:border-white/10 p-6 shadow-sm space-y-5"
            >
              {ACTIVITIES.map(a => (
                <motion.div key={a.id} variants={cardVar} className="flex gap-4">
                  <div className="h-8 w-8 bg-bg-cream dark:bg-zinc-800 border border-black/5 dark:border-white/10 flex items-center justify-center shrink-0">
                    <span className="material-symbols-outlined text-sm text-slate-655 dark:text-zinc-400">{ACT_ICON[a.type]}</span>
                  </div>
                  <div className="flex-1 pt-0.5">
                    <p className="text-xs text-primary dark:text-white leading-relaxed">{a.message}</p>
                    <span className="text-[9px] font-bold text-accent-gold uppercase tracking-widest mt-1 block font-mono">{a.time}</span>
                  </div>
                </motion.div>
              ))}
            </motion.div>

            {}
            <motion.div initial={{ opacity: 0, scale: 0.95 }} whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true }}
              className="p-6 bg-accent-gold dark:bg-accent-purple/80 text-white relative overflow-hidden"
            >
              <div className="relative z-10">
                <div className="inline-flex items-center gap-1.5 bg-black/15 px-2 py-0.5 text-[9px] font-bold uppercase tracking-widest mb-3 font-mono">
                  <span className="material-symbols-outlined text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>lightbulb</span> PRO TIP
                </div>
                <p className="font-serif text-sm italic mb-4 text-white leading-relaxed font-light">
                  Type in the <strong>search bar</strong> below or press <strong>⌘K</strong> to globally search your file vault and issue exports in real-time.
                </p>
                <button onClick={() => navigate('workspace')}
                  className="w-full bg-white/20 hover:bg-white/30 text-white py-2.5 text-xs font-bold uppercase tracking-[0.2em] shadow-md transition-colors border border-white/30"
                >
                  Open Workspace ➜
                </button>
              </div>
            </motion.div>
          </div>
        </div>
      </main>

      {}
      <div className="fixed bottom-8 left-1/2 -translate-x-1/2 w-full max-w-xl px-4 z-50">
        <div className="backdrop-blur-xl bg-surface/95 dark:bg-[#111111]/95 border border-black/15 dark:border-white/10 shadow-2xl px-5 h-14 flex items-center gap-3 focus-within:border-accent-gold transition-all rounded-2xl">
          <span className="material-symbols-outlined text-accent-gold text-[20px]" style={{ fontVariationSettings: "'FILL' 1" }}>auto_awesome</span>
          <input value={genieQuery} onChange={e => setGenieQuery(e.target.value)}
            className="flex-1 bg-transparent text-primary dark:text-white placeholder-slate-450 dark:placeholder-zinc-500 text-xs font-serif italic focus:outline-none"
            placeholder="Search projects or ask Genie to 'draft v2.0'…"
          />
          {genieQuery && <button onClick={() => setGenieQuery('')} className="text-[10px] text-slate-450 hover:text-primary dark:hover:text-white uppercase tracking-wider transition-colors">Clear</button>}
          <div className="flex items-center gap-1 border-l border-black/10 dark:border-white/10 pl-3 ml-1 font-mono">
            <kbd className="bg-bg-cream dark:bg-zinc-800 px-1.5 py-0.5 text-[10px] font-bold text-primary dark:text-white border border-black/5 dark:border-white/10 rounded">⌘</kbd>
            <kbd className="bg-bg-cream dark:bg-zinc-800 px-1.5 py-0.5 text-[10px] font-bold text-primary dark:text-white border border-black/5 dark:border-white/10 rounded">K</kbd>
          </div>
        </div>
      </div>
    </div>
  );
}
