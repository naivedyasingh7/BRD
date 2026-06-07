import React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { useApp } from '../context/AppContext';

export default function ThemeToggle({ className = '' }: { className?: string }) {
  const { isDark, toggleDarkMode } = useApp();
  return (
    <motion.button
      whileHover={{ scale: 1.06 }}
      whileTap={{ scale: 0.92 }}
      onClick={toggleDarkMode}
      title={isDark ? 'Light mode' : 'Dark mode'}
      aria-label="Toggle theme"
      className={`relative h-9 w-9 rounded-full bg-black/5 dark:bg-white/10 border border-black/8 dark:border-white/10 flex items-center justify-center cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-gold transition-all hover:bg-black/10 dark:hover:bg-white/20 ${className}`}
    >
      <AnimatePresence mode="wait" initial={false}>
        <motion.span
          key={isDark ? 'sun' : 'moon'}
          initial={{ rotate: -90, scale: 0.3, opacity: 0 }}
          animate={{ rotate: 0, scale: 1, opacity: 1 }}
          exit={{ rotate: 90, scale: 0.3, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 280, damping: 16 }}
          className="material-symbols-outlined text-[17px] leading-none text-slate-655 dark:text-white"
          style={{ fontVariationSettings: "'FILL' 1" }}
        >
          {isDark ? 'light_mode' : 'dark_mode'}
        </motion.span>
      </AnimatePresence>
    </motion.button>
  );
}
