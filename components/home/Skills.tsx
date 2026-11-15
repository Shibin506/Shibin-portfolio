import Section, { Reveal } from './Section';
import { skillsData } from '@/lib/skillsData';

const LABELS: Record<string, string> = {
  Languages: 'Languages',
  Frameworks: 'Frameworks & APIs',
  Database: 'Databases & Cloud',
  'AI/ML': 'AI & LLMs',
  DevOps: 'DevOps & Testing',
  Others: 'Data & Distributed Systems',
};

export default function Skills() {
  const groups = Object.keys(LABELS)
    .map((cat) => ({
      label: LABELS[cat],
      skills: skillsData.filter((s) => s.category === cat).sort((a, b) => a.order - b.order),
    }))
    .filter((g) => g.skills.length);

  return (
    <Section id="skills" kicker="skills" title="Tools I reach for">
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {groups.map((g, i) => (
          <Reveal key={g.label} delay={(i % 3) * 0.06}>
            <div className="panel h-full p-5">
              <div className="flex items-baseline justify-between">
                <h3 className="font-semibold">{g.label}</h3>
                <span className="font-mono text-xs text-muted">{String(g.skills.length).padStart(2, '0')}</span>
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                {g.skills.map((s) => (
                  <span key={s.skill} className="rounded-lg border border-line bg-surface2/60 px-2.5 py-1 text-sm transition hover:border-accent/50 hover:text-accent">
                    {s.skill}
                  </span>
                ))}
              </div>
            </div>
          </Reveal>
        ))}
      </div>
    </Section>
  );
}
