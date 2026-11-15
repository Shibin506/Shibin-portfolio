'use client';

import Image from 'next/image';
import { motion } from 'framer-motion';
import { FaGithub, FaLinkedin } from 'react-icons/fa';
import { HiOutlineMail, HiArrowRight } from 'react-icons/hi';
import { site } from '@/lib/site';

const rise = (delay: number) => ({
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.55, delay, ease: [0.2, 0.65, 0.3, 0.9] as const },
});

export default function Hero() {
  return (
    <section className="relative overflow-hidden">
      <div className="glow absolute inset-0 -z-10" aria-hidden />
      <div className="dots absolute inset-0 -z-10" aria-hidden />

      <div className="mx-auto grid max-w-page items-center gap-12 px-5 pb-12 pt-28 sm:px-8 sm:pt-36 lg:grid-cols-[1.35fr_1fr] lg:gap-16 lg:pb-16">
        <div>
          <motion.div {...rise(0)} className="mb-7 lg:hidden">
            <Portrait className="h-28 w-24" />
          </motion.div>

          <motion.p {...rise(0.05)} className="inline-flex items-center gap-2 rounded-full border border-line bg-surface/70 px-3 py-1 text-xs text-muted">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-pulse-dot rounded-full bg-ok" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-ok" />
            </span>
            {site.status}
          </motion.p>

          <motion.h1 {...rise(0.12)} className="mt-6 font-display text-[2.6rem] font-semibold leading-[1.02] tracking-tight sm:text-6xl lg:text-7xl">
            {site.name.split(' ').slice(0, 2).join(' ')}
            <br />
            <span className="text-gradient">{site.name.split(' ').slice(2).join(' ')}</span>
          </motion.h1>

          <motion.p {...rise(0.2)} className="mt-5 max-w-xl text-lg text-muted sm:text-xl">
            <span className="text-fg">{site.role}.</span> {site.tagline}
          </motion.p>

          <motion.p {...rise(0.26)} className="mt-4 font-mono text-xs text-muted sm:text-sm">
            prev <span className="text-fg">SWE Intern @ LinkedIn</span> · <span className="text-fg">SWE @ Accenture</span> · MS @ SJSU &rsquo;26
          </motion.p>

          <motion.div {...rise(0.32)} className="mt-8 flex flex-wrap items-center gap-3">
            <a href="#projects" className="btn-solid">
              See my work <HiArrowRight aria-hidden />
            </a>
            <a href={`mailto:${site.email}`} className="btn-ghost">
              <HiOutlineMail aria-hidden /> Get in touch
            </a>
            <div className="ml-1 flex items-center gap-1">
              <IconLink href={site.links.github} label="GitHub"><FaGithub /></IconLink>
              <IconLink href={site.links.linkedin} label="LinkedIn"><FaLinkedin /></IconLink>
            </div>
          </motion.div>

          <motion.dl {...rise(0.4)} className="mt-12 grid max-w-2xl grid-cols-1 gap-3 sm:grid-cols-3">
            {site.stats.map((s) => (
              <div key={s.value} className="panel px-4 py-3">
                <dt className="sr-only">{s.label}</dt>
                <dd className="font-display text-2xl font-semibold tracking-tight">{s.value}</dd>
                <dd className="mt-1 text-xs leading-snug text-muted">
                  {s.label} <span className="font-mono text-accent">· {s.where}</span>
                </dd>
              </div>
            ))}
          </motion.dl>
        </div>

        <motion.div
          initial={{ opacity: 0, scale: 0.96, rotate: 2 }}
          animate={{ opacity: 1, scale: 1, rotate: 0 }}
          transition={{ duration: 0.7, delay: 0.15 }}
          className="hidden justify-self-end lg:block"
        >
          <div className="relative">
            <div className="absolute -inset-3 -z-10 rounded-[2rem] bg-gradient-to-br from-accent/40 via-transparent to-accent2/40 blur-2xl" aria-hidden />
            <Portrait className="h-[26rem] w-[21rem]" />
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function Portrait({ className }: { className: string }) {
  return (
    <div className={`relative overflow-hidden rounded-2xl border border-line bg-white ${className}`}>
      <Image
        src="/profile.jpg"
        alt="Shibin Biji Thomas"
        fill
        priority
        sizes="(max-width: 1024px) 96px, 336px"
        className="object-cover object-top"
      />
    </div>
  );
}

function IconLink({ href, label, children }: { href: string; label: string; children: React.ReactNode }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      aria-label={label}
      className="rounded-lg p-2 text-xl text-muted transition hover:-translate-y-0.5 hover:text-accent"
    >
      {children}
    </a>
  );
}
