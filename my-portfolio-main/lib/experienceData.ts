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
    company: "Accenture Pvt Ltd",
    role: "Software Engineer",
    location: "India",
    startDateText: "March 2023",
    endDateText: "December 2024",
    description: `• Achieved 98% data accuracy by implementing custom validation logic and test automation, ensuring compliance and consistency across datasets from multiple sources.

• Designed and implemented scalable database solutions on AWS (EC2) utilizing advanced SQL partitioning and index optimization techniques, resulting in 40% improved query performance and 25% cost reduction

• Automated data collection and processing workflows using Python scripts, reducing manual work by 40% and increasing productivity

• Integrated Elasticsearch and Kibana to build real-time log monitoring dashboards, enabling faster root cause analysis and improving issue detection time by 30%`,
    logo: "/accenture.webp"
  },
  {
    company: "Accenture Pvt Ltd",
    role: "Associate Software Engineer",
    location: "India",
    startDateText: "July 2021",
    endDateText: "March 2023",
    description: `• Implemented robust database transaction logic leveraging ACID principles and RBAC policies, ensuring data integrity and security compliance

• Collaborated with cross-functional teams to gather requirements and deliver insights that revamped process workflows and decreased costs by 15%

• Implemented CI/CD pipelines using Jenkins for an insurance analytics platform, reducing build and deployment time by 60% and enabling automated testing across multiple environments`,
    logo: "/accenture.webp"
  }
]; 