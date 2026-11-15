export interface Project {
  title: string;
  description: string[];
  techStack: string[];
  github?: string;
  demo?: string;
  /** Path to a short demo video in /public, shown inline on the card. */
  video?: string;
  videoPoster?: string;
} 