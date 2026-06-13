import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'motion/react';

const SLIDES = [
  {
    id: 's1', badge: 'Acoustic Pipeline', title: 'Acoustic Ingestion Engine',
    sub: 'From voice notes to formal specifications',
    desc: 'Parses product briefs, Zoom recordings, and stakeholder arguments directly into structured documents using real-time context models.',
    img: 'voice', accent: '#C5A059',
  },
  {
    id: 's2', badge: 'Matrix Translation', title: 'Precision Alignment Matrix',
    sub: 'High-fidelity requirements extraction',
    desc: 'Isolates compliance guidelines, rate-limiting policies, and security regulations. Automates generation of publication-grade user stories and flowcharts.',
    img: 'matrix', accent: '#C5A059',
  },
  {
    id: 's3', badge: 'Fintech Audit', title: 'Compliance Pre-Flight Check',
    sub: 'Zero credential lockout verification',
    desc: 'Runs requirements through active financial industry guardrails. Enforces standard lockouts, multi-factor backup gateways, and PostgreSQL audit structures.',
    img: 'security', accent: '#8B5CF6',
  },
  {
    id: 's4', badge: 'Enterprise Sync', title: 'Global Integration Gateways',
    sub: 'Direct push to Confluence and Jira',
    desc: 'Distributes structured requirements natively to corporate wiki systems, formats user stories into tracker backlogs, and persists audit logs into secure databases.',
    img: 'office', accent: '#C5A059',
  },
];

export default function ShowcaseCarousel() {
  const [idx, setIdx] = useState(0);
  const [playing, setPlaying] = useState(true);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  const next = useCallback(() => setIdx(i => (i + 1) % SLIDES.length), []);
  const prev = useCallback(() => setIdx(i => (i - 1 + SLIDES.length) % SLIDES.length), []);

  const stop = useCallback(() => {
    if (timer.current) { clearInterval(timer.current); timer.current = null; }
  }, []);

  const resume = useCallback(() => {
    if (!playing) return;
    stop();
    timer.current = setInterval(next, 5500);
  }, [playing, next, stop]);

  useEffect(() => {
    if (!playing) { stop(); return; }
    stop();
    timer.current = setInterval(next, 5500);
    return stop;
  }, [idx, playing, next, stop]);

  const slide = SLIDES[idx];

  return (
    <div
      className="bg-surface dark:bg-[#111111] border border-black/5 dark:border-white/10 overflow-hidden shadow-sm hover:shadow-md transition-shadow"
      onMouseEnter={stop}
      onMouseLeave={resume}
    >
      {}
      <div className="relative aspect-[21/9] bg-slate-900 overflow-hidden">
        <AnimatePresence mode="sync">
          <motion.img
            key={slide.id}
            src={`https://picsum.photos/seed/${slide.img}/1200/500`}
            alt={slide.title}
            initial={{ opacity: 0, scale: 1.08 }}
            animate={{ opacity: 0.38, scale: 1 }}
            exit={{ opacity: 0, scale: 0.96 }}
            transition={{ duration: 1.1, ease: [0.25, 0.46, 0.45, 0.94] }}
            className="absolute inset-0 w-full h-full object-cover"
            loading="lazy"
          />
        </AnimatePresence>
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/60 to-transparent" />

        {}
        <div className="absolute top-4 left-4 right-4 flex justify-between items-center z-10">
          <AnimatePresence mode="wait">
            <motion.span
              key={slide.id + '-badge'}
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.4, ease: [0.25, 0.46, 0.45, 0.94] }}
              className="text-[9px] bg-accent-gold/20 text-accent-gold border border-accent-gold/40 px-2.5 py-1 tracking-widest uppercase font-bold font-mono"
            >
              {slide.badge}
            </motion.span>
          </AnimatePresence>
          <div className="flex items-center gap-1.5 bg-black/40 backdrop-blur-sm px-2 py-1 text-[9px] tracking-widest text-white/70 font-mono font-bold">
            <span>{String(idx + 1).padStart(2, '0')}</span>
            <span className="opacity-40">/</span>
            <span>{String(SLIDES.length).padStart(2, '0')}</span>
          </div>
        </div>

        {}
        <button
          onClick={() => setPlaying(p => !p)}
          className="absolute bottom-4 right-4 z-20 h-8 w-8 bg-black/40 backdrop-blur-sm hover:bg-black/60 text-white flex items-center justify-center border border-white/10 transition-all cursor-pointer active:scale-95"
          aria-label={playing ? 'Pause' : 'Play'}
        >
          <span className="material-symbols-outlined text-sm">{playing ? 'pause' : 'play_arrow'}</span>
        </button>

        {}
        <div className="absolute bottom-0 inset-x-0 p-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={slide.id + '-h'}
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] }}
            >
              <h2 className="font-serif text-2xl font-light italic text-white leading-tight">{slide.title}</h2>
              <p className="text-accent-gold text-[10px] uppercase tracking-widest font-mono font-semibold mt-1">{slide.sub}</p>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>

      {}
      <div className="p-5 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <AnimatePresence mode="wait">
          <motion.p
            key={slide.id + '-d'}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.45, ease: [0.25, 0.46, 0.45, 0.94] }}
            className="font-editorial text-sm text-slate-655 dark:text-zinc-400 font-light italic leading-relaxed max-w-2xl"
          >
            {slide.desc}
          </motion.p>
        </AnimatePresence>
        <div className="flex items-center gap-3 shrink-0">
          <button onClick={prev} aria-label="Previous" className="h-9 w-9 bg-surface dark:bg-zinc-900 border border-black/10 dark:border-white/10 text-primary dark:text-white flex items-center justify-center hover:border-accent-gold transition-colors cursor-pointer active:scale-95">
            <span className="material-symbols-outlined text-sm">arrow_back</span>
          </button>
          <button onClick={next} aria-label="Next" className="h-9 w-9 bg-surface dark:bg-zinc-900 border border-black/10 dark:border-white/10 text-primary dark:text-white flex items-center justify-center hover:border-accent-gold transition-colors cursor-pointer active:scale-95">
            <span className="material-symbols-outlined text-sm">arrow_forward</span>
          </button>
          <div className="flex items-center gap-1.5 ml-1">
            {SLIDES.map((_, i) => (
              <button key={i} onClick={() => { setIdx(i); setPlaying(false); }} aria-label={`Slide ${i + 1}`}
                className={`h-2 transition-all rounded-none border-0 p-0 cursor-pointer ${i === idx ? 'w-6 bg-accent-gold' : 'w-2 bg-slate-300 dark:bg-zinc-700 hover:bg-slate-400'}`}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
