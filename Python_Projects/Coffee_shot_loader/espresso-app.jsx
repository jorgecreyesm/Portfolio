// Espresso Tracker — iOS shot logging screen
// Dark roast theme, amber accents, premium specialty-coffee aesthetic.

const { useState, useMemo } = React;

// ─────────────────────────────────────────────────────────────
// Tweakable defaults (host rewrites this block on disk)
// ─────────────────────────────────────────────────────────────
const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "brand": "Aurora Roasters",
  "brandOptions": ["Aurora Roasters", "Northstar Coffee", "Atlas & Oak", "Hollow Drum", "Verba Coffee Co.", "Daylight Roastery"],
  "bean": "Aurora Yirgacheffe",
  "beansByBrand": {
    "Aurora Roasters": ["Aurora Yirgacheffe", "Sunrise Espresso"],
    "Northstar Coffee": ["Polaris Blend", "True North"],
    "Atlas & Oak": ["Oak House Espresso"],
    "Hollow Drum": ["Drum Roll"],
    "Verba Coffee Co.": ["Verba Single Origin"],
    "Daylight Roastery": ["Sunbeam", "Solstice"]
  },
  "roast": "Medium",
  "origin": "Ethiopia",
  "originOptions": ["Ethiopia", "Colombia", "Kenya", "Brazil", "Costa Rica", "Guatemala", "Panama"],
  "showBeanBar": true,
  "accent": "#d4a574",
  "sweetSpotCenter": 2.25,
  "showSweetSpot": true
}/*EDITMODE-END*/;

const ROAST_OPTIONS = ["Light", "Medium-light", "Medium", "Medium-dark", "Dark"];
const ACCENT_OPTIONS = ["#d4a574", "#e89b5a", "#c87a4a", "#b6845e", "#e8b87a"];

// ─────────────────────────────────────────────────────────────
// Sample shot history (stands in for the Postgres `shots` table
// joined with `beans`). Real app: SELECT … FROM shots JOIN beans …
// ─────────────────────────────────────────────────────────────
const SAMPLE_SHOTS = [
  { id: 12, shot_at: 'Today · 8:42',     brand: 'Aurora Roasters',  bean: 'Aurora Yirgacheffe',  roast: 'Medium',     origin: 'Ethiopia',  dose: 18.0, yield: 36.0, time: 27, grind: '3.5', rating: 4, notes: 'Bright jasmine, syrupy body' },
  { id: 11, shot_at: 'Today · 7:15',     brand: 'Aurora Roasters',  bean: 'Aurora Yirgacheffe',  roast: 'Medium',     origin: 'Ethiopia',  dose: 18.0, yield: 38.5, time: 29, grind: '3.6', rating: 5, notes: 'Perfect — bergamot pop' },
  { id: 10, shot_at: 'Yesterday · 9:20', brand: 'Aurora Roasters',  bean: 'Sunrise Espresso',     roast: 'Medium-dark',origin: 'Brazil',    dose: 18.5, yield: 37.0, time: 26, grind: '3.3', rating: 3, notes: 'Bit ashy on finish' },
  { id:  9, shot_at: 'Yesterday · 8:05', brand: 'Daylight Roastery',bean: 'Sunbeam',              roast: 'Light',      origin: 'Kenya',     dose: 17.5, yield: 35.0, time: 28, grind: '3.7', rating: 4, notes: 'Tart cherry, clean' },
  { id:  8, shot_at: 'Tue · 8:30',       brand: 'Northstar Coffee', bean: 'Polaris Blend',        roast: 'Medium-dark',origin: 'Colombia',  dose: 18.0, yield: 38.0, time: 30, grind: '3.4', rating: 4, notes: 'Cocoa, balanced' },
  { id:  7, shot_at: 'Mon · 7:45',       brand: 'Aurora Roasters',  bean: 'Aurora Yirgacheffe',  roast: 'Medium',     origin: 'Ethiopia',  dose: 18.0, yield: 34.0, time: 24, grind: '3.4', rating: 2, notes: 'Sour — pulled too fast' },
  { id:  6, shot_at: 'Sun · 8:50',       brand: 'Atlas & Oak',      bean: 'Oak House Espresso',   roast: 'Dark',       origin: 'Brazil',    dose: 19.0, yield: 38.0, time: 28, grind: '3.2', rating: 3, notes: 'Smooth, a touch flat' },
  { id:  5, shot_at: 'Sat · 9:10',       brand: 'Verba Coffee Co.', bean: 'Verba Single Origin',  roast: 'Medium',     origin: 'Costa Rica',dose: 18.0, yield: 36.0, time: 27, grind: '3.5', rating: 5, notes: 'Caramel, citrus, gorgeous' },
];

// ─────────────────────────────────────────────────────────────
// CSV export — matches the dashboard.py column order
// ─────────────────────────────────────────────────────────────
function downloadShotsCSV(shots) {
  const headers = ['id','shot_at','brand','bean','roast','origin','dose_g','yield_g','ratio','time_sec','grind_setting','taste_rating','notes'];
  const esc = (v) => {
    if (v == null) return '';
    const s = String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const lines = [
    headers.join(','),
    ...shots.map((s) => {
      const ratio = (s.yield / s.dose).toFixed(2);
      return [s.id, s.shot_at, s.brand, s.bean, s.roast, s.origin,
              s.dose, s.yield, ratio, s.time, s.grind, s.rating, s.notes]
             .map(esc).join(',');
    }),
  ];
  const csv = lines.join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = `shots-${new Date().toISOString().slice(0,10)}.csv`;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// ─────────────────────────────────────────────────────────────
// Palette
// ─────────────────────────────────────────────────────────────
const C = {
  bg:        '#0c0807',
  bg2:       '#120d09',
  surface:   '#1a130d',
  surface2:  '#221911',
  line:      '#2a1f15',
  line2:     '#3a2b1d',
  ink:       '#f5e6d3',
  inkDim:    '#cbb89d',
  muted:     '#8a7864',
  mutedDim:  '#5d4f3f',
  amber:     '#d4a574',
  amberHi:   '#e8b87a',
  amberDim:  '#8a6a44',
  cream:     '#f5e6d3',
  good:      '#7bc48a',
  bad:       '#e08572',
};

// ─────────────────────────────────────────────────────────────
// Brew-ratio status logic
// ─────────────────────────────────────────────────────────────
function ratioStatus(ratio, center = 2.25) {
  const lo = center - 0.25, hi = center + 0.25;
  if (!isFinite(ratio) || ratio <= 0) return { color: C.amberDim, label: '—', sub: 'awaiting input' };
  if (ratio >= lo && ratio <= hi)     return { color: C.good,  label: 'BALANCED',       sub: 'in the pocket' };
  if (ratio >= 1.5 && ratio < lo)     return { color: C.amber, label: 'RISTRETTO',      sub: 'concentrated · syrupy' };
  if (ratio > hi && ratio <= 3.0)     return { color: C.amber, label: 'LUNGO',          sub: 'long · diluted' };
  if (ratio < 1.5)                    return { color: C.bad,   label: 'UNDER-EXTRACTED', sub: 'tighten or pull longer' };
  return                                     { color: C.bad,   label: 'OVER-EXTRACTED',  sub: 'coarser grind' };
}

// ─────────────────────────────────────────────────────────────
// Circular brew-ratio gauge
// ─────────────────────────────────────────────────────────────
function RatioGauge({ ratio, accent = C.amber, showSweetSpot = true, sweetSpotCenter = 2.25 }) {
  const status = ratioStatus(ratio, sweetSpotCenter);
  // override the amber-tier color to the user's accent
  if (status.color === C.amber) status.color = accent;

  // Arc maps ratio 1.0 → 4.0 across 270° (from -135° to +135°)
  const min = 1.0, max = 4.0;
  const pct = Math.max(0, Math.min(1, (ratio - min) / (max - min)));
  const size = 240, r = 96, cx = size / 2, cy = size / 2;
  const arcSweep = 270; // degrees
  const C2pi = 2 * Math.PI * r;
  const visible = C2pi * arcSweep / 360;
  const filled = visible * pct;
  const gap = C2pi - visible;

  // Tick marks every 0.5 ratio across the arc
  const ticks = [];
  for (let v = 1.0; v <= 4.0 + 0.001; v += 0.5) {
    const t = (v - min) / (max - min);
    const ang = (-135 + t * 270) * Math.PI / 180;
    const tx1 = cx + Math.cos(ang) * (r + 10);
    const ty1 = cy + Math.sin(ang) * (r + 10);
    const tx2 = cx + Math.cos(ang) * (r + 16);
    const ty2 = cy + Math.sin(ang) * (r + 16);
    const isMajor = Math.abs(v - Math.round(v)) < 0.01;
    ticks.push(
      <line key={v} x1={tx1} y1={ty1} x2={tx2} y2={ty2}
        stroke={isMajor ? C.amberDim : C.line2}
        strokeWidth={isMajor ? 1.2 : 0.8}
        strokeLinecap="round" />
    );
  }

  // Sweet-spot arc (center ± 0.25) faint behind
  const sweetStart = Math.max(0, ((sweetSpotCenter - 0.25) - min) / (max - min));
  const sweetEnd = Math.min(1, ((sweetSpotCenter + 0.25) - min) / (max - min));
  const sweetVisible = visible * (sweetEnd - sweetStart);
  const sweetOffset = visible * sweetStart;

  const ratioStr = isFinite(ratio) && ratio > 0
    ? `1:${ratio.toFixed(1)}`
    : '1:—';

  return (
    <div style={{
      position: 'relative', width: size, height: size,
      margin: '0 auto',
    }}>
      <svg width={size} height={size} style={{ display: 'block' }}>
        <defs>
          <radialGradient id="gaugeFill" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#1f160e" />
            <stop offset="80%" stopColor="#120d08" />
            <stop offset="100%" stopColor="#0a0705" />
          </radialGradient>
          <linearGradient id="ringGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor={status.color} />
            <stop offset="100%" stopColor={status.color} stopOpacity="0.65" />
          </linearGradient>
        </defs>

        {/* center dish */}
        <circle cx={cx} cy={cy} r={r - 14} fill="url(#gaugeFill)" />
        <circle cx={cx} cy={cy} r={r - 14} fill="none" stroke="#1d150e" strokeWidth="1" />

        {/* ticks */}
        {ticks}

        {/* base track */}
        <circle
          cx={cx} cy={cy} r={r}
          fill="none" stroke={C.line} strokeWidth="3"
          strokeDasharray={`${visible} ${gap}`}
          transform={`rotate(135 ${cx} ${cy})`}
          strokeLinecap="round"
        />

        {/* sweet-spot indicator */}
        {showSweetSpot && (
          <circle
            cx={cx} cy={cy} r={r}
            fill="none" stroke={C.good} strokeOpacity="0.18" strokeWidth="5"
            strokeDasharray={`${sweetVisible} ${C2pi}`}
            strokeDashoffset={-sweetOffset}
            transform={`rotate(135 ${cx} ${cy})`}
            strokeLinecap="butt"
          />
        )}

        {/* filled arc */}
        <circle
          cx={cx} cy={cy} r={r}
          fill="none" stroke="url(#ringGrad)" strokeWidth="3.5"
          strokeDasharray={`${filled} ${C2pi}`}
          transform={`rotate(135 ${cx} ${cy})`}
          strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 0.3s ease, stroke 0.3s ease' }}
        />

        {/* end-cap dot */}
        {pct > 0 && (() => {
          const ang = (-135 + pct * 270) * Math.PI / 180;
          const dx = cx + Math.cos(ang) * r;
          const dy = cy + Math.sin(ang) * r;
          return (
            <g style={{ transition: 'all 0.3s ease' }}>
              <circle cx={dx} cy={dy} r="5" fill={status.color}
                style={{ filter: `drop-shadow(0 0 6px ${status.color})` }} />
              <circle cx={dx} cy={dy} r="2" fill="#0a0705" />
            </g>
          );
        })()}
      </svg>

      {/* HTML overlay — numbers & labels */}
      <div style={{
        position: 'absolute', inset: 0,
        display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        pointerEvents: 'none',
      }}>
        <div style={{
          fontSize: 9.5, letterSpacing: '0.32em', fontWeight: 600,
          color: C.muted, marginBottom: 2,
        }}>BREW RATIO</div>
        <div style={{
          fontFamily: '"Instrument Serif", serif', fontStyle: 'italic',
          fontSize: 58, lineHeight: 1, fontWeight: 400,
          color: status.color, letterSpacing: '-0.02em',
          transition: 'color 0.3s ease',
          textShadow: `0 0 24px ${status.color}33`,
        }}>{ratioStr}</div>
        <div style={{
          marginTop: 8, fontSize: 9, letterSpacing: '0.24em', fontWeight: 600,
          color: status.color,
        }}>{status.label}</div>
        <div style={{
          fontSize: 11, color: C.muted, marginTop: 3,
          fontStyle: 'italic', fontFamily: '"Instrument Serif", serif',
        }}>{status.sub}</div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Stepper input — for dose & yield
// ─────────────────────────────────────────────────────────────
function StepperCard({ label, unit, value, setValue, step = 0.1, min = 0, max = 200, accent = false, decimals = 1 }) {
  const fmt = (n) => Number(n).toFixed(decimals);
  const dec = () => setValue(+fmt(Math.max(min, value - step)));
  const inc = () => setValue(+fmt(Math.min(max, value + step)));
  const [draft, setDraft] = useState(null);
  const display = draft != null ? draft : fmt(value);
  const commit = () => {
    if (draft == null) return;
    const n = parseFloat(draft);
    if (isFinite(n)) setValue(+fmt(Math.max(min, Math.min(max, n))));
    setDraft(null);
  };
  return (
    <div style={{
      flex: 1, background: C.surface,
      border: `1px solid ${C.line}`, borderRadius: 18,
      padding: '14px 14px 12px',
      boxShadow: '0 1px 0 rgba(255,255,255,0.02) inset, 0 8px 20px -12px #000',
    }}>
      <div style={{
        fontSize: 9.5, letterSpacing: '0.22em', fontWeight: 600,
        color: C.muted, marginBottom: 8,
      }}>{label}</div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 4, marginBottom: 10 }}>
        <input
          type="text"
          inputMode="decimal"
          value={display}
          onChange={(e) => setDraft(e.target.value.replace(/[^0-9.]/g, ''))}
          onFocus={(e) => { setDraft(fmt(value)); e.target.select(); }}
          onBlur={commit}
          onKeyDown={(e) => { if (e.key === 'Enter') e.target.blur(); }}
          style={{
            width: '2.6em',
            background: 'transparent', border: 'none', outline: 'none',
            padding: 0, margin: 0,
            fontFamily: '"Instrument Serif", serif',
            fontSize: 36, lineHeight: 1, color: accent ? C.amberHi : C.cream,
            fontWeight: 400, letterSpacing: '-0.01em',
            caretColor: C.amber,
          }}
        />
        <span style={{
          fontSize: 11, color: C.muted, fontFamily: '"JetBrains Mono", monospace',
        }}>{unit}</span>
      </div>
      <div style={{ display: 'flex', gap: 6 }}>
        <StepBtn onClick={dec}>−</StepBtn>
        <StepBtn onClick={inc}>+</StepBtn>
      </div>
    </div>
  );
}

function StepBtn({ children, onClick }) {
  return (
    <button onClick={onClick} style={{
      flex: 1, height: 30, borderRadius: 10,
      background: C.surface2, border: `1px solid ${C.line}`,
      color: C.amber, fontSize: 16, fontWeight: 500,
      fontFamily: 'inherit', cursor: 'pointer',
      transition: 'all 0.1s',
    }}
    onMouseDown={(e) => e.currentTarget.style.background = C.line2}
    onMouseUp={(e) => e.currentTarget.style.background = C.surface2}
    onMouseLeave={(e) => e.currentTarget.style.background = C.surface2}
    >{children}</button>
  );
}

// ─────────────────────────────────────────────────────────────
// Simple "stat" card — for time, grind, temp, pressure
// ─────────────────────────────────────────────────────────────
function StatCard({ label, value, unit, sub }) {
  return (
    <div style={{
      flex: 1, background: C.surface,
      border: `1px solid ${C.line}`, borderRadius: 16,
      padding: '12px 14px',
    }}>
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
        marginBottom: 4,
      }}>
        <span style={{
          fontSize: 9, letterSpacing: '0.22em', fontWeight: 600,
          color: C.muted, textTransform: 'uppercase',
        }}>{label}</span>
        {sub && <span style={{
          fontSize: 9, color: C.mutedDim,
          fontFamily: '"JetBrains Mono", monospace',
        }}>{sub}</span>}
      </div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 4 }}>
        <span style={{
          fontFamily: '"Instrument Serif", serif',
          fontSize: 26, lineHeight: 1.1, color: C.cream,
          letterSpacing: '-0.01em',
        }}>{value}</span>
        <span style={{ fontSize: 11, color: C.muted, fontFamily: '"JetBrains Mono", monospace' }}>{unit}</span>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Star rating row (1–10)
// ─────────────────────────────────────────────────────────────
function StarRating({ value, setValue, max = 5 }) {
  return (
    <div style={{
      background: C.surface, border: `1px solid ${C.line}`,
      borderRadius: 16, padding: '14px 16px',
    }}>
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
        marginBottom: 10,
      }}>
        <span style={{
          fontSize: 9.5, letterSpacing: '0.22em', fontWeight: 600,
          color: C.muted,
        }}>TASTE RATING</span>
        <span style={{
          fontFamily: '"Instrument Serif", serif', fontStyle: 'italic',
          fontSize: 20, color: C.amberHi,
        }}>{value}<span style={{ fontSize: 11, color: C.muted, fontStyle: 'normal', fontFamily: '"JetBrains Mono", monospace' }}> / {max}</span></span>
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
        {Array.from({ length: max }, (_, i) => {
          const on = i < value;
          return (
            <button key={i} onClick={() => setValue(i + 1)} aria-label={`Rate ${i+1}`} style={{
              border: 'none', background: 'transparent', padding: 0,
              cursor: 'pointer', fontSize: 34, lineHeight: 1,
              color: on ? C.amber : C.line2,
              textShadow: on ? `0 0 12px ${C.amber}66` : 'none',
              transition: 'color 0.15s, transform 0.08s',
              fontFamily: '"JetBrains Mono", monospace',
              flex: 1,
            }}
            onMouseDown={(e) => e.currentTarget.style.transform = 'scale(0.85)'}
            onMouseUp={(e) => e.currentTarget.style.transform = 'scale(1)'}
            onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
            >★</button>
          );
        })}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Bean type & brand bar — horizontal chip row above the bean tile
// ─────────────────────────────────────────────────────────────
function BeanChip({ label, value, icon, accent, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      style={{
        display: 'inline-flex', alignItems: 'center', gap: 7,
        padding: '7px 11px 7px 9px',
        background: C.surface, border: `1px solid ${C.line}`,
        borderRadius: 999,
        flexShrink: 0,
        cursor: 'pointer',
        fontFamily: 'inherit',
        transition: 'background 0.12s, border-color 0.12s',
      }}
      onMouseDown={(e) => { e.currentTarget.style.background = C.surface2; e.currentTarget.style.borderColor = C.line2; }}
      onMouseUp={(e)   => { e.currentTarget.style.background = C.surface;  e.currentTarget.style.borderColor = C.line; }}
      onMouseLeave={(e)=> { e.currentTarget.style.background = C.surface;  e.currentTarget.style.borderColor = C.line; }}
    >
      <span style={{
        width: 18, height: 18, borderRadius: '50%',
        background: `linear-gradient(135deg, ${accent}, ${accent}55)`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flexShrink: 0,
      }}>{icon}</span>
      <span style={{ display: 'flex', flexDirection: 'column', lineHeight: 1, alignItems: 'flex-start' }}>
        <span style={{
          fontSize: 7.5, letterSpacing: '0.22em', fontWeight: 600,
          color: C.muted, textTransform: 'uppercase', marginBottom: 2,
        }}>{label}</span>
        <span style={{
          fontSize: 11.5, fontWeight: 500, color: C.cream,
          letterSpacing: '0.01em', whiteSpace: 'nowrap',
        }}>{value}</span>
      </span>
      <svg width="9" height="9" viewBox="0 0 24 24" fill="none" style={{ marginLeft: 2, opacity: 0.5 }}>
        <path d="M7 10l5 5 5-5" stroke={C.muted} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </button>
  );
}

function BeanBar({ brand, bean, roast, origin, accent, onTap }) {
  return (
    <div style={{
      display: 'flex', gap: 7, overflowX: 'auto',
      padding: '0 22px 14px',
      scrollbarWidth: 'none',
    }}>
      <BeanChip label="BRAND" value={brand} accent={accent}
        onClick={() => onTap('brand')}
        icon={
          <svg width="9" height="9" viewBox="0 0 24 24" fill="none">
            <path d="M12 3l2.5 5 5.5 1-4 4 1 5.5L12 16l-5 2.5 1-5.5-4-4 5.5-1z"
              fill="#1a1108" />
          </svg>
        } />
      <BeanChip label="BEAN" value={bean || 'Add bean'} accent={accent}
        onClick={() => onTap('bean')}
        icon={
          <svg width="9" height="11" viewBox="0 0 24 24" fill="none">
            <ellipse cx="12" cy="12" rx="6" ry="9" fill="#1a1108"
              transform="rotate(-25 12 12)" />
            <path d="M9 5 Q12 12 15 19" stroke={accent} strokeWidth="0.9"
              transform="rotate(-25 12 12)" fill="none" strokeLinecap="round" />
          </svg>
        } />
      <BeanChip label="ROAST" value={roast} accent={accent}
        onClick={() => onTap('roast')}
        icon={
          <svg width="9" height="11" viewBox="0 0 24 24" fill="none">
            <ellipse cx="12" cy="12" rx="6" ry="9" fill="#1a1108" />
            <path d="M12 3v18" stroke={accent} strokeWidth="1.2" />
          </svg>
        } />
      <BeanChip label="ORIGIN" value={origin} accent={accent}
        onClick={() => onTap('origin')}
        icon={
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="8" fill="#1a1108" />
            <path d="M4 12h16M12 4c2.5 2 2.5 14 0 16M12 4c-2.5 2-2.5 14 0 16"
              stroke={accent} strokeWidth="0.9" fill="none" />
          </svg>
        } />
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Bottom sheet — mobile-native picker for chip-bar fields
// ─────────────────────────────────────────────────────────────
function BottomSheet({ open, title, onClose, children }) {
  if (!open) return null;
  return (
    <>
      <div onClick={onClose} style={{
        position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.55)',
        zIndex: 200,
      }} />
      <div style={{
        position: 'absolute', left: 0, right: 0, bottom: 0,
        background: `linear-gradient(180deg, ${C.surface} 0%, ${C.bg2} 100%)`,
        borderTop: `1px solid ${C.line2}`,
        borderRadius: '22px 22px 0 0',
        padding: '10px 20px 28px',
        zIndex: 201,
        animation: undefined,
        maxHeight: '72%', overflowY: 'auto',
        boxShadow: '0 -20px 40px -10px rgba(0,0,0,0.7)',
      }}>
        <div style={{
          width: 36, height: 4, borderRadius: 999,
          background: C.line2, margin: '0 auto 14px',
        }} />
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          marginBottom: 16,
        }}>
          <h3 style={{
            margin: 0, fontFamily: '"Instrument Serif", serif', fontWeight: 400,
            fontStyle: 'italic', fontSize: 24, color: C.cream, letterSpacing: '-0.01em',
          }}>{title}</h3>
          <button onClick={onClose} style={{
            width: 30, height: 30, borderRadius: '50%',
            background: C.surface2, border: `1px solid ${C.line2}`,
            color: C.muted, fontSize: 16, cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontFamily: 'inherit',
          }}>×</button>
        </div>
        {children}
      </div>
    </>
  );
}

function PickerList({ options, value, onSelect, onAdd, addPlaceholder }) {
  const [adding, setAdding] = useState(false);
  const [draft, setDraft] = useState('');
  const commitAdd = () => {
    const v = draft.trim();
    if (!v) { setAdding(false); setDraft(''); return; }
    onAdd(v);
    setAdding(false);
    setDraft('');
  };
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      {options.map((opt) => {
        const on = opt === value;
        return (
          <button key={opt} onClick={() => onSelect(opt)} style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            background: on ? C.surface2 : C.surface,
            border: `1px solid ${on ? C.amberDim : C.line}`,
            borderRadius: 12, padding: '12px 14px',
            color: on ? C.cream : C.inkDim,
            fontFamily: 'inherit', fontSize: 14, fontWeight: 500,
            cursor: 'pointer', textAlign: 'left',
            transition: 'all 0.12s',
          }}>
            <span>{opt}</span>
            {on && (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M5 12.5 l5 5 L20 7" stroke={C.amber}
                  strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            )}
          </button>
        );
      })}
      {onAdd && !adding && (
        <button onClick={() => setAdding(true)} style={{
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
          background: 'transparent',
          border: `1px dashed ${C.line2}`,
          borderRadius: 12, padding: '12px 14px',
          color: C.amber, fontFamily: 'inherit', fontSize: 13, fontWeight: 500,
          cursor: 'pointer',
        }}>
          <span style={{ fontSize: 18, lineHeight: '14px' }}>+</span>
          Add new
        </button>
      )}
      {onAdd && adding && (
        <div style={{
          display: 'flex', gap: 6, alignItems: 'center',
          background: C.surface, border: `1px solid ${C.amberDim}`,
          borderRadius: 12, padding: '10px 12px',
        }}>
          <input
            autoFocus
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder={addPlaceholder}
            onKeyDown={(e) => {
              if (e.key === 'Enter') commitAdd();
              if (e.key === 'Escape') { setAdding(false); setDraft(''); }
            }}
            style={{
              flex: 1, background: 'transparent', border: 0, outline: 0,
              color: C.cream, fontFamily: 'inherit', fontSize: 14,
              padding: '4px 0',
            }}
          />
          <button onClick={() => { setAdding(false); setDraft(''); }} style={{
            background: 'transparent', border: 0,
            color: C.muted, fontSize: 18, cursor: 'pointer', padding: '0 4px',
            fontFamily: 'inherit',
          }}>×</button>
          <button onClick={commitAdd} style={{
            background: C.amber, border: 0, color: '#1a1108',
            fontWeight: 600, fontSize: 13, padding: '6px 14px', borderRadius: 8,
            cursor: 'pointer', fontFamily: 'inherit',
          }}>Add</button>
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Coffee bean header tile
// ─────────────────────────────────────────────────────────────
function BeanTile({ bean, brand, roast, onClick }) {
  const empty = !bean;
  return (
    <button
      type="button"
      onClick={onClick}
      style={{
        width: '100%',
        background: `linear-gradient(135deg, ${C.surface2} 0%, ${C.surface} 100%)`,
        border: `1px solid ${C.line2}`, borderRadius: 18,
        padding: '14px 16px',
        display: 'flex', alignItems: 'center', gap: 12,
        cursor: 'pointer', fontFamily: 'inherit',
        textAlign: 'left',
        transition: 'transform 0.08s, border-color 0.12s',
      }}
      onMouseDown={(e) => { e.currentTarget.style.transform = 'scale(0.995)'; }}
      onMouseUp={(e)   => { e.currentTarget.style.transform = 'scale(1)'; }}
      onMouseLeave={(e)=> { e.currentTarget.style.transform = 'scale(1)'; }}
    >
      {/* bean glyph */}
      <div style={{
        width: 42, height: 42, borderRadius: 12,
        background: `linear-gradient(135deg, #3a2715, #1d130b)`,
        border: `1px solid ${C.line2}`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flexShrink: 0,
      }}>
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
          <ellipse cx="12" cy="12" rx="7" ry="10" transform="rotate(-30 12 12)"
            stroke={C.amber} strokeWidth="1.4" fill="none" />
          <path d="M7 7 Q12 12 17 17" stroke={C.amber} strokeWidth="1.4"
            transform="rotate(-30 12 12)" strokeLinecap="round" fill="none" />
        </svg>
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{
          fontSize: 9, letterSpacing: '0.22em', fontWeight: 600,
          color: C.muted, marginBottom: 3,
        }}>BEAN</div>
        <div style={{
          color: empty ? C.muted : C.cream, fontSize: 15, fontWeight: 500,
          fontFamily: 'inherit', fontStyle: empty ? 'italic' : 'normal',
          whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
        }}>{bean || `Tap to add a bean from ${brand}`}</div>
        <div style={{
          fontSize: 11, color: C.muted, marginTop: 2,
          fontFamily: '"JetBrains Mono", monospace',
        }}>{brand} · {roast.toLowerCase()} roast</div>
      </div>
      <div style={{
        width: 28, height: 28, borderRadius: 10,
        background: C.surface2, border: `1px solid ${C.line2}`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        color: C.amber, fontSize: 16, flexShrink: 0,
      }}>›</div>
    </button>
  );
}

// ─────────────────────────────────────────────────────────────
// Main screen
// ─────────────────────────────────────────────────────────────
function LogShotScreen({ t, setTweak, onOpenLog, onShotLogged }) {
  const [dose, setDose] = useState(18.0);
  const [yieldG, setYield] = useState(36.0);
  const [timeSec, setTimeSec] = useState(27);
  const [grind, setGrind] = useState(3.5);
  const [rating, setRating] = useState(4);
  const [bean, setBean] = useState(''); // unused — bean now lives in tweak state (t.bean)
  const [notes, setNotes] = useState('');
  const [logged, setLogged] = useState(false);
  const [saving, setSaving] = useState(false);
  const [sheet, setSheet] = useState(null); // null | 'brand' | 'roast' | 'origin'

  const ratio = useMemo(() => (dose > 0 ? yieldG / dose : 0), [dose, yieldG]);
  const status = ratioStatus(ratio, t.sweetSpotCenter);
  if (status.color === C.amber) status.color = t.accent;

  const today = new Date();
  const dateStr = today.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' });
  const timeStr = today.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });

  return (
    <div style={{
      height: '100%', overflowY: 'auto', overflowX: 'hidden',
      background: `
        radial-gradient(ellipse 130% 80% at 50% 0%, #1f140c 0%, #0c0807 55%, #060403 100%)
      `,
      color: C.ink, paddingBottom: 120,
      WebkitFontSmoothing: 'antialiased',
    }}>
      {/* spacer for status bar */}
      <div style={{ height: 56 }} />

      {/* header */}
      <div style={{ padding: '0 22px', marginBottom: 18 }}>
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
        }}>
          <div>
            <div style={{
              fontSize: 10, letterSpacing: '0.28em', fontWeight: 600,
              color: C.amber, marginBottom: 4,
            }}>NEW ENTRY</div>
            <h1 style={{
              fontFamily: '"Instrument Serif", serif', fontWeight: 400,
              fontSize: 34, lineHeight: 1, margin: 0, letterSpacing: '-0.02em',
              color: C.cream,
            }}>Log <em style={{ color: C.amber }}>Shot</em>.</h1>
            <div style={{
              fontSize: 12, color: C.muted, marginTop: 6,
              fontFamily: '"JetBrains Mono", monospace', letterSpacing: '0.04em',
            }}>{dateStr} · {timeStr}</div>
          </div>
          <button
            onClick={onOpenLog}
            title="View shot log"
            style={{
            width: 38, height: 38, borderRadius: 12,
            background: C.surface, border: `1px solid ${C.line}`,
            color: C.amber, fontSize: 18, cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <rect x="4" y="5" width="16" height="14" rx="2" stroke={C.amber} strokeWidth="1.6" fill="none"/>
              <path d="M7 9h10M7 12h10M7 15h6" stroke={C.amber} strokeWidth="1.6" strokeLinecap="round"/>
            </svg>
          </button>
        </div>
      </div>

      {/* bean type & brand bar */}
      {t.showBeanBar && (
        <BeanBar brand={t.brand} bean={t.bean} roast={t.roast} origin={t.origin} accent={t.accent}
          onTap={(field) => setSheet(field)} />
      )}

      {/* brew ratio gauge */}
      <div style={{ padding: '6px 22px 18px' }}>
        <RatioGauge ratio={ratio} accent={t.accent} showSweetSpot={t.showSweetSpot} sweetSpotCenter={t.sweetSpotCenter} />
      </div>

      {/* bean tile removed — BEAN chip in bar covers this */}

      {/* dose + yield */}
      <div style={{ padding: '0 22px 10px', display: 'flex', gap: 10 }}>
        <StepperCard label="DOSE" unit="g" value={dose} setValue={setDose} accent />
        <StepperCard label="YIELD" unit="g" value={yieldG} setValue={setYield} accent />
      </div>

      {/* time + grind */}
      <div style={{ padding: '0 22px 14px', display: 'flex', gap: 10 }}>
        <StepperCard label="TIME"  unit="s" value={timeSec} setValue={setTimeSec}
          step={1} min={0} max={120} decimals={0} />
        <StepperCard label="GRIND" unit=""  value={grind}   setValue={setGrind}
          step={0.1} min={0} max={50} decimals={1} />
      </div>

      {/* rating */}
      <div style={{ padding: '0 22px 12px' }}>
        <StarRating value={rating} setValue={setRating} />
      </div>

      {/* notes */}
      <div style={{ padding: '0 22px 18px' }}>
        <div style={{
          background: C.surface, border: `1px solid ${C.line}`,
          borderRadius: 16, padding: '12px 14px',
        }}>
          <div style={{
            fontSize: 9.5, letterSpacing: '0.22em', fontWeight: 600,
            color: C.muted, marginBottom: 8,
          }}>TASTING NOTES</div>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Bright bergamot, jasmine on the finish, syrupy body…"
            style={{
              width: '100%', minHeight: 64, resize: 'none',
              background: 'transparent', border: 'none', outline: 'none',
              color: C.cream, fontFamily: 'inherit', fontSize: 13.5,
              lineHeight: 1.5, padding: 0,
              fontStyle: notes ? 'normal' : 'italic',
            }}
          />
        </div>
      </div>

      {/* CTA */}
      <div style={{ padding: '0 22px' }}>
        <button
          onClick={async () => {
            setSaving(true);
            try {
              const res = await fetch('/api/shots', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  brand:         t.brand,
                  bean:          t.bean || t.brand,
                  roast:         t.roast,
                  origin:        t.origin,
                  dose_g:        dose,
                  yield_g:       yieldG,
                  time_sec:      timeSec,
                  grind_setting: String(grind),
                  taste_rating:  rating,
                  notes:         notes.trim() || null,
                }),
              });
              if (res.ok) {
                setLogged(true);
                setNotes('');
                setTimeout(() => setLogged(false), 2200);
                onShotLogged?.();
              }
            } finally {
              setSaving(false);
            }
          }}
          disabled={saving}
          style={{
            width: '100%', height: 56, borderRadius: 18,
            background: `linear-gradient(180deg, ${C.amberHi} 0%, ${C.amber} 100%)`,
            color: '#1a1108', fontSize: 14, fontWeight: 700,
            letterSpacing: '0.16em', border: 'none', cursor: 'pointer',
            fontFamily: 'inherit',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
            boxShadow: `0 10px 28px -10px ${C.amber}90, 0 1px 0 rgba(255,255,255,0.25) inset`,
            transition: 'transform 0.08s',
          }}
          onMouseDown={(e) => e.currentTarget.style.transform = 'scale(0.985)'}
          onMouseUp={(e) => e.currentTarget.style.transform = 'scale(1)'}
          onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
        >
          {!saving && (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M4 9h12a3 3 0 0 1 0 6h-1M4 9v6a4 4 0 0 0 4 4h4a4 4 0 0 0 4-4V9H4z"
                stroke="#1a1108" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M8 3v3M12 3v3" stroke="#1a1108" strokeWidth="1.8" strokeLinecap="round"/>
              <path d="M5 21h12" stroke="#1a1108" strokeWidth="1.8" strokeLinecap="round"/>
            </svg>
          )}
          {saving ? 'SAVING…' : 'LOG SHOT'}
        </button>
      </div>

      {/* Success toast */}
      {logged && (
        <div style={{
          position: 'absolute', left: 22, right: 22, bottom: 48,
          background: 'linear-gradient(180deg, #1c2a1d 0%, #14201a 100%)',
          border: `1px solid #2f4731`, borderRadius: 16,
          padding: '14px 16px',
          display: 'flex', alignItems: 'center', gap: 12,
          boxShadow: '0 18px 40px -12px rgba(0,0,0,0.7)',
          animation: 'rise 0.35s ease-out both',
          zIndex: 100,
        }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: '#2a3f2c', border: '1px solid #3d5a40',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M5 12.5 l5 5 L20 7"
                stroke={C.good} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div>
            <div style={{
              fontFamily: '"Instrument Serif", serif', fontStyle: 'italic',
              fontSize: 18, color: C.cream, lineHeight: 1,
            }}>Shot logged.</div>
            <div style={{
              fontFamily: '"JetBrains Mono", monospace',
              fontSize: 11, color: C.inkDim, marginTop: 4, letterSpacing: '0.04em',
            }}>1:{ratio.toFixed(1)} · {rating}/5 · saved to journal</div>
          </div>
        </div>
      )}

      {/* Bottom sheet pickers — tap a chip to swap brand/roast/origin */}
      <BottomSheet open={sheet === 'brand'} title="Brand" onClose={() => setSheet(null)}>
        <PickerList
          options={t.brandOptions}
          value={t.brand}
          onSelect={(v) => {
            const firstBean = (t.beansByBrand?.[v] || [])[0] || '';
            setTweak({ brand: v, bean: firstBean });
            setSheet(null);
          }}
          onAdd={(v) => {
            const next = t.brandOptions.includes(v) ? t.brandOptions : [...t.brandOptions, v];
            const beansByBrand = t.beansByBrand || {};
            setTweak({
              brandOptions: next,
              brand: v,
              bean: '',
              beansByBrand: beansByBrand[v] ? beansByBrand : { ...beansByBrand, [v]: [] },
            });
            setSheet(null);
          }}
          addPlaceholder="New brand name…"
        />
      </BottomSheet>
      <BottomSheet open={sheet === 'bean'} title={`${t.brand} · beans`} onClose={() => setSheet(null)}>
        <PickerList
          options={t.beansByBrand?.[t.brand] || []}
          value={t.bean}
          onSelect={(v) => { setTweak('bean', v); setSheet(null); }}
          onAdd={(v) => {
            const list = t.beansByBrand?.[t.brand] || [];
            const next = list.includes(v) ? list : [...list, v];
            setTweak({
              beansByBrand: { ...(t.beansByBrand || {}), [t.brand]: next },
              bean: v,
            });
            setSheet(null);
          }}
          addPlaceholder={`New bean for ${t.brand}…`}
        />
      </BottomSheet>
      <BottomSheet open={sheet === 'roast'} title="Roast level" onClose={() => setSheet(null)}>
        <PickerList
          options={["Light", "Medium-light", "Medium", "Medium-dark", "Dark"]}
          value={t.roast}
          onSelect={(v) => { setTweak('roast', v); setSheet(null); }}
        />
      </BottomSheet>
      <BottomSheet open={sheet === 'origin'} title="Origin" onClose={() => setSheet(null)}>
        <PickerList
          options={t.originOptions}
          value={t.origin}
          onSelect={(v) => { setTweak('origin', v); setSheet(null); }}
          onAdd={(v) => {
            const next = t.originOptions.includes(v) ? t.originOptions : [...t.originOptions, v];
            setTweak({ originOptions: next, origin: v });
            setSheet(null);
          }}
          addPlaceholder="New origin country…"
        />
      </BottomSheet>

      <style>{`
        @keyframes rise {
          from { opacity: 0; transform: translateY(12px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        ::-webkit-scrollbar { width: 0; }
        @keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
        @keyframes sheet-up { from { transform: translateY(100%); } to { transform: translateY(0); } }
      `}</style>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// OptionPicker — tap to pick, + Add to type a custom name
// ─────────────────────────────────────────────────────────────
function OptionPicker({ label, value, options, onChange, onOptionsChange, placeholder }) {
  const [adding, setAdding] = useState(false);
  const [draft, setDraft] = useState('');

  // Ensure current value is shown even if not in the options list.
  const allOptions = options.includes(value) ? options : [...options, value];

  const commitAdd = () => {
    const v = draft.trim();
    if (!v) { setAdding(false); setDraft(''); return; }
    if (!options.includes(v)) onOptionsChange([...options, v]);
    onChange(v);
    setAdding(false);
    setDraft('');
  };

  const removeOption = (opt) => {
    const next = options.filter(o => o !== opt);
    onOptionsChange(next);
    if (value === opt && next.length) onChange(next[0]);
  };

  return (
    <div className="twk-row">
      <div className="twk-lbl">
        <span>{label}</span>
        <span className="twk-val" style={{
          maxWidth: 140, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
        }}>{value}</span>
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
        {allOptions.map((opt) => {
          const on = opt === value;
          return (
            <span key={opt} style={{
              display: 'inline-flex', alignItems: 'center',
              background: on ? 'rgba(41,38,27,0.85)' : 'rgba(0,0,0,0.05)',
              color: on ? '#fff' : 'rgba(41,38,27,0.8)',
              borderRadius: 999, padding: '3px 4px 3px 9px',
              fontSize: 11, fontWeight: 500,
              transition: 'background 0.12s',
            }}>
              <button
                type="button"
                onClick={() => onChange(opt)}
                style={{
                  background: 'transparent', border: 0, padding: 0, margin: 0,
                  color: 'inherit', font: 'inherit', cursor: 'default',
                }}
              >{opt}</button>
              {options.length > 1 && (
                <button
                  type="button"
                  onClick={(e) => { e.stopPropagation(); removeOption(opt); }}
                  title="Remove"
                  style={{
                    marginLeft: 4, width: 14, height: 14,
                    background: 'transparent', border: 0, padding: 0,
                    color: on ? 'rgba(255,255,255,0.7)' : 'rgba(41,38,27,0.45)',
                    fontSize: 13, lineHeight: '14px', cursor: 'default',
                    borderRadius: '50%',
                  }}
                >×</button>
              )}
            </span>
          );
        })}
        {!adding && (
          <button
            type="button"
            onClick={() => setAdding(true)}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 3,
              background: 'transparent',
              border: '1px dashed rgba(41,38,27,0.3)',
              color: 'rgba(41,38,27,0.7)',
              borderRadius: 999, padding: '2px 8px',
              font: 'inherit', fontSize: 11, fontWeight: 500,
              cursor: 'default',
            }}
          >+ Add</button>
        )}
        {adding && (
          <span style={{
            display: 'inline-flex', alignItems: 'center', gap: 4,
            background: 'rgba(255,255,255,0.9)',
            border: '.5px solid rgba(0,0,0,0.18)',
            borderRadius: 999, padding: '2px 4px 2px 8px',
          }}>
            <input
              autoFocus
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              placeholder={placeholder}
              onKeyDown={(e) => {
                if (e.key === 'Enter') commitAdd();
                if (e.key === 'Escape') { setAdding(false); setDraft(''); }
              }}
              style={{
                width: 110, border: 0, outline: 0, background: 'transparent',
                font: 'inherit', fontSize: 11, padding: 0,
                color: 'rgba(41,38,27,0.95)',
              }}
            />
            <button type="button" onClick={commitAdd} title="Add"
              style={{
                width: 18, height: 18, borderRadius: '50%',
                background: 'rgba(41,38,27,0.85)', color: '#fff',
                border: 0, padding: 0, fontSize: 11, lineHeight: '18px',
                cursor: 'default',
              }}>✓</button>
            <button type="button" onClick={() => { setAdding(false); setDraft(''); }} title="Cancel"
              style={{
                width: 18, height: 18, borderRadius: '50%',
                background: 'transparent', color: 'rgba(41,38,27,0.55)',
                border: 0, padding: 0, fontSize: 13, lineHeight: '18px',
                cursor: 'default',
              }}>×</button>
          </span>
        )}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Shot Log screen — list view + CSV export
// ─────────────────────────────────────────────────────────────
function ShotLogScreen({ shots, onBack }) {
  const total = shots.length;
  const avgRating = (shots.reduce((a, s) => a + s.rating, 0) / total).toFixed(1);
  const avgRatio = (shots.reduce((a, s) => a + s.yield / s.dose, 0) / total).toFixed(2);

  return (
    <div style={{
      height: '100%', overflowY: 'auto', overflowX: 'hidden',
      background: `radial-gradient(ellipse 130% 80% at 50% 0%, #1f140c 0%, #0c0807 55%, #060403 100%)`,
      color: C.ink, paddingBottom: 60,
    }}>
      <div style={{ height: 56 }} />

      {/* header */}
      <div style={{ padding: '0 22px', marginBottom: 16,
        display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <button onClick={onBack} style={{
          width: 38, height: 38, borderRadius: 12,
          background: C.surface, border: `1px solid ${C.line}`,
          color: C.amber, cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M15 6l-6 6 6 6" stroke={C.amber} strokeWidth="2"
              strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
        <div style={{ textAlign: 'center', flex: 1 }}>
          <div style={{
            fontSize: 10, letterSpacing: '0.28em', fontWeight: 600,
            color: C.amber, marginBottom: 2,
          }}>JOURNAL</div>
          <div style={{
            fontFamily: '"Instrument Serif", serif', fontSize: 22, color: C.cream,
            lineHeight: 1,
          }}>Shot log</div>
        </div>
        <button onClick={() => downloadShotsCSV(shots)} title="Download CSV" style={{
          height: 38, padding: '0 12px', borderRadius: 12,
          background: C.surface, border: `1px solid ${C.amberDim}`,
          color: C.amber, cursor: 'pointer',
          display: 'flex', alignItems: 'center', gap: 5,
          fontFamily: 'inherit', fontSize: 11, fontWeight: 600,
          letterSpacing: '0.1em',
        }}>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
            <path d="M12 4v12m0 0l-4-4m4 4l4-4M5 20h14"
              stroke={C.amber} strokeWidth="2"
              strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          CSV
        </button>
      </div>

      {/* summary strip */}
      <div style={{ padding: '0 22px 14px', display: 'flex', gap: 8 }}>
        <SummaryStat label="SHOTS" value={total} />
        <SummaryStat label="AVG RATIO" value={`1:${avgRatio}`} />
        <SummaryStat label="AVG ★" value={`${avgRating}`} suffix="/5" />
      </div>

      {/* column headers */}
      <div style={{
        padding: '8px 22px', display: 'grid',
        gridTemplateColumns: '50px 1fr 70px 36px',
        gap: 6, alignItems: 'center',
        fontSize: 8.5, letterSpacing: '0.18em', fontWeight: 600,
        color: C.muted, textTransform: 'uppercase',
        borderBottom: `1px solid ${C.line}`,
      }}>
        <span>ID</span><span>BEAN / WHEN</span><span style={{ textAlign: 'right' }}>RATIO · TIME</span><span style={{ textAlign: 'right' }}>★</span>
      </div>

      {/* rows */}
      <div style={{ padding: '0 22px' }}>
        {shots.map((s) => <ShotRow key={s.id} shot={s} />)}
      </div>

      {/* footer note */}
      <div style={{
        padding: '14px 22px 0', textAlign: 'center',
        fontSize: 10.5, color: C.mutedDim,
        fontFamily: '"JetBrains Mono", monospace', letterSpacing: '0.05em',
      }}>{total} shots · tap CSV to export</div>
    </div>
  );
}

function SummaryStat({ label, value, suffix }) {
  return (
    <div style={{
      flex: 1, background: C.surface, border: `1px solid ${C.line}`,
      borderRadius: 12, padding: '8px 10px',
    }}>
      <div style={{
        fontSize: 8.5, letterSpacing: '0.2em', fontWeight: 600,
        color: C.muted, marginBottom: 2,
      }}>{label}</div>
      <div style={{
        fontFamily: '"Instrument Serif", serif', fontSize: 20,
        color: C.cream, lineHeight: 1,
      }}>{value}<span style={{
        fontSize: 10, color: C.muted, fontFamily: '"JetBrains Mono", monospace',
        marginLeft: 2,
      }}>{suffix}</span></div>
    </div>
  );
}

function ShotRow({ shot }) {
  const ratio = (shot.yield / shot.dose).toFixed(1);
  const ratioColor = (() => {
    const r = shot.yield / shot.dose;
    if (r >= 2.0 && r <= 2.5) return C.good;
    if (r < 1.5 || r > 3.0) return C.bad;
    return C.amber;
  })();
  return (
    <div style={{
      padding: '12px 0', borderBottom: `1px solid ${C.line}`,
      display: 'grid', gridTemplateColumns: '50px 1fr 70px 36px',
      gap: 6, alignItems: 'center',
    }}>
      <div style={{
        fontFamily: '"JetBrains Mono", monospace', fontSize: 11,
        color: C.muted,
      }}>#{String(shot.id).padStart(2, '0')}</div>
      <div style={{ minWidth: 0 }}>
        <div style={{
          fontSize: 13, fontWeight: 500, color: C.cream,
          whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
        }}>{shot.bean}</div>
        <div style={{
          fontSize: 10, color: C.muted, marginTop: 2,
          fontFamily: '"JetBrains Mono", monospace',
          whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
        }}>{shot.shot_at} · {shot.dose}→{shot.yield}g</div>
      </div>
      <div style={{ textAlign: 'right' }}>
        <div style={{
          fontFamily: '"Instrument Serif", serif', fontStyle: 'italic',
          fontSize: 16, color: ratioColor, lineHeight: 1,
        }}>1:{ratio}</div>
        <div style={{
          fontSize: 10, color: C.muted, marginTop: 2,
          fontFamily: '"JetBrains Mono", monospace',
        }}>{shot.time}s</div>
      </div>
      <div style={{
        textAlign: 'right', color: C.amber, fontSize: 12,
        fontFamily: '"JetBrains Mono", monospace',
      }}>{'★'.repeat(shot.rating)}<span style={{ color: C.line2 }}>{'★'.repeat(5 - shot.rating)}</span></div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Mount
// ─────────────────────────────────────────────────────────────
const { useEffect } = React;

const isMobile     = window.matchMedia('(max-width: 500px)').matches;
const isStandalone = window.matchMedia('(display-mode: standalone)').matches || !!navigator.standalone;
const isIOS        = /iphone|ipad|ipod/i.test(navigator.userAgent);

function InstallBanner({ onDismiss }) {
  return (
    <div style={{
      position: 'fixed', bottom: 20, left: 16, right: 16, zIndex: 9999,
      background: 'linear-gradient(180deg, #2a1d14 0%, #1a1108 100%)',
      border: '1px solid #d4a574',
      borderRadius: 18, padding: '14px 16px',
      display: 'flex', alignItems: 'center', gap: 12,
      boxShadow: '0 12px 32px rgba(0,0,0,0.6)',
    }}>
      <img src="/icon-192.png" width="40" height="40"
        style={{ borderRadius: 10, flexShrink: 0 }} />
      <div style={{ flex: 1 }}>
        <div style={{
          fontSize: 13, fontWeight: 600, color: '#f5e6d3', marginBottom: 2,
        }}>Install Espresso Tracker</div>
        <div style={{ fontSize: 11, color: '#8a7864' }}>
          {isIOS
            ? 'Tap Share ↑ → Add to Home Screen'
            : 'Tap Install to add to your home screen'}
        </div>
      </div>
      <button onClick={onDismiss} style={{
        background: 'transparent', border: 'none',
        color: '#8a7864', fontSize: 20, cursor: 'pointer',
        padding: '0 4px', lineHeight: 1,
      }}>×</button>
    </div>
  );
}

function App() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);
  const [screen, setScreen] = useState('log'); // 'log' | 'history'
  const [shots, setShots] = useState(SAMPLE_SHOTS);
  const [installPrompt, setInstallPrompt] = useState(null);
  const [showBanner, setShowBanner] = useState(false);

  const fetchShots = () => {
    fetch('/api/shots')
      .then((r) => r.json())
      .then((data) => setShots(data))
      .catch(() => {}); // keep SAMPLE_SHOTS as fallback if API is down
  };

  useEffect(() => {
    fetchShots();
    if (isStandalone) return; // already installed
    // Android: capture the install prompt
    const handler = (e) => { e.preventDefault(); setInstallPrompt(e); setShowBanner(true); };
    window.addEventListener('beforeinstallprompt', handler);
    // iOS: show manual instructions
    if (isIOS) setShowBanner(true);
    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const handleInstall = async () => {
    if (installPrompt) {
      installPrompt.prompt();
      const { outcome } = await installPrompt.userChoice;
      if (outcome === 'accepted') setShowBanner(false);
    } else {
      setShowBanner(false); // iOS — they've read the instructions
    }
  };

  const content = (
    <>
      {screen === 'log'
        ? <LogShotScreen t={t} setTweak={setTweak} onOpenLog={() => setScreen('history')} onShotLogged={fetchShots} />
        : <ShotLogScreen shots={shots} onBack={() => setScreen('log')} />
      }
      {showBanner && isMobile && (
        <InstallBanner onDismiss={handleInstall} />
      )}
    </>
  );

  return (
    <>
      {isMobile
        ? <div style={{ height: '100dvh', overflow: 'hidden', position: 'relative' }}>{content}</div>
        : <IOSDevice width={402} height={874} dark={true}>{content}</IOSDevice>
      }
      <TweaksPanel title="Tweaks">
        <TweakSection label="Bean" />
        <OptionPicker
          label="Brand"
          value={t.brand}
          options={t.brandOptions}
          onChange={(v) => setTweak('brand', v)}
          onOptionsChange={(opts) => setTweak('brandOptions', opts)}
          placeholder="e.g. Sunday Roasters"
        />
        <TweakSelect
          label="Roast"
          value={t.roast}
          options={ROAST_OPTIONS}
          onChange={(v) => setTweak('roast', v)}
        />
        <OptionPicker
          label="Origin"
          value={t.origin}
          options={t.originOptions}
          onChange={(v) => setTweak('origin', v)}
          onOptionsChange={(opts) => setTweak('originOptions', opts)}
          placeholder="e.g. Yemen"
        />
        <TweakToggle label="Show bean bar" value={t.showBeanBar}
          onChange={(v) => setTweak('showBeanBar', v)} />

        <TweakSection label="Appearance" />
        <TweakColor label="Accent color" value={t.accent} options={ACCENT_OPTIONS}
          onChange={(v) => setTweak('accent', v)} />

        <TweakSection label="Brew ratio" />
        <TweakSlider label="Sweet spot center" value={t.sweetSpotCenter}
          min={1.8} max={2.8} step={0.05} unit=":1"
          onChange={(v) => setTweak('sweetSpotCenter', v)} />
        <TweakToggle label="Show sweet-spot ring" value={t.showSweetSpot}
          onChange={(v) => setTweak('showSweetSpot', v)} />
      </TweaksPanel>
    </>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
