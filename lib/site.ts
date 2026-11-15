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
    "I'm a software engineer finishing an MS in Applied Data Intelligence at San Jose State (December 2026). This summer I was a Software Engineer Intern at LinkedIn, where I worked on the feed recommendation system: ranking-model optimizations in PyTorch that won 11 of 12 AUC comparisons (up to +0.20% clicks) and improved normalized entropy in 11 of 12. I also built RAG pipelines and LLM evaluation workflows, and the Go and Python services and AWS/GCP telemetry pipelines around them.",
    'Before that I spent three and a half years at Accenture as a full-stack engineer: React and TypeScript client apps on top of Go, Java and Python microservices, REST, gRPC and GraphQL APIs, and PostgreSQL tuning that cut API response times from 450 ms to 280 ms, on AWS architectures that took availability from 98.2% to 99.7%.',
    'On my own time I build end to end: full-stack apps like MedBridge (FastAPI + Next.js) and Lumen (Go, Java and Python services behind a React dashboard), a crash-safe storage engine in Rust, and a GitHub App that diagnoses failed CI runs. I also contribute to rocketride-server, an open-source C++/Python AI pipeline engine. I like measuring things: most of my projects ship with an eval or a benchmark.',
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
