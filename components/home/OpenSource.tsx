import { FaGithub, FaStar } from 'react-icons/fa';
import { HiArrowUpRight } from 'react-icons/hi2';
import Section, { Reveal } from './Section';
import { openSourceContributions, openSourceProject } from '@/lib/openSourceData';

export default function OpenSource() {
  const p = openSourceProject;
  return (
    <Section id="open-source" kicker="open source" title="Contributing upstream">
      <Reveal>
        <div className="panel p-6 sm:p-8">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <a href={p.url} target="_blank" rel="noopener noreferrer" className="group inline-flex items-center gap-2 font-display text-2xl font-semibold">
              <FaGithub aria-hidden /> {p.name}
              <HiArrowUpRight className="text-base text-muted transition group-hover:text-accent" aria-hidden />
            </a>
            <span className="inline-flex items-center gap-1.5 rounded-full border border-line px-3 py-1 font-mono text-xs text-muted">
              <FaStar className="text-accent" aria-hidden /> {p.stars} stars
            </span>
          </div>
          <p className="mt-3 max-w-3xl text-muted">{p.summary}</p>

          <ul className="mt-6 grid gap-4 md:grid-cols-2">
            {openSourceContributions.map((c) => (
              <li key={c.prNumber} className="rounded-xl border border-line bg-surface2/50 p-5">
                <div className="flex items-center justify-between gap-3">
                  <a href={c.url} target="_blank" rel="noopener noreferrer" className="font-mono text-xs text-muted hover:text-accent">
                    PR #{c.prNumber}
                  </a>
                  <span
                    className={`rounded-full px-2.5 py-0.5 font-mono text-[0.7rem] ${
                      c.status === 'Merged' ? 'bg-ok/15 text-ok' : 'bg-accent/15 text-accent'
                    }`}
                  >
                    {c.status}
                  </span>
                </div>
                <h3 className="mt-2 font-semibold leading-snug">{c.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted">{c.description[0]}</p>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {c.techStack.map((t) => <span key={t} className="chip">{t}</span>)}
                </div>
              </li>
            ))}
          </ul>
        </div>
      </Reveal>
    </Section>
  );
}
