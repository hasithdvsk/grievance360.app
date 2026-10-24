"use client";

import React, { useEffect, useState, useRef } from "react";

interface CountingNumberProps {
  value: string; // e.g. "14,892", "16.2 hrs", "< 12 hrs", "97.4%"
  className?: string;
  durationMs?: number;
}

export const CountingNumber: React.FC<CountingNumberProps> = ({
  value,
  className = "",
  durationMs = 1600,
}) => {
  // Extract numeric portion and prefixes/suffixes
  // e.g. "14,892" -> num: 14892, suffix: ""
  // "16.2 hrs" -> num: 16.2, suffix: " hrs"
  // "< 12 hrs" -> prefix: "< ", num: 12, suffix: " hrs"
  // "97.4%" -> num: 97.4, suffix: "%"
  const match = value.match(/^([^0-9.]*)([0-9,.]+)(.*)$/);
  const prefix = match ? match[1] : "";
  const rawNumStr = match ? match[2].replace(/,/g, "") : "0";
  const suffix = match ? match[3] : "";
  const targetNum = parseFloat(rawNumStr) || 0;
  const isDecimal = rawNumStr.includes(".");
  const decimalPlaces = isDecimal ? rawNumStr.split(".")[1].length : 0;
  const hasCommas = match ? match[2].includes(",") : false;

  const [currentVal, setCurrentVal] = useState(0);
  const elementRef = useRef<HTMLSpanElement>(null);
  const hasAnimated = useRef(false);

  useEffect(() => {
    if (hasAnimated.current) return;

    let startTimestamp: number | null = null;
    let animFrame: number;

    const step = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / durationMs, 1);
      // Ease out cubic
      const easeProgress = 1 - Math.pow(1 - progress, 3);
      const val = easeProgress * targetNum;
      setCurrentVal(val);

      if (progress < 1) {
        animFrame = requestAnimationFrame(step);
      } else {
        setCurrentVal(targetNum);
        hasAnimated.current = true;
      }
    };

    animFrame = requestAnimationFrame(step);

    return () => cancelAnimationFrame(animFrame);
  }, [durationMs, targetNum]);

  const formattedNum = isDecimal
    ? currentVal.toFixed(decimalPlaces)
    : Math.floor(currentVal).toString();

  const withCommas = hasCommas
    ? formattedNum.replace(/\B(?=(\d{3})+(?!\d))/g, ",")
    : formattedNum;

  return (
    <span ref={elementRef} className={`font-mono font-extrabold ${className}`}>
      {prefix}
      {withCommas}
      {suffix}
    </span>
  );
};

export default CountingNumber;
