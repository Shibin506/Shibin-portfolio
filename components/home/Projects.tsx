'use client';

import { useState } from 'react';
import { FaGithub } from 'react-icons/fa';
import { HiArrowUpRight } from 'react-icons/hi2';
import DemoVideo from './DemoVideo';
import Section, { Reveal } from './Section';
import { projectsData } from '@/lib/projectsData';
import type { Project } from '@/types';

const MORE_SHOWN = 6;

function splitTitle(title: string) {
  const [name, ...rest] = title.split(' — ');
  return { name, subtitle: rest.join(' — ') };
}

export default function Projects() {
  const featured = projectsData.filter((p) => p.featured);
  const others = projectsData.filter((p) => !p.featured);
  const [all, setAll] = useState(false);
  const shownOthers = all ? others : others.slice(0, MORE_SHOWN);

  return (
    <Section id="projects" kicker="projects" title="Things I've built">
      <div className="grid gap-6 md:grid-cols-2">
        {featured.map((p, i) => (
          <Reveal key={p.title} delay={i === 0 ? 0 : ((i - 1) % 2) * 0.08} className={i === 0 ? 'md:col-span-2' : ''}>
            <FeaturedCard project={p} wide={i === 0} />
          </Reveal>
        ))}
      </div>

      <Reveal>
        <h3 className="mt-16 font-display text-xl font-semibold">More projects</h3>
      </Reveal>
      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {shownOthers.map((p, i) => (
          <Reveal key={p.title} delay={(i % 3) * 0.05}>
            <SmallCard project={p} />
          </Reveal>
        ))}
      </div>
      {others.length > MORE_SHOWN && (
        <div className="mt-8 text-center">
          <button type="button" className="btn-ghost" onClick={() => setAll((a) => !a)} aria-expanded={all}>
            {all ? 'Show fewer' : `Show all ${others.length}`}
          </button>
        </div>
      )}
    </Section>
  );
}

function FeaturedCard({ project: p, wide }: { project: Project; wide: boolean }) {
  const { name, subtitle } = splitTitle(p.title);
  return (
    <article
      className={`panel group flex h-full flex-col overflow-hidden transition hover:-translate-y-1 hover:border-accent/50 ${
        wide && p.video ? 'lg:grid lg:grid-cols-[1.15fr_1fr]' : ''
      }`}
    >
      {p.video && (
        <div className={`flex items-center border-b border-line bg-surface2/40 p-3 sm:p-4 ${wide ? 'lg:border-b-0 lg:border-r' : ''}`}>
          <DemoVideo src={p.video} poster={p.videoPoster} label={`${name} demo video`} />
        </div>
      )}
      <div className="flex flex-1 flex-col p-6 sm:p-7">
        <div className="flex items-start justify-between gap-4">
          <div>
            <span className="rounded-full bg-accent/15 px-2.5 py-0.5 font-mono text-[0.68rem] uppercase tracking-wider text-accent">
              Featured
            </span>
            <h3 className="mt-3 font-display text-2xl font-semibold tracking-tight">{name}</h3>
            {subtitle && <p className="mt-1 text-sm text-muted">{subtitle}</p>}
          </div>
          {p.github && (
            <a href={p.github} target="_blank" rel="noopener noreferrer" aria-label={`${name} on GitHub`}
               className="rounded-lg p-2 text-xl text-muted transition hover:text-accent">
              <FaGithub />
            </a>
          )}
        </div>
        <ul className="mt-4 space-y-2.5 text-sm leading-relaxed text-muted">
          {p.description.map((d) => (
            <li key={d.slice(0, 40)} className="flex gap-3">
              <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-accent" aria-hidden />
              <span>{d}</span>
            </li>
          ))}
        </ul>
        <div className="mt-auto flex flex-wrap gap-1.5 pt-5">
          {p.techStack.map((t) => <span key={t} className="chip">{t}</span>)}
        </div>
      </div>
    </article>
  );
}

function SmallCard({ project: p }: { project: Project }) {
  const { name, subtitle } = splitTitle(p.title);
  const body = (
    <article className="panel flex h-full flex-col p-5 transition group-hover:-translate-y-1 group-hover:border-accent/50">
      <div className="flex items-start justify-between gap-3">
        <h4 className="font-display text-lg font-semibold leading-snug">{name}</h4>
        {p.github && <HiArrowUpRight className="mt-1 shrink-0 text-muted transition group-hover:text-accent" aria-hidden />}
      </div>
      {subtitle && <p className="mt-0.5 text-xs text-muted">{subtitle}</p>}
      <p className="mt-3 line-clamp-4 text-sm leading-relaxed text-muted">{p.description[0]}</p>
      <div className="mt-auto flex flex-wrap gap-1.5 pt-4">
        {p.techStack.slice(0, 4).map((t) => <span key={t} className="chip">{t}</span>)}
        {p.techStack.length > 4 && <span className="chip">+{p.techStack.length - 4}</span>}
      </div>
    </article>
  );
  return p.github ? (
    <a href={p.github} target="_blank" rel="noopener noreferrer" className="group block h-full" aria-label={`${name} on GitHub`}>
      {body}
    </a>
  ) : (
    <div className="group h-full">{body}</div>
  );
}
