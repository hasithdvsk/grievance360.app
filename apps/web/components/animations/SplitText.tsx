"use client";

import React from "react";
import { motion, Variants } from "framer-motion";

interface SplitTextProps {
  text: string;
  className?: string;
  delay?: number;
  stagger?: number;
}

const letterVariants: Variants = {
  hidden: {
    opacity: 0,
    y: 35,
    rotateX: -80,
    filter: "blur(4px)",
  },
  visible: (custom: number) => ({
    opacity: 1,
    y: 0,
    rotateX: 0,
    filter: "blur(0px)",
    transition: {
      type: "spring",
      damping: 18,
      stiffness: 200,
      delay: custom,
    },
  }),
};

export const SplitText: React.FC<SplitTextProps> = ({
  text,
  className = "",
  delay = 0.05,
  stagger = 0.025,
}) => {
  const words = text.split(" ");

  let charCount = 0;

  return (
    <span className={`inline-block perspective-1000 ${className}`}>
      {words.map((word, wordIdx) => {
        const letters = word.split("");
        const wordStartIdx = charCount;
        charCount += letters.length + 1;

        return (
          <span key={wordIdx} className="inline-block whitespace-nowrap mr-[0.3em]">
            {letters.map((char, charIdx) => {
              const letterIndex = wordStartIdx + charIdx;
              const charDelay = delay + letterIndex * stagger;

              return (
                <motion.span
                  key={charIdx}
                  custom={charDelay}
                  variants={letterVariants}
                  initial="hidden"
                  animate="visible"
                  whileHover={{
                    y: -6,
                    scale: 1.1,
                    transition: { type: "spring", stiffness: 450, damping: 15 },
                  }}
                  className="inline-block transform-gpu will-change-transform select-none cursor-default"
                >
                  {char}
                </motion.span>
              );
            })}
          </span>
        );
      })}
    </span>
  );
};

export default SplitText;
