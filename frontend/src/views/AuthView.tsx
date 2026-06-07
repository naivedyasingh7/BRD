import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import AmbientCanvas from '../components/AmbientCanvas';
import BrandLogo from '../components/BrandLogo';
import ThemeToggle from '../components/ThemeToggle';
import { useApp } from '../context/AppContext';

function pwStrength(p: string) {
  let s = 0;
  if (p.length >= 8) s++;
  if (/[A-Z]/.test(p)) s++;
  if (/[0-9]/.test(p)) s++;
  if (/[^A-Za-z0-9]/.test(p)) s++;
  return s;
}
const STRENGTH_LABEL = ['', 'Weak', 'Fair', 'Good', 'Strong'];
const STRENGTH_COLOR = ['', 'bg-red-400', 'bg-amber-400', 'bg-lime-400', 'bg-emerald-400'];

// Input styles: dark bg in dark mode, white bg in light mode
const INPUT = `w-full px-3 py-2.5 rounded-lg text-sm transition-all focus:outline-none
  bg-black/10 dark:bg-white/5
  border border-black/15 dark:border-white/10
  text-primary dark:text-white
  placeholder-slate-450 dark:placeholder-white/20
  focus:border-accent-gold/60 focus:bg-white dark:focus:bg-white/8`;

export default function AuthView() {
  const { navigate, isDark, setUserEmail, addToast } = useApp();
  const [isSignIn, setIsSignIn] = useState(true);

  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [showPwd, setShowPwd]   = useState(false);

  const [firstName, setFirstName]     = useState('');
  const [lastName, setLastName]       = useState('');
  const [dob, setDob]                 = useState('');
  const [gender, setGender]           = useState('');
  const [regEmail, setRegEmail]       = useState('');
  const [phone, setPhone]             = useState('');
  const [regPwd, setRegPwd]           = useState('');
  const [confirmPwd, setConfirmPwd]   = useState('');
  const [showRegPwd, setShowRegPwd]   = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [agreed, setAgreed]           = useState(false);

  const [loading, setLoading] = useState(false);
  const [errors, setErrors]   = useState<Record<string, string>>({});

  const strength = pwStrength(isSignIn ? password : regPwd);

  const validateSignIn = () => {
    const e: Record<string, string> = {};
    if (!/\S+@\S+\.\S+/.test(email)) e.email = 'Please enter a valid email address.';
    if (password.length < 6) e.password = 'Password must be at least 6 characters.';
    setErrors(e); return Object.keys(e).length === 0;
  };

  const validateSignUp = () => {
    const e: Record<string, string> = {};
    if (!firstName.trim()) e.firstName = 'Required.';
    if (!/\S+@\S+\.\S+/.test(regEmail)) e.regEmail = 'Enter a valid email.';
    if (regPwd.length < 8) e.regPwd = 'Min. 8 characters.';
    if (regPwd !== confirmPwd) e.confirmPwd = 'Passwords do not match.';
    if (!agreed) e.agreed = 'You must accept the terms.';
    setErrors(e); return Object.keys(e).length === 0;
  };

  const handleSubmit = (ev: React.FormEvent) => {
    ev.preventDefault();
    if (!(isSignIn ? validateSignIn() : validateSignUp())) return;
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setUserEmail(isSignIn ? email : regEmail);
      addToast(isSignIn ? 'Welcome back! Redirecting…' : 'Account created! Welcome to BRD Genie.', 'success');
      navigate('dashboard');
    }, 1400);
  };

  const switchMode = (signIn: boolean) => { setIsSignIn(signIn); setErrors({}); };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-bg-cream dark:bg-black p-4 overflow-auto py-10 transition-colors duration-500">

      {/* Canvas — always visible, adapts to theme */}
      <div className="fixed inset-0 z-0">
        <AmbientCanvas isDark={isDark} />
      </div>

      {/* Light mode gradient wash */}
      {!isDark && (
        <div className="fixed inset-0 z-0 bg-gradient-to-br from-blue-50/80 via-white/60 to-slate-50/80" />
      )}

      {/* Theme toggle */}
      <div className="fixed top-5 right-5 z-30">
        <ThemeToggle />
      </div>

      {/* Card */}
      <motion.div
        initial={{ opacity: 0, y: 24, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        className="relative z-10 w-full max-w-4xl flex rounded-2xl overflow-hidden shadow-2xl shadow-black/10 dark:shadow-black/60"
        style={{ minHeight: '560px' }}
      >
        {/* ── Left branding panel ── */}
        <div className="hidden md:flex w-[38%] shrink-0 flex-col p-10 bg-slate-100 dark:bg-[#111827]/80 backdrop-blur-xl border-r border-black/8 dark:border-white/8">
          <div className="flex-1 flex flex-col items-center justify-center -mt-8">
            <button
              onClick={() => navigate('splash')}
              className="flex flex-col items-center gap-5 hover:opacity-75 transition-opacity"
            >
              <div className="scale-[1.4]">
                <BrandLogo size="xl" />
              </div>
              <span className="font-serif text-3xl font-bold text-primary dark:text-white mt-4">BRD Genie</span>
            </button>
          </div>

          <div className="space-y-3">
            <div className="w-full h-px bg-black/10 dark:bg-white/10" />
            <p className="text-sm text-slate-655 dark:text-white/45 leading-relaxed font-sans text-left">
              AI-powered requirements engineering that turns chaotic conversations into
              audit-ready specifications.
            </p>
            <p className="text-[10px] text-slate-450 dark:text-white/25 font-mono uppercase tracking-widest text-left">
              BRD Genie · Precision for Bharat
            </p>
          </div>
        </div>

        {/* ── Right form panel ── */}
        <div className="flex-1 bg-white dark:bg-[#141b2d]/90 backdrop-blur-xl p-8 md:p-10 flex flex-col justify-center overflow-y-auto">

          {/* Header */}
          <div className="mb-6">
            <h1 className="text-xl font-bold text-primary dark:text-white uppercase tracking-widest">
              {isSignIn ? 'Welcome back.' : 'Register your account'}
            </h1>
          </div>

          {/* Tab toggle */}
          <div className="flex mb-6 border border-black/10 dark:border-white/10 rounded-lg overflow-hidden w-fit">
            {['Sign In', 'Sign Up'].map((label, i) => (
              <button key={label} type="button"
                onClick={() => switchMode(i === 0)}
                className={`px-5 py-2 text-xs font-bold uppercase tracking-widest transition-colors ${
                  isSignIn === (i === 0)
                    ? 'bg-black/8 dark:bg-white/10 text-primary dark:text-white'
                    : 'text-slate-450 dark:text-white/35 hover:text-primary dark:hover:text-white/60'
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          <AnimatePresence mode="wait">
            {isSignIn ? (
              /* ── SIGN IN FORM ── */
              <motion.form key="signin"
                initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 10 }}
                transition={{ duration: 0.2 }}
                onSubmit={handleSubmit} className="space-y-4" noValidate
              >
                <div>
                  <p className="text-[9px] font-bold uppercase tracking-[0.25em] text-slate-450 dark:text-white/30 mb-3">Account Info</p>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-[9px] font-bold uppercase tracking-widest text-slate-655 dark:text-white/40 mb-1">
                        Email Address <span className="text-accent-gold">*</span>
                      </label>
                      <input type="email" value={email}
                        onChange={e => { setEmail(e.target.value); setErrors(p => ({ ...p, email: '' })); }}
                        placeholder="you@company.com" autoComplete="email"
                        className={`${INPUT} ${errors.email ? 'border-red-400' : ''}`}
                      />
                      {errors.email && <p className="text-red-500 text-[10px] mt-1">{errors.email}</p>}
                    </div>
                    <div>
                      <label className="block text-[9px] font-bold uppercase tracking-widest text-slate-655 dark:text-white/40 mb-1">
                        Password <span className="text-accent-gold">*</span>
                      </label>
                      <div className="relative">
                        <input type={showPwd ? 'text' : 'password'} value={password}
                          onChange={e => { setPassword(e.target.value); setErrors(p => ({ ...p, password: '' })); }}
                          placeholder="Min. 6 characters" autoComplete="current-password"
                          className={`${INPUT} pr-10 ${errors.password ? 'border-red-400' : ''}`}
                        />
                        <button type="button" onClick={() => setShowPwd(s => !s)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-450 dark:text-white/30 hover:text-primary dark:hover:text-white/70 cursor-pointer">
                          <span className="material-symbols-outlined text-[17px]">{showPwd ? 'visibility_off' : 'visibility'}</span>
                        </button>
                      </div>
                      {errors.password && <p className="text-red-500 text-[10px] mt-1">{errors.password}</p>}
                    </div>
                  </div>
                </div>

                <div className="flex justify-end">
                  <button type="button" className="text-[11px] text-accent-gold hover:text-accent-gold-dark transition-colors">
                    Forgot password?
                  </button>
                </div>

                <button type="submit" disabled={loading}
                  className="w-full bg-accent-gold hover:bg-accent-gold-light text-white font-bold py-3 rounded-lg text-sm uppercase tracking-widest transition-all flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer shadow-lg active:scale-[0.99]"
                >
                  {loading ? <><span className="material-symbols-outlined animate-spin text-[17px]">progress_activity</span>Authenticating…</> : 'Sign In'}
                </button>

                <div className="relative flex items-center">
                  <div className="flex-1 border-t border-black/8 dark:border-white/8" />
                  <span className="mx-3 text-[9px] text-slate-450 dark:text-white/25 uppercase tracking-widest">or continue with</span>
                  <div className="flex-1 border-t border-black/8 dark:border-white/8" />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  {[
                    { label: 'Google',    logo: 'https://www.svgrepo.com/show/475656/google-color.svg', invert: false },
                    { label: 'Microsoft', logo: 'https://www.svgrepo.com/show/452070/microsoft.svg',    invert: true  },
                  ].map(({ label, logo, invert }) => (
                    <button key={label} type="button"
                      onClick={() => addToast(`${label} SSO is not configured in this demo.`, 'info')}
                      className="flex items-center justify-center gap-2 py-2.5 px-4 bg-black/5 dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-lg hover:bg-black/8 dark:hover:bg-white/10 transition-all text-xs font-semibold text-slate-655 dark:text-white/60 hover:text-primary dark:hover:text-white cursor-pointer"
                    >
                      <img src={logo} alt={label} className={`w-4 h-4 ${invert ? 'dark:invert dark:opacity-60' : ''}`} />
                      {label}
                    </button>
                  ))}
                </div>

                <p className="text-center text-xs text-slate-450 dark:text-white/35">
                  New to BRD Genie?{' '}
                  <button type="button" onClick={() => switchMode(false)}
                    className="text-accent-gold hover:text-accent-gold-dark font-semibold cursor-pointer">
                    Sign up
                  </button>
                </p>
              </motion.form>

            ) : (
              /* ── SIGN UP FORM ── */
              <motion.form key="signup"
                initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.2 }}
                onSubmit={handleSubmit} className="space-y-5" noValidate
              >
                {/* PERSONAL INFO */}
                <div>
                  <p className="text-[9px] font-bold uppercase tracking-[0.25em] text-slate-450 dark:text-white/30 mb-3">Personal Info</p>
                  <div className="grid grid-cols-2 gap-3 mb-3">
                    <div>
                      <label className="block text-[9px] font-bold uppercase tracking-widest text-slate-655 dark:text-white/40 mb-1">
                        First Name <span className="text-accent-gold">*</span>
                      </label>
                      <input type="text" value={firstName} onChange={e => setFirstName(e.target.value)}
                        placeholder="First" className={`${INPUT} ${errors.firstName ? 'border-red-400' : ''}`} />
                      {errors.firstName && <p className="text-red-500 text-[10px] mt-1">{errors.firstName}</p>}
                    </div>
                    <div>
                      <label className="block text-[9px] font-bold uppercase tracking-widest text-slate-655 dark:text-white/40 mb-1">Last Name</label>
                      <input type="text" value={lastName} onChange={e => setLastName(e.target.value)}
                        placeholder="Last" className={INPUT} />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[9px] font-bold uppercase tracking-widest text-slate-655 dark:text-white/40 mb-1">Date of Birth</label>
                      <input type="text" value={dob} onChange={e => setDob(e.target.value)}
                        placeholder="DD/MM/YYYY" className={INPUT} />
                    </div>
                    <div>
                      <label className="block text-[9px] font-bold uppercase tracking-widest text-slate-655 dark:text-white/40 mb-1">Gender</label>
                      <select value={gender} onChange={e => setGender(e.target.value)}
                        className={`${INPUT} cursor-pointer appearance-none`}>
                        <option value="">Select</option>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                        <option value="other">Other</option>
                        <option value="prefer_not">Prefer not to say</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* CONTACT DETAILS */}
                <div>
                  <p className="text-[9px] font-bold uppercase tracking-[0.25em] text-slate-450 dark:text-white/30 mb-3">Contact Details</p>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-[9px] font-bold uppercase tracking-widest text-slate-655 dark:text-white/40 mb-1">
                        Email Address <span className="text-accent-gold">*</span>
                      </label>
                      <input type="email" value={regEmail} onChange={e => setRegEmail(e.target.value)}
                        placeholder="you@company.com" autoComplete="email"
                        className={`${INPUT} ${errors.regEmail ? 'border-red-400' : ''}`} />
                      {errors.regEmail && <p className="text-red-500 text-[10px] mt-1">{errors.regEmail}</p>}
                    </div>
                    <div>
                      <label className="block text-[9px] font-bold uppercase tracking-widest text-slate-655 dark:text-white/40 mb-1">Phone Number</label>
                      <div className="flex gap-2">
                        <div className="flex items-center gap-1.5 px-3 py-2.5 bg-black/5 dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-lg text-sm text-slate-655 dark:text-white/70 shrink-0">
                          <span className="text-sm">🇮🇳</span>
                          <span className="text-xs">+91</span>
                        </div>
                        <input type="tel" value={phone} onChange={e => setPhone(e.target.value)}
                          placeholder="98765 43210" className={`${INPUT} flex-1`} />
                      </div>
                    </div>
                  </div>
                </div>

                {/* SECURITY */}
                <div>
                  <p className="text-[9px] font-bold uppercase tracking-[0.25em] text-slate-450 dark:text-white/30 mb-3">Security</p>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[9px] font-bold uppercase tracking-widest text-slate-655 dark:text-white/40 mb-1">
                        Password <span className="text-accent-gold">*</span>
                      </label>
                      <div className="relative">
                        <input type={showRegPwd ? 'text' : 'password'} value={regPwd}
                          onChange={e => setRegPwd(e.target.value)}
                          placeholder="Min. 8 characters" autoComplete="new-password"
                          className={`${INPUT} pr-9 ${errors.regPwd ? 'border-red-400' : ''}`} />
                        <button type="button" onClick={() => setShowRegPwd(s => !s)}
                          className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-450 dark:text-white/30 hover:text-primary dark:hover:text-white/70 cursor-pointer">
                          <span className="material-symbols-outlined text-[15px]">{showRegPwd ? 'visibility_off' : 'visibility'}</span>
                        </button>
                      </div>
                      {errors.regPwd && <p className="text-red-500 text-[10px] mt-1">{errors.regPwd}</p>}
                      {regPwd.length > 0 && (
                        <div className="flex gap-1 h-1 mt-2 rounded-full overflow-hidden bg-black/8 dark:bg-white/5">
                          {[1,2,3,4].map(l => (
                            <div key={l} className={`flex-1 h-full rounded-full transition-colors ${strength >= l ? STRENGTH_COLOR[strength] : ''}`} />
                          ))}
                        </div>
                      )}
                    </div>
                    <div>
                      <label className="block text-[9px] font-bold uppercase tracking-widest text-slate-655 dark:text-white/40 mb-1">
                        Confirm Password <span className="text-accent-gold">*</span>
                      </label>
                      <div className="relative">
                        <input type={showConfirm ? 'text' : 'password'} value={confirmPwd}
                          onChange={e => setConfirmPwd(e.target.value)}
                          placeholder="Re-enter password" autoComplete="new-password"
                          className={`${INPUT} pr-9 ${errors.confirmPwd ? 'border-red-400' : ''}`} />
                        <button type="button" onClick={() => setShowConfirm(s => !s)}
                          className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-450 dark:text-white/30 hover:text-primary dark:hover:text-white/70 cursor-pointer">
                          <span className="material-symbols-outlined text-[15px]">{showConfirm ? 'visibility_off' : 'visibility'}</span>
                        </button>
                      </div>
                      {errors.confirmPwd && <p className="text-red-500 text-[10px] mt-1">{errors.confirmPwd}</p>}
                    </div>
                  </div>
                </div>

                {/* Terms */}
                <div>
                  <label className="flex items-start gap-3 cursor-pointer">
                    <input type="checkbox" checked={agreed} onChange={e => setAgreed(e.target.checked)}
                      className="mt-0.5 w-4 h-4 rounded border-black/20 dark:border-white/20 bg-black/5 dark:bg-white/5 accent-accent-gold cursor-pointer shrink-0" />
                    <span className="text-xs text-slate-655 dark:text-white/45 leading-relaxed">
                      I accept the{' '}
                      <button type="button" className="text-accent-gold hover:underline">Terms of Service</button>
                      {' '}and{' '}
                      <button type="button" className="text-accent-gold hover:underline">Privacy Policy</button>
                    </span>
                  </label>
                  {errors.agreed && <p className="text-red-500 text-[10px] mt-1">{errors.agreed}</p>}
                </div>

                <button type="submit" disabled={loading}
                  className="w-full bg-accent-gold hover:bg-accent-gold-light text-white font-bold py-3 rounded-lg text-sm uppercase tracking-widest transition-all flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer shadow-lg active:scale-[0.99]"
                >
                  {loading ? <><span className="material-symbols-outlined animate-spin text-[17px]">progress_activity</span>Creating workspace…</> : 'Register Account'}
                </button>

                <p className="text-center text-xs text-slate-450 dark:text-white/35">
                  Already registered?{' '}
                  <button type="button" onClick={() => switchMode(true)}
                    className="text-accent-gold hover:text-accent-gold-dark font-semibold cursor-pointer">
                    ← Sign in
                  </button>
                </p>
              </motion.form>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  );
}
