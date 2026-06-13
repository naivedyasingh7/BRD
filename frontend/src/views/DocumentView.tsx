import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import DOMPurify from 'dompurify';
import Navbar from '../components/Navbar';
import { useApp } from '../context/AppContext';

const SVG_PURIFY_CONFIG = {
  USE_PROFILES: { svg: true, svgFilters: true },
  FORBID_TAGS: ['script', 'use'],
  FORBID_ATTR: ['onload', 'onerror', 'onclick', 'onmouseover', 'href', 'xlink:href'],
};

const STATUS_STYLE: Record<string, string> = {
  Validated:  'bg-emerald-50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800',
  'In Review':'bg-sky-50 dark:bg-sky-950/30 text-sky-700 dark:text-sky-400 border-sky-200 dark:border-sky-800',
  Draft:      'bg-slate-50 dark:bg-zinc-900 text-slate-600 dark:text-zinc-400 border-slate-200 dark:border-zinc-700',
};

type Section = 'executive' | 'objectives' | 'functional' | 'visuals' | 'stories';
const TOC: { id: string; label: string; section: Section }[] = [
  { id: '1.0', label: '1.0 Executive Summary',         section: 'executive'  },
  { id: '2.0', label: '2.0 Project Objectives',         section: 'objectives' },
  { id: '3.0', label: '3.0 Functional Requirements',    section: 'functional' },
  { id: '4.0', label: '4.0 System Flowchart',           section: 'visuals'    },
  { id: '5.0', label: '5.0 User Stories Matrix',        section: 'stories'    },
];

export default function DocumentView() {
  const { selectedProjectId, documents, updateDocument, navigate, addToast, projects } = useApp();
  const doc = documents[selectedProjectId];

  const [activeTab, setActiveTab]       = useState('1.0');
  const [activeVer, setActiveVer]       = useState('v1.4.2');
  const [zoomed, setZoomed]             = useState(false);
  const [exporting, setExporting]       = useState(false);
  const [exportTarget, setExportTarget] = useState('');
  const [exportPct, setExportPct]       = useState(0);
  const [newComment, setNewComment]     = useState('');
  const [geniePrompt, setGeniePrompt]   = useState('');
  const [genieLog, setGenieLog]         = useState<string[]>([]);
  const [genieLoading, setGenieLoading] = useState(false);
  const [comments, setComments]         = useState([{
    id: 'c1', author: 'Alistair Ross', role: 'Head of Compliance',
    text: "Let's ensure we mandate dual-channel delivery (SMS & WhatsApp). Some regions experience high latency with standard SMS gateways.",
    time: '2h ago',
  }]);

  const executiveRef  = useRef<HTMLDivElement>(null);
  const objectivesRef = useRef<HTMLDivElement>(null);
  const functionalRef = useRef<HTMLDivElement>(null);
  const visualsRef    = useRef<HTMLDivElement>(null);
  const storiesRef    = useRef<HTMLDivElement>(null);

  const refs: Record<Section, React.RefObject<HTMLDivElement>> = {
    executive:  executiveRef,
    objectives: objectivesRef,
    functional: functionalRef,
    visuals:    visualsRef,
    stories:    storiesRef,
  };

  if (!doc) {
    return (
      <div className="min-h-screen bg-bg-cream dark:bg-black flex items-center justify-center">
        <div className="text-center space-y-4">
          <p className="font-editorial italic text-slate-655 dark:text-zinc-400">No document selected.</p>
          <button onClick={() => navigate('dashboard')} className="text-accent-gold underline text-sm">Back to dashboard</button>
        </div>
      </div>
    );
  }

  const scrollTo = (section: Section, id: string) => {
    setActiveTab(id);
    refs[section].current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const triggerExport = (target: string) => {
    if (target === 'Export PDF') {
      const content = [
        `# ${doc.projectName}`,
        `## Executive Summary`,
        doc.executiveSummary,
        `## Objectives`,
        doc.objectives.map(o => `- ${o}`).join('\n'),
        `## Functional Requirements`,
        doc.functionalRequirements.map(r => `### ${r.id}: ${r.title}\n${r.description}`).join('\n\n'),
        `## User Stories`,
        doc.userStories.map(s => `- **${s.actor}**: ${s.goal} → ${s.outcome}`).join('\n'),
      ].join('\n\n');
      const blob = new Blob([content], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = `${doc.projectName.replace(/\s+/g, '_')}_BRD.md`;
      a.click(); URL.revokeObjectURL(url);
      addToast('BRD downloaded as Markdown.', 'success');
      return;
    }
    setExportTarget(target); setExporting(true); setExportPct(0);
    const iv = setInterval(() => {
      setExportPct(p => {
        if (p >= 100) {
          clearInterval(iv);
          setTimeout(() => { setExporting(false); addToast(`${target} integration is not configured in this demo.`, 'info'); }, 600);
          return 100;
        }
        return p + 20;
      });
    }, 220);
  };

  const applyImprovement = (id: string, text: string) => {
    const updated = { ...doc, suggestedImprovements: doc.suggestedImprovements.map(i => i.id === id ? { ...i, applied: true } : i) };
    updateDocument(selectedProjectId, updated);
    setGenieLog(l => [...l, `Applied: "${text}"`]);
    addToast(`Incorporated: "${text}"`, 'success');
  };

  const handleGeniePrompt = async () => {
    if (!geniePrompt.trim() || genieLoading) return;
    const p = geniePrompt; setGeniePrompt('');
    setGenieLog(l => [...l, `Query: "${p}"…`]);
    setGenieLoading(true);

    const project = projects.find(pr => pr.id === selectedProjectId);
    const markdown = doc.functionalRequirements.map(r => `### ${r.id}: ${r.title}\n${r.description}`).join('\n\n');
    const existingBrd = `# ${doc.projectName}\n\n## Executive Summary\n${doc.executiveSummary}\n\n## Functional Requirements\n${markdown}`;

    try {
      const response = await fetch('/api/clarify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          state: {
            raw_input: '',
            cleaned_input: existingBrd,
            structured_data: { context: doc.executiveSummary, requirements: markdown, stakeholders: '', risks: '' },
            questions: [p],
            answers: [p],
            brd_draft: existingBrd,
            final_brd: existingBrd,
            language: project?.language ?? 'English',
            localized_brd: '',
          },
          answers: [p],
        }),
      });

      if (response.ok) {
        const state = await response.json();
        const updatedMarkdown = (state.final_brd as string) || (state.brd_draft as string) || '';
        if (updatedMarkdown) {
          const lines = updatedMarkdown.split('\n').filter((l: string) => l.startsWith('-') || l.startsWith('*'));
          updateDocument(selectedProjectId, {
            ...doc,
            executiveSummary: updatedMarkdown.match(/executive summary[^\n]*\n+([^\n#][^\n]+)/i)?.[1]?.trim() ?? doc.executiveSummary,
            suggestedImprovements: [
              ...doc.suggestedImprovements,
              { id: `imp_${Date.now()}`, text: `Applied: ${p}`, applied: true },
            ],
          });
          setGenieLog(l => [...l, `Genie: Amendment applied (${lines.length} items updated).`]);
          addToast('Document updated via Genie Agent.', 'success');
        } else {
          setGenieLog(l => [...l, `Genie: No changes returned from backend.`]);
        }
      } else {
        setGenieLog(l => [...l, `Genie: Backend error. Is the server running?`]);
        addToast('Genie request failed. Check backend connection.', 'error');
      }
    } catch {
      setGenieLog(l => [...l, `Genie: Could not reach backend.`]);
      addToast('Genie request failed. Check backend connection.', 'error');
    } finally {
      setGenieLoading(false);
    }
  };

  const postComment = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    setComments(c => [...c, { id: Math.random().toString(), author: 'Sarah Analyst', role: 'Lead BA (You)', text: newComment, time: 'Just now' }]);
    setNewComment('');
    addToast('Comment posted.', 'success');
  };

  return (
    <div className="min-h-screen bg-bg-cream dark:bg-black text-primary dark:text-white pb-24 font-sans transition-colors duration-300">

      {exporting && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-6"
          >
            <motion.div initial={{ scale: 0.94 }} animate={{ scale: 1 }} exit={{ scale: 0.94 }}
              className="bg-surface dark:bg-[#111111] border border-black/10 dark:border-white/10 p-8 max-w-sm w-full shadow-2xl space-y-5 rounded-xl"
            >
              <div className="flex items-center gap-4">
                <span className="material-symbols-outlined text-4xl animate-spin text-accent-gold">sync</span>
                <div>
                  <p className="font-serif font-bold italic text-sm">Exporting Requirement Matrix</p>
                  <p className="text-xs text-slate-655 dark:text-zinc-400 italic font-editorial">Packaging to {exportTarget}…</p>
                </div>
              </div>
              <div className="w-full h-[3px] bg-black/5 dark:bg-white/5 overflow-hidden rounded-full">
                <motion.div className="bg-accent-gold h-full rounded-full" animate={{ width: `${exportPct}%` }} transition={{ duration: 0.2 }} />
              </div>
              <div className="flex justify-between text-[9px] font-mono text-slate-450 dark:text-zinc-500 font-bold uppercase tracking-wider">
                <span>Bundling context</span><span>{exportPct}%</span>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {zoomed && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={() => setZoomed(false)}
            className="fixed inset-0 bg-black/90 backdrop-blur-md z-50 flex items-center justify-center p-6 cursor-zoom-out"
          >
            <motion.div initial={{ scale: 0.94, y: 16 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.94 }}
              onClick={e => e.stopPropagation()}
              className="bg-surface dark:bg-[#111111] border border-black/10 dark:border-white/10 p-10 rounded-2xl max-w-5xl w-full shadow-2xl relative text-center"
            >
              <button onClick={() => setZoomed(false)} className="absolute right-5 top-5 p-2 rounded-full bg-black/5 dark:bg-white/10 hover:text-accent-gold transition-colors cursor-pointer">
                <span className="material-symbols-outlined text-sm">close</span>
              </button>
              <h4 className="font-serif text-xl font-bold italic mb-8">System Architecture Diagram</h4>
              <div className="bg-[#1A1A1A] p-8 rounded-xl flex items-center justify-center overflow-auto max-h-[65vh]">
                <motion.div drag dragConstraints={{ left: -120, right: 120, top: -120, bottom: 120 }}
                  className="w-full max-w-2xl cursor-grab active:cursor-grabbing"
                  dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(doc.flowchartSvg, SVG_PURIFY_CONFIG) }}
                />
              </div>
              <p className="text-[9px] font-mono uppercase tracking-widest text-slate-450 dark:text-zinc-500 mt-5">Drag to pan · Click outside to dismiss</p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <Navbar active="document" />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-12">
        <header className="mb-10 border-b border-black/5 dark:border-white/10 pb-6">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-5">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <span className="border border-accent-gold text-accent-gold font-bold text-[9px] px-2.5 py-1 uppercase tracking-widest">Specification</span>
                <span className="text-[10px] text-slate-450 dark:text-zinc-500 uppercase tracking-widest font-mono font-bold flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-xs">update</span> Edited 2h ago
                </span>
              </div>
              <h1 className="font-serif text-3xl font-light italic text-primary dark:text-white leading-tight">{doc.projectName}</h1>
            </div>
            <div className="flex flex-wrap gap-2">
              {[
                { label: 'Push to Jira',       icon: 'grid_view',  border: false },
                { label: 'Push to Confluence', icon: 'feed',       border: true  },
                { label: 'Export PDF',         icon: 'download',   border: false },
              ].map(({ label, icon, border }) => (
                <button key={label} onClick={() => triggerExport(label)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 text-[10px] font-bold uppercase tracking-widest cursor-pointer transition-colors ${
                    border
                      ? 'bg-surface dark:bg-zinc-900 border border-accent-gold text-accent-gold hover:bg-bg-cream dark:hover:bg-zinc-800'
                      : 'bg-surface dark:bg-zinc-900 border border-black/10 dark:border-white/10 text-primary dark:text-white hover:bg-bg-cream dark:hover:bg-zinc-800'
                  }`}
                >
                  <span className="material-symbols-outlined text-xs">{icon}</span>{label}
                </button>
              ))}
            </div>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">

          <aside className="lg:col-span-3">
            <div className="bg-surface dark:bg-[#111111] border border-black/5 dark:border-white/10 p-5 sticky top-24 shadow-sm space-y-7">
              <div>
                <p className="text-[10px] font-bold text-accent-gold tracking-[0.2em] uppercase mb-3 font-mono">Document Index</p>
                <nav className="space-y-0.5">
                  {TOC.map(item => (
                    <button key={item.id} onClick={() => scrollTo(item.section, item.id)}
                      className={`w-full text-left px-3 py-2.5 text-xs font-semibold transition-all flex items-center justify-between cursor-pointer border-l-2 ${
                        activeTab === item.id
                          ? 'bg-bg-cream dark:bg-zinc-800 border-accent-gold text-primary dark:text-white font-serif italic'
                          : 'text-slate-655 dark:text-zinc-400 hover:bg-bg-cream dark:hover:bg-zinc-800/50 border-transparent'
                      }`}
                    >
                      {item.label}
                      <span className="material-symbols-outlined text-[10px] opacity-30">chevron_right</span>
                    </button>
                  ))}
                </nav>
              </div>

              <div className="border-t border-black/5 dark:border-white/10 pt-5">
                <p className="text-[10px] font-bold text-slate-450 dark:text-zinc-500 tracking-[0.2em] uppercase mb-3 font-mono">Version History</p>
                <div className="space-y-1.5">
                  {[
                    { v: 'v1.4.2', date: 'Jun 7 (Current)' },
                    { v: 'v1.4.1', date: 'Jun 4 — Alistair' },
                    { v: 'v1.0.0', date: 'May 28 (Draft)' },
                  ].map(ver => (
                    <button key={ver.v} onClick={() => { setActiveVer(ver.v); addToast(`Switched to ${ver.v}`, 'info'); }}
                      className={`w-full text-left p-2.5 rounded-xl text-xs flex justify-between items-center cursor-pointer transition-all ${
                        activeVer === ver.v
                          ? 'bg-primary dark:bg-accent-purple text-white shadow-md'
                          : 'bg-surface dark:bg-zinc-900/50 border border-black/5 dark:border-white/10 text-slate-655 dark:text-zinc-400 hover:border-accent-gold/40'
                      }`}
                    >
                      <span className="font-mono font-bold">{ver.v}</span>
                      <span className="text-[9px] uppercase tracking-wider opacity-80">{ver.date}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </aside>

          <article className="lg:col-span-6 bg-surface dark:bg-[#111111] border border-black/5 dark:border-white/10 p-6 md:p-10 shadow-sm space-y-12 min-h-[800px]">

            <div ref={refs.executive} className="space-y-4">
              <h2 className="font-serif text-xl font-light italic border-b border-black/5 dark:border-white/10 pb-2.5">1.0 Executive Summary</h2>
              <p className="font-editorial text-sm text-slate-655 dark:text-zinc-300 leading-relaxed font-light italic">{doc.executiveSummary}</p>
            </div>

            <div ref={refs.objectives} className="space-y-4">
              <h2 className="font-serif text-xl font-light italic border-b border-black/5 dark:border-white/10 pb-2.5">2.0 Project Objectives</h2>
              <div className="p-5 bg-bg-cream dark:bg-zinc-900/50 border-l-2 border-accent-gold space-y-3">
                <p className="text-sm font-serif font-bold italic">Core compliance and architectural objectives:</p>
                <ul className="space-y-2 list-disc pl-5 text-xs text-slate-655 dark:text-zinc-300 font-editorial font-light italic">
                  {doc.objectives.length > 0 ? doc.objectives.map((o, i) => <li key={i}>{o}</li>) : <li>No objectives specified.</li>}
                </ul>
              </div>
            </div>

            <div ref={refs.functional} className="space-y-4">
              <h2 className="font-serif text-xl font-light italic border-b border-black/5 dark:border-white/10 pb-2.5">3.0 Functional Requirements</h2>
              {doc.functionalRequirements.length > 0 ? doc.functionalRequirements.map((req, idx) => (
                <div key={req.id} className="bg-bg-cream/50 dark:bg-zinc-900/30 border border-black/5 dark:border-white/10 p-5 space-y-4">
                  <div className="flex justify-between items-center border-b border-black/5 dark:border-white/10 pb-2">
                    <span className="font-mono text-[10px] font-bold text-slate-450 dark:text-zinc-500 tracking-wider">{req.id}</span>
                    <span className={`font-bold px-2 py-0.5 text-[9px] uppercase border ${STATUS_STYLE[req.status] ?? STATUS_STYLE.Draft}`}>{req.status}</span>
                  </div>
                  <p className="font-serif font-bold text-xs italic uppercase tracking-wider">{req.title}</p>
                  <p className="text-xs text-slate-655 dark:text-zinc-300 font-editorial font-light italic leading-relaxed">{req.description}</p>

                  {idx === 0 && (
                    <div className="border-t border-black/5 dark:border-white/10 pt-4 space-y-3">
                      <span className="text-[9px] font-bold text-accent-gold uppercase tracking-[0.15em] font-sans">Collaborator Thread</span>
                      {comments.map(c => (
                        <div key={c.id} className="bg-surface dark:bg-zinc-900 border border-black/5 dark:border-white/10 p-4 rounded-xl flex gap-3 hover:border-accent-gold/40 transition-colors">
                          <div className="w-9 h-9 rounded-full bg-accent-gold/20 flex items-center justify-center text-accent-gold font-bold text-sm shrink-0">{c.author[0]}</div>
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-serif font-bold text-xs italic">{c.author}</span>
                              <span className="text-[9px] font-mono bg-black/5 dark:bg-white/5 px-1.5 py-0.5 rounded">{c.role}</span>
                              <span className="text-[9px] text-slate-450 dark:text-zinc-500 font-mono ml-auto">{c.time}</span>
                            </div>
                            <p className="text-xs text-slate-655 dark:text-zinc-300 font-editorial font-light italic leading-relaxed">{c.text}</p>
                          </div>
                        </div>
                      ))}
                      <form onSubmit={postComment} className="flex gap-2 pt-3 border-t border-black/5 dark:border-white/10">
                        <input type="text" value={newComment} onChange={e => setNewComment(e.target.value)}
                          placeholder="Post a reply…"
                          className="flex-1 bg-surface dark:bg-zinc-900 border border-black/10 dark:border-white/10 focus:border-accent-gold rounded-full px-4 py-2 text-xs outline-none font-serif italic text-primary dark:text-white"
                        />
                        <button type="submit" className="bg-primary dark:bg-accent-gold text-white dark:text-black font-bold text-[10px] uppercase tracking-wider px-5 py-2 rounded-full cursor-pointer active:scale-95 transition-transform">Post</button>
                      </form>
                    </div>
                  )}
                </div>
              )) : (
                <div className="bg-surface dark:bg-zinc-900 border border-black/5 dark:border-white/10 p-12 text-center text-slate-655 dark:text-zinc-400 font-editorial italic">
                  No functional requirements defined yet.
                </div>
              )}
            </div>

            <div ref={refs.visuals} className="space-y-4">
              <div className="flex justify-between items-center border-b border-black/5 dark:border-white/10 pb-2.5">
                <h2 className="font-serif text-xl font-light italic">4.0 System Flowchart</h2>
                <button onClick={() => setZoomed(true)} className="text-xs text-accent-gold font-bold flex items-center gap-1 cursor-pointer font-serif italic hover:underline">
                  <span className="material-symbols-outlined text-xs">zoom_in</span> Zoom
                </button>
              </div>
              <div onClick={() => setZoomed(true)} className="bg-[#1A1A1A] p-8 border border-black/10 dark:border-white/10 flex justify-center items-center relative group cursor-zoom-in overflow-hidden">
                <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                <div className="w-full text-white" dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(doc.flowchartSvg, SVG_PURIFY_CONFIG) }} />
                <p className="absolute bottom-2 left-1/2 -translate-x-1/2 text-[9px] font-mono tracking-widest text-accent-gold/70 uppercase">[Click to zoom]</p>
              </div>
            </div>

            <div ref={refs.stories} className="space-y-4">
              <h2 className="font-serif text-xl font-light italic border-b border-black/5 dark:border-white/10 pb-2.5">5.0 User Stories Matrix</h2>
              <div className="overflow-x-auto border border-black/5 dark:border-white/10 bg-surface dark:bg-zinc-900">
                <table className="w-full text-left text-xs border-collapse">
                  <thead className="bg-bg-cream dark:bg-zinc-800 uppercase font-bold tracking-widest text-[9px] border-b border-black/10 dark:border-white/10 text-slate-655 dark:text-zinc-400">
                    <tr>
                      <th className="px-5 py-3">Actor</th>
                      <th className="px-5 py-3">Goal</th>
                      <th className="px-5 py-3">Outcome</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-black/5 dark:divide-white/5 font-editorial italic">
                    {doc.userStories.length > 0 ? doc.userStories.map((s, i) => (
                      <tr key={i}>
                        <td className="px-5 py-4 font-serif font-bold italic text-primary dark:text-white">{s.actor}</td>
                        <td className="px-5 py-4 text-slate-655 dark:text-zinc-300">{s.goal}</td>
                        <td className="px-5 py-4 text-slate-655 dark:text-zinc-300 leading-relaxed">{s.outcome}</td>
                      </tr>
                    )) : (
                      <tr><td colSpan={3} className="px-5 py-8 text-center text-slate-450 italic">No user stories defined.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </article>

          <aside className="lg:col-span-3 space-y-6">
            <div className="bg-surface dark:bg-[#111111] border border-black/5 dark:border-white/10 p-5 shadow-sm space-y-4">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-accent-gold animate-pulse" style={{ fontVariationSettings: "'FILL' 1" }}>auto_awesome</span>
                <p className="text-xs font-bold uppercase tracking-[0.15em]">Genie Smart Suggestions</p>
              </div>
              <div className="space-y-3">
                {doc.suggestedImprovements.length > 0 ? doc.suggestedImprovements.map(imp => (
                  <div key={imp.id} className={`p-3.5 border text-xs flex flex-col gap-2.5 transition-all ${
                    imp.applied
                      ? 'bg-emerald-50 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-400 line-through italic font-editorial'
                      : 'bg-bg-cream/40 dark:bg-zinc-900/40 border-black/10 dark:border-white/10 text-slate-655 dark:text-zinc-300'
                  }`}>
                    <p className="leading-relaxed font-editorial italic font-light">{imp.text}</p>
                    {!imp.applied && (
                      <button onClick={() => applyImprovement(imp.id, imp.text)}
                        className="bg-primary dark:bg-accent-gold text-white dark:text-black font-bold px-2.5 py-1 text-[9px] uppercase tracking-widest cursor-pointer active:scale-95 transition-transform w-fit">
                        Apply Rule ➜
                      </button>
                    )}
                  </div>
                )) : <p className="text-xs text-slate-450 dark:text-zinc-500 italic font-editorial">No improvements suggested.</p>}
              </div>
            </div>

            <div className="bg-surface dark:bg-[#111111] border border-black/5 dark:border-white/10 p-5 shadow-sm space-y-4">
              <p className="text-xs font-bold uppercase tracking-[0.15em]">Dialogue with Genie</p>
              {genieLog.length > 0 && (
                <div className="bg-bg-cream dark:bg-zinc-900 border border-black/5 dark:border-white/10 p-2.5 text-[9px] font-mono text-emerald-700 dark:text-emerald-400 font-bold h-20 overflow-y-auto">
                  {genieLog.map((l, i) => <div key={i} className="mb-0.5">❯ {l}</div>)}
                </div>
              )}
              <textarea value={geniePrompt} onChange={e => setGeniePrompt(e.target.value)}
                placeholder="Ask Genie: 'add SLA compliance paragraph'…"
                className="w-full h-24 bg-surface dark:bg-zinc-900 border border-black/10 dark:border-white/10 focus:border-accent-gold p-3.5 text-xs outline-none resize-none font-serif italic text-primary dark:text-white focus:ring-0"
              />
              <button onClick={handleGeniePrompt} disabled={genieLoading}
                className="w-full bg-primary dark:bg-accent-gold hover:bg-neutral-800 font-bold py-2.5 text-xs text-white dark:text-black cursor-pointer uppercase tracking-widest active:scale-95 transition-transform disabled:opacity-50">
                {genieLoading ? 'Processing…' : 'Incorporate Amendments'}
              </button>
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
}
