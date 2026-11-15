import './globals.css';
import '@fontsource-variable/inter';
import '@fontsource-variable/bricolage-grotesque';
import '@fontsource/ibm-plex-mono/400.css';
import '@fontsource/ibm-plex-mono/500.css';
import type { Metadata } from 'next';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { Providers } from './providers';

export const metadata: Metadata = {
  title: 'Shibin Biji Thomas — Software Engineer',
  description:
    'Software engineer with hands-on AI/ML, full-stack and cloud backend experience as a Software Engineer Intern at LinkedIn and a Software Engineer at Accenture. MS at San Jose State (Dec 2026), open to new-grad roles.',
  openGraph: {
    title: 'Shibin Biji Thomas — Software Engineer',
    description: 'Software engineer with hands-on AI/ML, full-stack and cloud backend experience at LinkedIn and Accenture.',
    type: 'website',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen flex flex-col">
        <Providers>
          <Navbar />
          <div className="flex-1 flex flex-col">{children}</div>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
