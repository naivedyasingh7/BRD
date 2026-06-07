import React, { useState } from 'react';
import { motion } from 'motion/react';
import Navbar from '../components/Navbar';
import ThemeToggle from '../components/ThemeToggle';
import { useApp } from '../context/AppContext';

const cardVar = {
  hidden:  { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] as [number, number, number, number] } },
};

export default function SettingsView() {
  const { userEmail, navigate, addToast } = useApp();
  const [name, setName]            = useState('Sarah Analyst');
  const [company, setCompany]      = useState('Global Fintech Corp');
  const [notifications, setNotifs] = useState(true);

  const handleSave = () => addToast('Settings saved successfully.', 'success');

  const handleSignOut = () => {
    addToast('Signing out…', 'info');
    setTimeout(() => navigate('splash'), 1000);
  };

  const Field = ({ label, value, onChange, disabled, type = 'text' }: {
    label: string; value: string; onChange?: (v: string) => void; disabled?: boolean; type?: string;
  }) => (
    <div>
      <label className="block text-[10px] font-sans font-semibold uppercase tracking-widest text-slate-655 dark:text-zinc-400 mb-1.5">
        {label}
      </label>
      <input
        type={type} value={value} disabled={disabled}
        onChange={e => onChange?.(e.target.value)}
        className={`w-full border px-4 py-3 text-sm font-sans font-semibold focus:outline-none focus:ring-2 focus:ring-accent-gold transition-all ${
          disabled
            ? 'bg-black/5 dark:bg-black/20 border-black/5 dark:border-white/5 text-slate-450 dark:text-zinc-500 cursor-not-allowed'
            : 'bg-surface dark:bg-zinc-900 border-black/10 dark:border-white/10 text-primary dark:text-white focus:border-accent-gold'
        }`}
      />
      {disabled && (
        <span className="text-[10px] font-sans text-slate-450 dark:text-zinc-500 mt-1 block">
          Cannot be changed directly.
        </span>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-bg-cream dark:bg-black text-primary dark:text-white font-sans transition-colors duration-300 pb-20">
      <Navbar active="settings" />

      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-12">
        {/* Page header */}
        <motion.div initial="hidden" animate="visible" variants={cardVar} className="mb-10">
          <span className="text-[10px] uppercase tracking-[0.22em] text-accent-gold font-sans font-bold font-mono">Account</span>
          <h1 className="font-sans text-4xl font-semibold text-primary dark:text-white mt-1 mb-2 tracking-tight">Settings</h1>
          <p className="font-sans text-slate-655 dark:text-zinc-400 text-sm font-normal">
            Manage your profile, preferences, and workspace configuration.
          </p>
        </motion.div>

        <div className="space-y-6">

          {/* Profile */}
          <motion.section variants={cardVar} initial="hidden" animate="visible"
            className="bg-surface dark:bg-[#111111] border border-black/5 dark:border-white/10 p-8 shadow-sm"
          >
            <h2 className="font-sans text-xl font-semibold mb-6 border-b border-black/5 dark:border-white/10 pb-4">
              Profile Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <Field label="Full Name"           value={name}    onChange={setName} />
              <Field label="Email Address"        value={userEmail || 'sarah@fintechcorp.com'} disabled type="email" />
              <div className="md:col-span-2">
                <Field label="Company / Organisation" value={company} onChange={setCompany} />
              </div>
            </div>
            <div className="mt-7 flex justify-end">
              <button onClick={handleSave}
                className="bg-primary dark:bg-accent-gold hover:bg-neutral-700 dark:hover:bg-accent-gold-light text-white dark:text-black font-sans font-semibold uppercase tracking-[0.2em] text-xs px-8 py-3 transition-all active:scale-[0.98] cursor-pointer rounded-lg">
                Save Profile
              </button>
            </div>
          </motion.section>

          {/* Preferences */}
          <motion.section variants={cardVar} initial="hidden" animate="visible"
            className="bg-surface dark:bg-[#111111] border border-black/5 dark:border-white/10 p-8 shadow-sm"
          >
            <h2 className="font-sans text-xl font-semibold mb-6 border-b border-black/5 dark:border-white/10 pb-4">
              Application Preferences
            </h2>
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-sans font-semibold text-sm mb-1">Dark Mode</p>
                  <p className="font-sans text-xs text-slate-655 dark:text-zinc-400">Toggle the dark theme.</p>
                </div>
                <ThemeToggle />
              </div>
              <div className="flex items-center justify-between pt-5 border-t border-black/5 dark:border-white/5">
                <div>
                  <p className="font-sans font-semibold text-sm mb-1">Email Notifications</p>
                  <p className="font-sans text-xs text-slate-655 dark:text-zinc-400">Receive alerts when BRD generation is complete.</p>
                </div>
                <button onClick={() => setNotifs(n => !n)}
                  className={`w-12 h-6 rounded-full p-1 transition-colors duration-300 cursor-pointer ${notifications ? 'bg-accent-gold' : 'bg-slate-300 dark:bg-zinc-700'}`}
                >
                  <div className={`w-4 h-4 bg-white rounded-full shadow transition-transform duration-300 ${notifications ? 'translate-x-6' : 'translate-x-0'}`} />
                </button>
              </div>
            </div>
          </motion.section>

          {/* Sign out — no "Danger Zone" heading */}
          <motion.section variants={cardVar} initial="hidden" animate="visible"
            className="bg-surface dark:bg-[#111111] border border-red-100 dark:border-red-900/30 p-8 shadow-sm"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="font-sans font-semibold text-sm mb-1">Sign Out</p>
                <p className="font-sans text-xs text-slate-655 dark:text-zinc-400">Securely end your current session.</p>
              </div>
              <button onClick={handleSignOut}
                className="border border-red-300 dark:border-red-700/50 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 font-sans font-semibold uppercase tracking-widest text-[10px] px-6 py-2 transition-all cursor-pointer active:scale-95 rounded-lg">
                Sign Out
              </button>
            </div>
          </motion.section>

        </div>
      </main>
    </div>
  );
}
