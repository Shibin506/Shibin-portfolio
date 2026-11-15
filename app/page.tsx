import Hero from '@/components/home/Hero';
import About from '@/components/home/About';
import Experience from '@/components/home/Experience';
import OpenSource from '@/components/home/OpenSource';
import Projects from '@/components/home/Projects';
import Skills from '@/components/home/Skills';
import Education from '@/components/home/Education';
import Contact from '@/components/home/Contact';

export default function Home() {
  return (
    <main>
      <Hero />
      <About />
      <Experience />
      <OpenSource />
      <Projects />
      <Skills />
      <Education />
      <Contact />
    </main>
  );
}
