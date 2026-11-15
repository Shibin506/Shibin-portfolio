import type { NextConfig } from "next";

// The site used to have one page per section; send old links to the matching
// section of the single-page home.
const sectionPages = ["experience", "projects", "skills", "education", "open-source"];

const nextConfig: NextConfig = {
  async redirects() {
    return sectionPages.map((s) => ({ source: `/${s}`, destination: `/#${s}`, permanent: false }));
  },
};

export default nextConfig;
