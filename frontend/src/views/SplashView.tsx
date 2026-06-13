import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import AmbientCanvas from '../components/AmbientCanvas';
import BrandLogo from '../components/BrandLogo';
import ThemeToggle from '../components/ThemeToggle';
import { useApp } from '../context/AppContext';

export default function SplashView() {
  const { navigate, isDark } = useApp();
  const [revealed, setRevealed] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setRevealed(true), 2800);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className="relative min-h-screen w-full flex flex-col overflow-hidden bg-white dark:bg-black transition-colors duration-500">
      {}
      <div className="absolute inset-0 z-0">
        <AmbientCanvas isDark={isDark} />
      </div>

      {}
      {!isDark && (
        <div className="absolute inset-0 z-0 bg-gradient-to-br from-blue-50/80 via-white/60 to-slate-50/80" />
      )}

      {}
      <div className="absolute top-5 right-5 z-20 flex items-center gap-3">
        <ThemeToggle />
        <button
          onClick={() => navigate('signin')}
          className="px-5 py-2 border border-black/15 dark:border-white/20 text-primary dark:text-white text-xs font-bold uppercase tracking-[0.2em] hover:bg-black/5 dark:hover:bg-white/10 transition-colors rounded-full backdrop-blur-sm"
        >
          Log In
        </button>
      </div>

      {}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6 text-center">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 1.6, ease: [0.16, 1, 0.3, 1] }}
          className="relative flex items-center justify-center mb-6"
        >
          <motion.div
            animate={{ scale: [1, 1.12, 1], opacity: [0.5, 0.25, 0.5] }}
            transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
            className="absolute w-56 h-56 rounded-full bg-accent-blue/10 dark:bg-accent-blue/15 blur-3xl"
          />
          <BrandLogo size="xl" animate className="relative z-10" />
        </motion.div>

        <AnimatePresence>
          {revealed && (
            <motion.h1
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05, duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
              className="font-serif text-6xl md:text-7xl lg:text-8xl font-bold text-primary dark:text-white tracking-tight"
            >
              BRD Genie
            </motion.h1>
          )}
        </AnimatePresence>
      </div>

      {}
      <AnimatePresence>
        {revealed && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
            className="relative z-10 flex flex-col items-center pb-12 md:pb-16 gap-4 text-center px-6"
          >
            <p className="font-sans text-sm font-normal text-slate-450 dark:text-white/50 leading-relaxed text-center whitespace-nowrap">
              <span className="block">Turn chaotic conversations into audit-ready specifications.</span>
              <span className="block">The premium requirements engineering workspace for Bharat.</span>
            </p>
            <button
              onClick={() => navigate('signin')}
              className="group relative inline-flex items-center gap-3 px-10 py-4 bg-primary dark:bg-white text-white dark:text-black rounded-2xl overflow-hidden transition-all hover:scale-[1.03] active:scale-[0.98] shadow-xl shadow-black/10 dark:shadow-black/30"
            >
              <div className="absolute inset-0 -translate-x-full group-hover:translate-x-0 bg-gradient-to-r from-transparent via-white/10 to-transparent transition-transform duration-700 skew-x-12" />
              <span className="font-semibold tracking-wide relative z-10">Enter the Workspace</span>
              <span className="material-symbols-outlined text-[20px] transition-transform duration-300 group-hover:translate-x-1 relative z-10">east</span>
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
