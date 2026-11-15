import Image from 'next/image';
import Section, { Reveal } from './Section';
import { educationData } from '@/lib/educationData';

export default function Education() {
  return (
    <Section id="education" kicker="education" title="Education">
      <div className="grid gap-5">
        {educationData.map((e) => (
          <Reveal key={e.institution}>
            <div className="panel flex flex-col gap-5 p-6 sm:flex-row sm:items-start">
              <span className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl border border-line bg-white p-2">
                <Image src={e.logo} alt="" width={44} height={44} unoptimized className="object-contain" />
              </span>
              <div className="flex-1">
                <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
                  <h3 className="font-display text-xl font-semibold">{e.institution}</h3>
                  <p className="font-mono text-xs text-muted">{e.startDateText} – {e.endDateText}</p>
                </div>
                <p className="mt-1 text-muted">{e.degree}</p>
                <p className="mt-1 font-mono text-xs text-muted">{e.location} · {e.grade}</p>
                <div className="mt-4 flex flex-wrap gap-1.5">
                  {e.coursework.map((c) => <span key={c} className="chip">{c}</span>)}
                </div>
              </div>
            </div>
          </Reveal>
        ))}
      </div>
    </Section>
  );
}
