'use client';

import { motion } from 'framer-motion';

interface PageLayoutProps {
  children: React.ReactNode;
  title: string;
  description?: string;
  actions?: React.ReactNode;
}

export default function PageLayout({ children, title, description, actions }: PageLayoutProps) {
  return (
    <motion.main
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="flex-1 pt-24 pb-12"
    >
      <div className="mx-auto h-full max-w-page px-5 sm:px-8">
        <motion.div
          initial={{ y: -20 }}
          animate={{ y: 0 }}
          className="mb-8"
        >
          <div className="flex justify-between items-center">
            <h1 className="font-display text-4xl font-semibold tracking-tight">
              {title}
            </h1>
            {actions && (
              <div className="flex items-center gap-4">
                {actions}
              </div>
            )}
          </div>
          {description && (
            <p className="mt-2 text-lg text-muted">
              {description}
            </p>
          )}
        </motion.div>
        <div className="h-full">
          {children}
        </div>
      </div>
    </motion.main>
  );
} 