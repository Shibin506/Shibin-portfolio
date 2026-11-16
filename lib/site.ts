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
    "I'm a software engineer finishing an MS at San Jose State (December 2026). At LinkedIn I worked on the feed recommendation system, shipping ranking-model improvements in PyTorch and TensorFlow (11 of 12 AUC wins), along with RAG and LLM evaluation pipelines.",
    'Before that I spent three and a half years at Accenture as a full-stack engineer, building React and TypeScript apps on Go, Java and Python microservices on AWS, and raising platform availability from 98.2% to 99.7%.',
    'I also contribute to rocketride-server, a 17.8k-star open-source C++/Python AI pipeline engine, fixing bugs in its CLI, LLM provider integrations and graph-database agent tools.',
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
