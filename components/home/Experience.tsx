'use client';

import Image from 'next/image';
import { useState } from 'react';
import { HiChevronDown } from 'react-icons/hi';
import Section, { Reveal } from './Section';
import { experienceData } from '@/lib/experienceData';

const SHOWN = 3;

function bullets(description: string) {
  return description
    .split(/\n\s*\n/)
    .map((b) => b.replace(/^\s*•\s*/, '').trim())
    .filter(Boolean);
}

export default function Experience() {
  return (
    <Section id="experience" kicker="experience" title="Where I've worked">
      <ol className="relative space-y-8 border-l border-line pl-8 sm:pl-10">
        {experienceData.map((job, i) => (
          <Reveal key={job.company + job.role} delay={i * 0.05}>
            <Job job={job} />
          </Reveal>
        ))}
      </ol>
    </Section>
  );
}

function Job({ job }: { job: (typeof experienceData)[number] }) {
  const [open, setOpen] = useState(false);
  const items = bullets(job.description);
  const visible = open ? items : items.slice(0, SHOWN);

  return (
    <li className="relative">
      <span className="absolute -left-[3.05rem] sm:-left-[3.55rem] top-1 flex h-9 w-9 items-center justify-center overflow-hidden rounded-full border border-line bg-white p-1.5">
        <Image src={job.logo} alt="" width={28} height={28} unoptimized className="object-contain" />
      </span>
      <div className="panel p-6 transition hover:border-accent/40">
        <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
          <h3 className="font-display text-xl font-semibold">
            {job.role} <span className="text-accent">· {job.company.replace(' Pvt Ltd', '')}</span>
          </h3>
          <p className="font-mono text-xs text-muted">
            {job.startDateText} – {job.endDateText}
          </p>
        </div>
        <p className="mt-1 font-mono text-xs text-muted">{job.location}</p>
        <ul className="mt-4 space-y-2.5 text-sm leading-relaxed text-muted">
          {visible.map((b) => (
            <li key={b.slice(0, 40)} className="flex gap-3">
              <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-accent" aria-hidden />
              <span>{b}</span>
            </li>
          ))}
        </ul>
        {items.length > SHOWN && (
          <button
            type="button"
            onClick={() => setOpen((o) => !o)}
            aria-expanded={open}
            className="mt-4 inline-flex items-center gap-1 font-mono text-xs text-accent hover:underline"
          >
            {open ? 'Show less' : `Show ${items.length - SHOWN} more`}
            <HiChevronDown className={`transition ${open ? 'rotate-180' : ''}`} aria-hidden />
          </button>
        )}
      </div>
    </li>
  );
}
