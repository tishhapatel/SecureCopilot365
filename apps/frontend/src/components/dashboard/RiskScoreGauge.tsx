import React from 'react';

interface GaugeProps {
  score: number;
  label?: string;
}

export default function RiskScoreGauge({ score, label = "Tenant Risk Score" }: GaugeProps) {
  // Gauge math
  const r = 50;
  const c = Math.PI * r; // Half circumference
  const pct = (100 - score) / 100;
  const strokeDashoffset = c * pct;

  // Dynamic colors
  let color = "#00f5d4"; // Low risk (green)
  let glowClass = "shadow-glowGreen";
  if (score >= 80) {
    color = "#ff0055"; // Critical risk (red)
    glowClass = "shadow-glowPurple";
  } else if (score >= 60) {
    color = "#ff7700"; // High risk (orange)
  } else if (score >= 30) {
    color = "#ffcc00"; // Medium risk (yellow)
  }

  return (
    <div className={`flex flex-col items-center justify-center p-4 bg-darkCard border border-darkBorder rounded-2xl transition duration-300 ${score >= 80 ? 'border-cyberPurple/30' : ''}`}>
      <div className="relative w-36 h-20 flex items-end justify-center overflow-hidden">
        <svg className="w-full h-full transform translate-y-3" viewBox="0 0 120 70">
          {/* Background Track */}
          <path
            d="M 10,60 A 50,50 0 0,1 110,60"
            fill="none"
            stroke="#1c2333"
            strokeWidth="10"
            strokeLinecap="round"
          />
          {/* Animated Glow Arc */}
          <path
            d="M 10,60 A 50,50 0 0,1 110,60"
            fill="none"
            stroke={color}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={c}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute flex flex-col items-center bottom-0">
          <span className="text-3xl font-extrabold font-mono tracking-tight text-white">{score}</span>
          <span className="text-[9px] uppercase tracking-wider text-gray-400 font-semibold">{label}</span>
        </div>
      </div>
      <div className="mt-3 text-[10px] text-gray-400 text-center font-medium">
        {score < 30 ? 'Postured Secure' : score < 60 ? 'Enhancements Advised' : 'Immediate Remediation Required'}
      </div>
    </div>
  );
}
