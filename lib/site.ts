// Everything on the home page that isn't experience/project/skill data.
// Numbers here are taken from the experience and open-source entries; keep them in sync.

export const site = {
  name: 'Shibin Biji Thomas',
  shortName: 'Shibin',
  role: 'Software Engineer',
  tagline:
    'Hands-on experience in AI/ML, full-stack and cloud backend engineering, from shipping production systems at LinkedIn and Accenture.',
  status: 'Open to new-grad SWE roles · MS graduating Dec 2026',
  email: 'shibinbiji2@gmail.com',
  links: {
    github: 'https://github.com/Shibin506',
    linkedin: 'https://www.linkedin.com/in/shibin-biji-593228183/',
  },
  stats: [
    { value: '120→85ms', label: 'API latency cut', where: 'LinkedIn' },
    { value: '99.7%', label: 'platform availability, up from 98.2%', where: 'Accenture' },
    { value: '17.8k★', label: 'open-source AI engine I contribute to', where: 'rocketride' },
  ],
  about: [
    "I'm a software engineer finishing an MS in Applied Data Intelligence at San Jose State (December 2026). This summer I was a Software Engineer Intern at LinkedIn, building telemetry pipelines, Go and Python services, and LLM evaluation workflows on AWS and GCP.",
    'Before that I spent three and a half years at Accenture designing serverless microservices, React/TypeScript client apps and high-availability AWS architectures.',
    'On my own time I build systems to understand them properly, like a crash-safe storage engine in Rust and a GitHub App that diagnoses failed CI runs, and I contribute to rocketride-server, an open-source C++/Python AI pipeline engine. I like measuring things: most of my projects ship with an eval or a benchmark.',
  ],
};

export const sections = [
  { id: 'about', label: 'About' },
  { id: 'experience', label: 'Experience' },
  { id: 'open-source', label: 'Open Source' },
  { id: 'projects', label: 'Projects' },
  { id: 'skills', label: 'Skills' },
  { id: 'education', label: 'Education' },
  { id: 'contact', label: 'Contact' },
] as const;
