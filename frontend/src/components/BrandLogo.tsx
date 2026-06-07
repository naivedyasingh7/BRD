import React from 'react';
import { motion } from 'motion/react';

type Size = 'xs'|'sm'|'md'|'lg'|'xl';
const SIZES: Record<Size,string> = { xs:'w-5 h-5', sm:'w-8 h-8', md:'w-11 h-11', lg:'w-20 h-20', xl:'w-36 h-36 md:w-44 md:h-44' };

const pV = {
  hidden:  { pathLength:0, opacity:0 },
  visible: (d:number) => ({
    pathLength:1, opacity:1,
    transition:{ pathLength:{ delay:d*0.26, type:'spring' as const, duration:1.5, bounce:0 }, opacity:{ delay:d*0.26, duration:0.3 } }
  }),
};
const fV = {
  hidden:  { scale:0, opacity:0 },
  visible: (d:number) => ({ scale:1, opacity:1, transition:{ delay:d*0.26, type:'spring' as const, stiffness:100, damping:14 } }),
};

export default function BrandLogo({ size='md', animate=false, className='' }: { size?:Size; animate?:boolean; className?:string }) {
  const P = animate ? motion.path : 'path' as any;
  const R = animate ? motion.rect : 'rect' as any;
  const pp = (d:number) => animate ? { variants:pV, initial:'hidden', animate:'visible', custom:d } : {};
  const rp = (d:number) => animate ? { variants:fV, initial:'hidden', animate:'visible', custom:d } : {};

  return (
    <div className={`inline-flex items-center justify-center ${SIZES[size]} ${className}`}>
      <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
        {/* Outer ambient arc — gold */}
        <P d="M 112 42 A 75 75 0 1 1 176 100" stroke="var(--color-accent-gold)" strokeWidth="13" strokeLinecap="round" opacity="0.9" {...pp(0)} />
        {/* Main G-helix body — charcoal/white */}
        <P d="M 152 100 A 52 52 0 1 0 100 152 L 144 152 A 12 12 0 0 0 156 140 L 156 132" stroke="var(--color-primary)" strokeWidth="15" strokeLinecap="round" strokeLinejoin="round" {...pp(1.0)} />
        {/* Inner arc */}
        <P d="M 128 85 A 32 32 0 1 0 100 132 L 115 132" stroke="var(--color-primary)" strokeWidth="11" strokeLinecap="round" strokeLinejoin="round" {...pp(1.8)} />
        {/* Gold pill */}
        <R x="105" y="84" width="42" height="14" rx="7" fill="var(--color-accent-gold)" {...rp(2.6)} />
        {/* Primary pill */}
        <R x="105" y="108" width="30" height="14" rx="7" fill="var(--color-primary)" {...rp(3.0)} />
      </svg>
    </div>
  );
}
