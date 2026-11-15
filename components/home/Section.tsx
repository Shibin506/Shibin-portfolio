'use client';

import { motion } from 'framer-motion';

export function Reveal({ children, delay = 0, className }: {
  children: React.ReactNode;
  delay?: number;
  className?: string;
}) {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y: 18 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.5, delay, ease: [0.2, 0.65, 0.3, 0.9] }}
    >
      {children}
    </motion.div>
  );
}

export default function Section({ id, kicker, title, children }: {
  id: string;
  kicker: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section id={id} aria-labelledby={`${id}-title`} className="mx-auto w-full max-w-page px-5 sm:px-8 py-16 sm:py-20">
      <Reveal>
        <p className="kicker">/ {kicker}</p>
        <h2 id={`${id}-title`} className="mt-3 font-display text-3xl sm:text-4xl font-semibold tracking-tight">
          {title}
        </h2>
      </Reveal>
      <div className="mt-10">{children}</div>
    </section>
  );
}
