import React from 'react';
import { motion } from 'motion/react';
import BrandLogo from './BrandLogo';
import ThemeToggle from './ThemeToggle';
import { useApp } from '../context/AppContext';
import { ViewType } from '../types';

const NAV_LINKS: { label: string; view: ViewType }[] = [
  { label: 'Home',      view: 'dashboard'  },
  { label: 'Workspace', view: 'workspace'  },
  { label: 'Projects',  view: 'document'   },
  { label: 'Settings',  view: 'settings'   },
];

export default function Navbar({ active }: { active: ViewType }) {
  const { navigate } = useApp();
  return (
    <div className="sticky top-4 z-40 w-full px-4 sm:px-6">
      <motion.nav
        initial={{ y: -16, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="bg-white/90 dark:bg-[#111111]/70 backdrop-blur-md border border-black/8 dark:border-white/10 shadow-sm rounded-full h-14 max-w-7xl mx-auto flex items-center px-5"
      >
        <div className="flex justify-between items-center w-full">
          {/* Brand */}
          <button onClick={() => navigate('splash')} className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <BrandLogo size="sm" />
            <span className="font-serif text-sm font-bold italic text-primary dark:text-white hidden sm:inline">BRD Genie</span>
          </button>

          {/* Links */}
          <div className="flex items-center gap-4 sm:gap-5">
            {NAV_LINKS.map(({ label, view }) => (
              <button
                key={view}
                onClick={() => navigate(view)}
                className={`font-sans text-xs uppercase tracking-wider transition-colors duration-200 ${
                  active === view
                    ? 'text-primary dark:text-white font-bold border-b-2 border-accent-gold pb-0.5'
                    : 'text-slate-655 dark:text-zinc-400 font-medium hover:text-primary dark:hover:text-white'
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Right controls */}
          <div className="flex items-center gap-2 sm:gap-3">
            <ThemeToggle />
            <button
              onClick={() => navigate('workspace')}
              className="bg-primary dark:bg-accent-gold text-white dark:text-black font-semibold h-9 px-4 rounded-full text-[10px] uppercase tracking-[0.15em] hover:bg-neutral-700 dark:hover:bg-accent-gold-light transition-all active:scale-95 shadow-sm hidden sm:flex items-center"
            >
              Draft New
            </button>
          </div>
        </div>
      </motion.nav>
    </div>
  );
}
