"use client";

import React, { useEffect, useState } from "react";
import { motion, useMotionValue, useSpring } from "framer-motion";

export const CustomCursor: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [isTextTarget, setIsTextTarget] = useState(false);
  const [isClicked, setIsClicked] = useState(false);
  const [isScrolling, setIsScrolling] = useState(false);

  // Raw mouse coordinates
  const mouseX = useMotionValue(-100);
  const mouseY = useMotionValue(-100);

  // Inner Dot: Responsive pinpoint tracker
  const dotX = useSpring(mouseX, { damping: 35, stiffness: 850, mass: 0.08 });
  const dotY = useSpring(mouseY, { damping: 35, stiffness: 850, mass: 0.08 });

  // Outer Ring: Spring-damped smooth trailing ring
  const ringX = useSpring(mouseX, { damping: 24, stiffness: 240, mass: 0.4 });
  const ringY = useSpring(mouseY, { damping: 24, stiffness: 240, mass: 0.4 });

  useEffect(() => {
    // Only activate custom cursor on fine pointers (mouse/trackpad)
    if (typeof window === "undefined") return;
    const isTouchDevice = window.matchMedia("(pointer: coarse)").matches;
    if (isTouchDevice) {
      setIsVisible(false);
      return;
    }

    let scrollTimeout: NodeJS.Timeout;

    const handleMouseMove = (e: MouseEvent) => {
      mouseX.set(e.clientX);
      mouseY.set(e.clientY);
      if (!isVisible) setIsVisible(true);
    };

    const handleMouseDown = () => setIsClicked(true);
    const handleMouseUp = () => setIsClicked(false);

    const handleMouseOver = (e: MouseEvent) => {
      const target = e.target as HTMLElement | null;
      if (!target) return;

      const isText = Boolean(
        target.closest('input, textarea, [contenteditable="true"]')
      );
      const interactive = Boolean(
        target.closest(
          'a, button, input, textarea, select, [role="button"], [data-cursor="pointer"], .cursor-pointer'
        )
      );

      setIsTextTarget(isText);
      setIsHovered(interactive);
    };

    const handleMouseLeave = () => setIsVisible(false);
    const handleMouseEnter = () => setIsVisible(true);

    const handleScroll = () => {
      setIsScrolling(true);
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => {
        setIsScrolling(false);
      }, 150);
    };

    window.addEventListener("mousemove", handleMouseMove, { passive: true });
    window.addEventListener("mousedown", handleMouseDown);
    window.addEventListener("mouseup", handleMouseUp);
    window.addEventListener("mouseover", handleMouseOver, { passive: true });
    window.addEventListener("scroll", handleScroll, { passive: true });
    document.documentElement.addEventListener("mouseleave", handleMouseLeave);
    document.documentElement.addEventListener("mouseenter", handleMouseEnter);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mousedown", handleMouseDown);
      window.removeEventListener("mouseup", handleMouseUp);
      window.removeEventListener("mouseover", handleMouseOver);
      window.removeEventListener("scroll", handleScroll);
      document.documentElement.removeEventListener("mouseleave", handleMouseLeave);
      document.documentElement.removeEventListener("mouseenter", handleMouseEnter);
      clearTimeout(scrollTimeout);
    };
  }, [mouseX, mouseY, isVisible]);

  if (!isVisible) return null;

  // Determine compact, non-obtrusive scale dynamics
  let ringScale = 1;
  if (isTextTarget) {
    // Contract slightly over text inputs to maintain high visibility and precision
    ringScale = 0.85;
  } else if (isHovered) {
    // Subtle, clean hover expansion (reduced from bulky 2.2 to comfortable 1.3)
    ringScale = 1.3;
  }

  if (isClicked) {
    ringScale = 0.75;
  }

  return (
    <div className="pointer-events-none fixed inset-0 z-[99999] overflow-hidden select-none">
      {/* Outer Spring-Damped Glassmorphic Trailing Ring (Compact 32px, crystal translucent) */}
      <motion.div
        style={{
          x: ringX,
          y: ringY,
          translateX: "-50%",
          translateY: "-50%",
        }}
        animate={{
          scale: ringScale,
          scaleY: isScrolling ? 1.2 : ringScale,
          scaleX: isScrolling ? 0.8 : ringScale,
          borderColor: isTextTarget
            ? "rgba(255, 255, 255, 0.55)"
            : isHovered
            ? "rgba(255, 255, 255, 0.9)"
            : "rgba(255, 255, 255, 0.28)",
          // Ultra-translucent background so all underlying text/letters remain 100% visible
          backgroundColor: isTextTarget
            ? "rgba(255, 255, 255, 0.02)"
            : isHovered
            ? "rgba(255, 255, 255, 0.08)"
            : "rgba(255, 255, 255, 0.03)",
          boxShadow: isHovered
            ? "0 0 18px 2px rgba(255, 255, 255, 0.35)"
            : "0 0 10px rgba(255, 255, 255, 0.15)",
        }}
        transition={{
          type: "spring",
          stiffness: isClicked ? 650 : 380,
          damping: isClicked ? 18 : 25,
        }}
        className="w-8 h-8 rounded-full border pointer-events-none transition-colors duration-150"
      />

      {/* Inner Dot: Sharp, crisp glowing pure white pointer */}
      <motion.div
        style={{
          x: dotX,
          y: dotY,
          translateX: "-50%",
          translateY: "-50%",
        }}
        animate={{
          scale: isClicked ? 0.7 : isTextTarget ? 0.85 : isHovered ? 1.15 : 1,
          opacity: isVisible ? 1 : 0,
        }}
        transition={{ type: "spring", stiffness: 750, damping: 30 }}
        className="w-1.5 h-1.5 rounded-full bg-white shadow-[0_0_10px_rgba(255,255,255,0.95)] pointer-events-none"
      />
    </div>
  );
};

export default CustomCursor;
