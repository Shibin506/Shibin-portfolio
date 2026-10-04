export interface Experience {
  company: string;
  role: string;
  location: string;
  startDateText: string;
  endDateText: string;
  description: string;
  logo: string;
}

export const experienceData: Experience[] = [
  {
    company: "LinkedIn",
    role: "AI/ML Intern",
    location: "Sunnyvale, CA, USA",
    startDateText: "May 2026",
    endDateText: "August 2026",
    description: `• Architected and benchmarked novel Multi-Task Learning (MTL) heads (MMoE v3, 2-Level PLE, Grouped/Capped CGC, DCNv2) for a 12-objective feed ranking model, systematically resolving gradient conflict and capacity contention across sparse and high-frequency engagement signals.

• Delivered top-tier ranking quality gains, achieving 11/12 AUC wins (up to +0.20% Click, +0.34% Save, +1.00% Message) and 11/12 Normalized Entropy (NE) improvements (up to -0.87% Vote NE, -0.82% Message NE).

• Designed and deployed a Hybrid Static-Head + Hashed-Tail embedding layer for ultra-high cardinality features (hashedActorId, 201.5M entities across 79.5B training impressions), eliminating severe hash collision interference across 16.78M embedding rows.

• Optimized multi-task gate routing by implementing a 20% capped private capacity constraint, gate dropout (0.15), and learnable softmax scales, preventing high-frequency signals (click, like) from monopolizing expert capacity.

• Implemented distributed GPU state synchronization (All-Gather sync across PyTorch DDP ranks) for dynamic registry updates and evaluated LFU eviction policies, identifying key trade-offs between eviction strategies.`,
    logo: "/linkedin.svg"
  },
  {
    company: "Accenture Pvt Ltd",
    role: "Software Engineer",
    location: "Pune, India",
    startDateText: "July 2021",
    endDateText: "December 2024",
    description: `• Developed and deployed predictive machine learning models (Scikit-learn, PyTorch, Python) for customer classification and lifecycle churn prediction, leveraging complex SQL queries on large-scale relational datasets.

• Conducted data mining, statistical analysis, and automated feature selection on multi-terabyte customer datasets, improving predictive model precision and recall by 18%.

• Containerized ML scoring microservices using Docker and deployed scalable inference pipelines on AWS (ECS, S3) with continuous integration (CI/CD), ensuring 99.6% system uptime.

• Designed unit and integration testing suites (PyTest, JUnit) for automated ML data validation and API endpoints, reducing production data pipeline defects by 24%.`,
    logo: "/accenture.webp"
  }
];
