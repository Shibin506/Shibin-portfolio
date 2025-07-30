export interface Skill {
  skill: string;
  category: string;
  order: number;
}

export const skillsData: Skill[] = [
  // Languages
  { skill: "Python", category: "Languages", order: 1 },
  { skill: "Java", category: "Languages", order: 2 },
  { skill: "C", category: "Languages", order: 3 },
  { skill: "C++", category: "Languages", order: 4 },
  { skill: "HTML", category: "Languages", order: 5 },
  { skill: "CSS", category: "Languages", order: 6 },
  { skill: "JavaScript", category: "Languages", order: 7 },
  { skill: "PowerShell", category: "Languages", order: 8 },

  // Database and Query Languages
  { skill: "MySQL", category: "Database", order: 1 },
  { skill: "NoSQL", category: "Database", order: 2 },
  { skill: "MongoDB", category: "Database", order: 3 },
  { skill: "PostgreSQL", category: "Database", order: 4 },
  { skill: "Snowflake", category: "Database", order: 5 },
  { skill: "AWS", category: "Database", order: 6 },
  { skill: "Azure", category: "Database", order: 7 },
  { skill: "Apache", category: "Database", order: 8 },

  // Frameworks/Libraries
  { skill: "Matplotlib", category: "Frameworks", order: 1 },
  { skill: "NumPy", category: "Frameworks", order: 2 },
  { skill: "Pandas", category: "Frameworks", order: 3 },
  { skill: "PySpark", category: "Frameworks", order: 4 },
  { skill: "Seaborn", category: "Frameworks", order: 5 },
  { skill: "React.js", category: "Frameworks", order: 6 },
  { skill: "Node.js", category: "Frameworks", order: 7 },

  // DevOps
  { skill: "AWS-CDK", category: "DevOps", order: 1 },
  { skill: "Docker", category: "DevOps", order: 2 },
  { skill: "GitHub Actions", category: "DevOps", order: 3 },
  { skill: "Kubernetes", category: "DevOps", order: 4 },
  { skill: "Jenkins", category: "DevOps", order: 5 },

  // AI/ML
  { skill: "LLM Integration", category: "AI/ML", order: 1 },
  { skill: "RAG Pipelines", category: "AI/ML", order: 2 },
  { skill: "Hugging Face", category: "AI/ML", order: 3 },
  { skill: "Vector DBs", category: "AI/ML", order: 4 },

  // Others
  { skill: "Agile", category: "Others", order: 1 },
  { skill: "Backend Development", category: "Others", order: 2 },
  { skill: "Communication Skills", category: "Others", order: 3 },
  { skill: "Power BI", category: "Others", order: 4 },
  { skill: "Tableau", category: "Others", order: 5 },
  { skill: "Problem Solving", category: "Others", order: 6 },
  { skill: "Postman", category: "Others", order: 7 },
  { skill: "Elasticsearch", category: "Others", order: 8 },
  { skill: "Kibana", category: "Others", order: 9 }
]; 