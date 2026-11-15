import Section, { Reveal } from './Section';
import { site } from '@/lib/site';

const focus = [
  'Backend & distributed systems',
  'Cloud infrastructure (AWS, GCP)',
  'LLM apps, RAG & evaluation',
  'Storage engines & developer tools',
];

export default function About() {
  return (
    <Section id="about" kicker="about" title="A bit about me">
      <div className="grid gap-10 lg:grid-cols-[1.6fr_1fr]">
        <Reveal className="space-y-4 text-[1.05rem] leading-relaxed text-muted">
          {site.about.map((p) => (
            <p key={p.slice(0, 24)}>{p}</p>
          ))}
        </Reveal>
        <Reveal delay={0.1}>
          <div className="panel p-6">
            <p className="kicker">what I work on</p>
            <ul className="mt-4 space-y-3">
              {focus.map((f) => (
                <li key={f} className="flex items-start gap-3 text-sm">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" aria-hidden />
                  {f}
                </li>
              ))}
            </ul>
          </div>
        </Reveal>
      </div>
    </Section>
  );
}
