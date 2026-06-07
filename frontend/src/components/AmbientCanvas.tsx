import React, { useEffect, useRef } from 'react';

interface Orb { x:number; y:number; r:number; vx:number; vy:number; rgb:string; a:number; }
interface Star { x:number; y:number; r:number; vx:number; vy:number; a:number; rgb:string; }

export default function AmbientCanvas({ isDark = false }: { isDark?: boolean }) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current; if (!canvas) return;
    const ctx = canvas.getContext('2d')!;
    let raf: number, orbs: Orb[] = [], stars: Star[] = [];

    const resize = () => {
      canvas.width  = canvas.parentElement?.clientWidth  ?? window.innerWidth;
      canvas.height = canvas.parentElement?.clientHeight ?? window.innerHeight;
      init();
    };

    const init = () => {
      const W = canvas.width, H = canvas.height, S = Math.min(W, H);
      // Subtle blue-only ambient blobs — no purple, no gold
      orbs = [
        { x:W*0.20, y:H*0.25, r:S*0.55, vx:0.05,  vy:0.04,  rgb: isDark?'96,184,240':'96,184,240',  a: isDark?0.06:0.07 },
        { x:W*0.80, y:H*0.70, r:S*0.50, vx:-0.04, vy:-0.05, rgb: isDark?'96,184,240':'137,207,245', a: isDark?0.04:0.04 },
        { x:W*0.50, y:H*0.50, r:S*0.40, vx:-0.05, vy:0.04,  rgb: isDark?'96,184,240':'96,184,240',  a: isDark?0.03:0.04 },
        { x:W*0.75, y:H*0.20, r:S*0.30, vx:0.06,  vy:0.07,  rgb: isDark?'255,255,255':'26,26,26',    a: isDark?0.015:0.02 },
      ];
      // Constellation stars
      const n = Math.min(60, Math.floor((W * H) / 20000));
      stars = Array.from({ length: n }, () => {
        const isBlue = Math.random() > 0.3;
        return {
          x: Math.random() * W, y: Math.random() * H,
          r: Math.random() * 1.4 + 0.4,
          vx: (Math.random()-0.5) * 0.15, vy: (Math.random()-0.5) * 0.15,
          rgb: isBlue ? '96,184,240' : (isDark ? '255,255,255' : '30,100,200'),
          a: isBlue ? (isDark ? 0.35 : 0.28) : (isDark ? 0.12 : 0.15),
        };
      });
    };

    const draw = () => {
      const W = canvas.width, H = canvas.height;
      ctx.clearRect(0, 0, W, H);

      // Draw orbs
      for (const o of orbs) {
        o.x += o.vx; o.y += o.vy;
        if (o.x < -o.r/2 || o.x > W+o.r/2) o.vx *= -1;
        if (o.y < -o.r/2 || o.y > H+o.r/2) o.vy *= -1;
        const g = ctx.createRadialGradient(o.x, o.y, 0, o.x, o.y, o.r);
        g.addColorStop(0,    `rgba(${o.rgb},${o.a})`);
        g.addColorStop(0.45, `rgba(${o.rgb},${o.a*0.4})`);
        g.addColorStop(1,    `rgba(${o.rgb},0)`);
        ctx.fillStyle = g;
        ctx.beginPath(); ctx.arc(o.x, o.y, o.r, 0, Math.PI*2); ctx.fill();
      }

      // Draw stars + connections
      for (let i = 0; i < stars.length; i++) {
        const s = stars[i];
        s.x += s.vx; s.y += s.vy;
        if (s.x < 0) s.x = W; if (s.x > W) s.x = 0;
        if (s.y < 0) s.y = H; if (s.y > H) s.y = 0;

        // Star dot with soft glow
        const sg = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, s.r * 3);
        sg.addColorStop(0, `rgba(${s.rgb},${s.a})`);
        sg.addColorStop(1, `rgba(${s.rgb},0)`);
        ctx.fillStyle = sg;
        ctx.beginPath(); ctx.arc(s.x, s.y, s.r * 3, 0, Math.PI*2); ctx.fill();

        ctx.beginPath(); ctx.arc(s.x, s.y, s.r, 0, Math.PI*2);
        ctx.fillStyle = `rgba(${s.rgb},${s.a * 1.5})`; ctx.fill();

        // Connect nearby stars
        for (let j = i+1; j < stars.length; j++) {
          const t = stars[j];
          const d = Math.hypot(s.x-t.x, s.y-t.y);
          if (d < 100) {
            ctx.beginPath(); ctx.moveTo(s.x, s.y); ctx.lineTo(t.x, t.y);
            const lineAlpha = isDark ? 0.07 : 0.06;
            ctx.strokeStyle = `rgba(${isDark?'255,255,255':'96,184,240'},${lineAlpha*(1-d/100)})`;
            ctx.lineWidth = 0.4; ctx.stroke();
          }
        }
      }
      raf = requestAnimationFrame(draw);
    };

    const onVisibility = () => {
      if (document.hidden) cancelAnimationFrame(raf);
      else { raf = requestAnimationFrame(draw); }
    };

    window.addEventListener('resize', resize);
    document.addEventListener('visibilitychange', onVisibility);
    resize(); draw();
    return () => {
      window.removeEventListener('resize', resize);
      document.removeEventListener('visibilitychange', onVisibility);
      cancelAnimationFrame(raf);
    };
  }, [isDark]);

  return <canvas ref={ref} className="absolute inset-0 w-full h-full pointer-events-none" />;
}
