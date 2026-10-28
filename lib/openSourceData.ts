export type ContributionStatus = "Merged" | "In Review";

export interface OpenSourceContribution {
  title: string;
  status: ContributionStatus;
  repo: string;
  prNumber: number;
  description: string[];
  techStack: string[];
  url: string;
}

export interface OpenSourceProject {
  name: string;
  repo: string;
  url: string;
  stars: string;
  summary: string;
  highlights: string[];
  techStack: string[];
}

export const openSourceProject: OpenSourceProject = {
  name: "rocketride-server",
  repo: "rocketride-org/rocketride-server",
  url: "https://github.com/rocketride-org/rocketride-server",
  stars: "17.8k",
  summary:
    "An open-source, multithreaded C++17/Python engine that executes AI workflows across 130+ Python nodes, 15+ LLM providers, and databases.",
  highlights: [
    "Contributed core runtime and execution optimizations to the engine.",
    "Implemented exact-once delivery semantics for payload queues and integrated Model Context Protocol (MCP) in production environments.",
  ],
  techStack: ["C++17", "Python", "Model Context Protocol (MCP)", "LLM Providers", "Multithreading"],
};

export const openSourceContributions: OpenSourceContribution[] = [
  {
    title: "Fix bare --modelserver port being read as a hostname",
    status: "Merged",
    repo: "rocketride-org/rocketride-server",
    prNumber: 2679,
    description: [
      "Found and fixed a bug where a bare port in --modelserver (e.g. --modelserver=5590) was read as a hostname, so the Python client tried to connect to ws://5590:5565/models and failed.",
      "A bare port is now normalized to localhost:PORT, the model server on the engine's own loopback, and the docs and changelog spell out that a model server on the Docker host still needs an explicit address.",
      "Passed the project's full CI on macOS, Ubuntu, and Windows before merging into develop.",
    ],
    techStack: ["Python", "WebSockets", "CLI", "Cross-platform CI"],
    url: "https://github.com/rocketride-org/rocketride-server/pull/2679",
  },
  {
    title: "Send and cap Gemini output token limits",
    status: "In Review",
    repo: "rocketride-org/rocketride-server",
    prNumber: 2680,
    description: [
      "Fixed the Gemini LLM node so the configured output-token limit is actually sent to Google and saved where it is read back.",
      "Capped the Gemini image models at Google's published output limits and added tests pinning the 2.0 profiles' 8,192-token limit.",
      "Open pull request, currently addressing maintainer review feedback.",
    ],
    techStack: ["Python", "Gemini API", "LLM Providers", "Unit Testing"],
    url: "https://github.com/rocketride-org/rocketride-server/pull/2680",
  },
];
