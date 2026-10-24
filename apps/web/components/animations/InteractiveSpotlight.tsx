"use client";

import React, { useRef, useState, useEffect } from "react";
import { motion, useSpring } from "framer-motion";

export const InteractiveSpotlight: React.FC<{ children?: React.ReactNode }> = ({
  children,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);

  // Smooth spring physics for spotlight position
  const mouseX = useSpring(0, { stiffness: 150, damping: 20 });
  const mouseY = useSpring(0, { stiffness: 150, damping: 20 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      mouseX.set(x);
      mouseY.set(y);
    };

    const node = containerRef.current;
    if (node) {
      node.addEventListener("mousemove", handleMouseMove);
      node.addEventListener("mouseenter", () => setIsHovered(true));
      node.addEventListener("mouseleave", () => setIsHovered(false));
    }

    return () => {
      if (node) {
        node.removeEventListener("mousemove", handleMouseMove);
        node.removeEventListener("mouseenter", () => setIsHovered(true));
        node.removeEventListener("mouseleave", () => setIsHovered(false));
      }
    };
  }, [mouseX, mouseY]);

  return (
    <div ref={containerRef} className="relative w-full overflow-hidden">
      {/* Dynamic Cursor Spotlight Beam */}
      <motion.div
        className="pointer-events-none absolute -inset-px transition-opacity duration-500 -z-10"
        style={{
          opacity: isHovered ? 1 : 0.35,
          background: `radial-gradient(600px circle at ${mouseX.get()}px ${mouseY.get()}px, rgba(255, 255, 255, 0.06), transparent 80%)`,
        }}
      />
      {children}
    </div>
  );
};

export default InteractiveSpotlight;
