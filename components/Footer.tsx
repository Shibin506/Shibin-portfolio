import { FaGithub, FaLinkedin } from 'react-icons/fa';
import { HiOutlineMail } from 'react-icons/hi';
import { site } from '@/lib/site';

export default function Footer() {
  return (
    <footer className="border-t border-line">
      <div className="mx-auto flex max-w-page flex-col items-center justify-between gap-4 px-5 py-8 text-sm text-muted sm:flex-row sm:px-8">
        <p>
          © {new Date().getFullYear()} {site.name} · built with Next.js & Tailwind
        </p>
        <div className="flex items-center gap-1 text-lg">
          <a href={site.links.github} target="_blank" rel="noopener noreferrer" aria-label="GitHub" className="p-2 hover:text-accent"><FaGithub /></a>
          <a href={site.links.linkedin} target="_blank" rel="noopener noreferrer" aria-label="LinkedIn" className="p-2 hover:text-accent"><FaLinkedin /></a>
          <a href={`mailto:${site.email}`} aria-label="Email" className="p-2 hover:text-accent"><HiOutlineMail /></a>
        </div>
      </div>
    </footer>
  );
}
