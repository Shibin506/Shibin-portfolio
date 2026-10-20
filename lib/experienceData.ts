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
    role: "Software Engineer Intern",
    location: "Sunnyvale, CA, USA",
    startDateText: "May 2026",
    endDateText: "August 2026",
    description: `• Engineered automated cloud telemetry, workflow automation, and audit monitoring pipelines on AWS (SNS → Firehose → S3, Lambda) and GCP using Go and Python, reducing manual reporting effort by 90%.

• Developed high-throughput serverless microservices and backend APIs in Go and Python, optimizing stream processing and event feedback loops to cut latency from 120ms to 85ms.

• Built custom RAG pipelines, LLM evaluation workflows, and AI agent frameworks in Python and PyTorch, applying vector databases to improve prediction accuracy from 72% to 85%.

• Leveraged AI productivity tools (Claude, Copilot) and serverless AWS Lambda routines for rapid service prototyping, raising system execution reliability from 65% to 87%.

• Delivered production ranking and model optimizations across concurrent pipelines, achieving 11/12 AUC wins (up to +0.20% Click) and 11/12 Normalized Entropy (NE) improvements.

• Orchestrated containerized services on AWS EKS and Kubernetes with Docker, Airflow DAGs, and Git, enforcing automated unit testing and CI/CD verification gates.`,
    logo: "/linkedin.svg"
  },
  {
    company: "Accenture Pvt Ltd",
    role: "Software Engineer",
    location: "Pune, India",
    startDateText: "July 2021",
    endDateText: "December 2024",
    description: `• Architected scalable, serverless microservices and backend transaction systems in Go, Java, and Python, translating client requirements into production systems that lifted platform availability from 98.2% to 99.7%.

• Developed client application web interfaces and integrations using React.js, TypeScript, and RESTful APIs, designing gRPC contracts and GraphQL schemas with Protobuf to standardize data flow.

• Optimized relational database schemas and complex queries across PostgreSQL and SQL, tuning indexing and connection pooling to cut backend API response times from 450ms to 280ms.

• Automated deployment pipelines using Docker, Kubernetes, and Jenkins on AWS and GCP, integrating live telemetry monitoring and automated testing for zero-downtime releases.`,
    logo: "/accenture.webp"
  }
];
