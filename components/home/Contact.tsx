import Link from 'next/link';
import { FaGithub, FaLinkedin } from 'react-icons/fa';
import { HiOutlineMail } from 'react-icons/hi';
import Section, { Reveal } from './Section';
import { site } from '@/lib/site';

export default function Contact() {
  return (
    <Section id="contact" kicker="contact" title="Let's talk">
      <Reveal>
        <div className="panel relative overflow-hidden p-8 sm:p-12">
          <div className="glow absolute inset-0 -z-10 opacity-80" aria-hidden />
          <p className="max-w-2xl text-lg text-muted">
            I&apos;m graduating in December 2026 and looking for{' '}
            <span className="text-fg">new-grad software engineering roles</span>. If you&apos;re hiring, or just
            want to talk about something I&apos;ve built, my inbox is open.
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <a href={`mailto:${site.email}`} className="btn-solid text-base">
              <HiOutlineMail aria-hidden /> {site.email}
            </a>
            <Link href="/contact" className="btn-ghost">Send a message</Link>
            <a href={site.links.linkedin} target="_blank" rel="noopener noreferrer" className="btn-ghost">
              <FaLinkedin aria-hidden /> LinkedIn
            </a>
            <a href={site.links.github} target="_blank" rel="noopener noreferrer" className="btn-ghost">
              <FaGithub aria-hidden /> GitHub
            </a>
          </div>
        </div>
      </Reveal>
    </Section>
  );
}
