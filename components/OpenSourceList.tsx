'use client';

import { motion } from 'framer-motion';
import PageLayout from './PageLayout';
import { FaGithub, FaStar, FaCodeBranch } from 'react-icons/fa';
import {
  OpenSourceContribution,
  OpenSourceProject,
} from '@/lib/openSourceData';

interface OpenSourceListProps {
  project: OpenSourceProject;
  contributions: OpenSourceContribution[];
}

const statusStyles: Record<string, string> = {
  Merged:
    'bg-purple-100 text-purple-800 border-purple-200 dark:bg-purple-900/40 dark:text-purple-200 dark:border-purple-700',
  'In Review':
    'bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-900/40 dark:text-amber-200 dark:border-amber-700',
};

const chip =
  'bg-gray-100 dark:bg-gray-700 text-sm px-2 py-1 rounded-full text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-600';

export default function OpenSourceList({ project, contributions }: OpenSourceListProps) {
  return (
    <PageLayout
      title="Open Source"
      description="Contributions to open-source software I use and care about"
    >
      {/* Project overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="card mb-10"
      >
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-100">
            {project.name}
          </h2>
          <span className="flex items-center gap-2 text-sm font-medium text-gray-600 dark:text-gray-300">
            <FaStar className="text-amber-500" />
            {project.stars} stars
          </span>
        </div>
        <p className="mt-2 text-gray-600 dark:text-gray-300">{project.summary}</p>
        <ul className="mt-3 space-y-1">
          {project.highlights.map((point, i) => (
            <li key={i} className="text-gray-600 dark:text-gray-300 flex items-start">
              <span className="text-primary dark:text-primary-light mr-2">•</span>
              {point}
            </li>
          ))}
        </ul>
        <div className="mt-4 flex flex-wrap gap-2">
          {project.techStack.map((tech) => (
            <span key={tech} className={chip}>{tech}</span>
          ))}
        </div>
        <a
          href={project.url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-6 inline-flex items-center gap-2 text-gray-600 hover:text-primary dark:text-gray-300 dark:hover:text-primary-light transition-colors"
        >
          <FaGithub className="w-5 h-5" />
          <span className="text-sm font-medium">View repository</span>
        </a>
      </motion.div>

      <h2 className="mb-6 text-2xl font-semibold text-gray-800 dark:text-gray-100">
        Pull Requests
      </h2>
      <div className="grid gap-8 md:grid-cols-2">
        {contributions.map((pr, index) => (
          <motion.div
            key={pr.prNumber}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 + index * 0.1 }}
            whileHover={{ scale: 1.02 }}
            className="card hover-lift relative overflow-hidden group"
          >
            <div className="relative z-10">
              <div className="flex items-center justify-between gap-3 mb-3">
                <span className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                  <FaCodeBranch />
                  {pr.repo}#{pr.prNumber}
                </span>
                <span
                  className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${statusStyles[pr.status]}`}
                >
                  {pr.status}
                </span>
              </div>
              <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-100 group-hover:text-primary dark:group-hover:text-primary-light transition-colors duration-300">
                {pr.title}
              </h3>
              <ul className="mt-2 space-y-1">
                {pr.description.map((point, i) => (
                  <li key={i} className="text-gray-600 dark:text-gray-300 flex items-start">
                    <span className="text-primary dark:text-primary-light mr-2">•</span>
                    {point}
                  </li>
                ))}
              </ul>
              <div className="mt-4 flex flex-wrap gap-2">
                {pr.techStack.map((tech) => (
                  <span key={tech} className={chip}>{tech}</span>
                ))}
              </div>
              <a
                href={pr.url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-6 inline-flex items-center gap-2 text-gray-600 hover:text-primary dark:text-gray-300 dark:hover:text-primary-light transition-colors"
              >
                <FaGithub className="w-5 h-5" />
                <span className="text-sm font-medium">View pull request</span>
              </a>
            </div>
          </motion.div>
        ))}
      </div>
    </PageLayout>
  );
}
