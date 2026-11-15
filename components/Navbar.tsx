'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTheme } from 'next-themes';
import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { HiOutlineMenuAlt3, HiX } from 'react-icons/hi';
import { HiOutlineMoon, HiOutlineSun } from 'react-icons/hi2';
import { sections } from '@/lib/site';

export default function Navbar() {
  const pathname = usePathname();
  const onHome = pathname === '/';
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState<string | null>(null);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => setMounted(true), []);

  useEffect(() => {
    const onScroll = () => {
      setScrolled(window.scrollY > 12);
      if (window.scrollY < 200) setActive(null); // back on the hero: nothing highlighted
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // Highlight the section currently in view.
  useEffect(() => {
    if (!onHome) return setActive(null);
    const els = sections.map((s) => document.getElementById(s.id)).filter(Boolean) as HTMLElement[];
    const io = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((e) => e.isIntersecting);
        if (visible.length) setActive(visible[0].target.id);
      },
      { rootMargin: '-45% 0px -50% 0px' },
    );
    els.forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, [onHome]);

  const href = (id: string) => (onHome ? `#${id}` : `/#${id}`);

  return (
    <header
      className={`fixed inset-x-0 top-0 z-50 transition ${
        scrolled || open ? 'border-b border-line bg-bg/80 backdrop-blur-md' : 'border-b border-transparent'
      }`}
    >
      <nav className="mx-auto flex h-16 max-w-page items-center justify-between px-5 sm:px-8" aria-label="Main">
        <Link href="/" className="font-display text-lg font-semibold tracking-tight">
          shibin<span className="text-accent">.</span>
        </Link>

        <ul className="hidden items-center gap-1 lg:flex">
          {sections.map((s) => (
            <li key={s.id}>
              <a
                href={href(s.id)}
                className={`rounded-lg px-3 py-2 text-sm transition ${
                  active === s.id ? 'text-accent' : 'text-muted hover:text-fg'
                }`}
                aria-current={active === s.id ? 'true' : undefined}
              >
                {s.label}
              </a>
            </li>
          ))}
        </ul>

        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={() => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')}
            className="rounded-lg p-2 text-lg text-muted transition hover:text-accent"
            aria-label="Toggle light and dark mode"
          >
            {mounted && (resolvedTheme === 'dark' ? <HiOutlineSun /> : <HiOutlineMoon />)}
          </button>
          <button
            type="button"
            onClick={() => setOpen((o) => !o)}
            className="rounded-lg p-2 text-xl text-muted transition hover:text-fg lg:hidden"
            aria-label="Menu"
            aria-expanded={open}
          >
            {open ? <HiX /> : <HiOutlineMenuAlt3 />}
          </button>
        </div>
      </nav>

      <AnimatePresence>
        {open && (
          <motion.ul
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden px-5 pb-4 lg:hidden"
          >
            {sections.map((s) => (
              <li key={s.id}>
                <a
                  href={href(s.id)}
                  onClick={() => setOpen(false)}
                  className="block rounded-lg px-3 py-2.5 text-muted hover:bg-surface hover:text-fg"
                >
                  {s.label}
                </a>
              </li>
            ))}
          </motion.ul>
        )}
      </AnimatePresence>
    </header>
  );
}
