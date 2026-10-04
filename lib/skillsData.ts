export interface Skill {
  skill: string;
  category: string;
  order: number;
}

const make = (category: string, skills: string[]): Skill[] =>
  skills.map((skill, i) => ({ skill, category, order: i + 1 }));

export const skillsData: Skill[] = [
  ...make("Languages", ["Java", "Python", "C++", "JavaScript", "TypeScript", "C#", "SQL", "HTML", "CSS"]),
  ...make("Database", ["PostgreSQL", "MongoDB", "Redis", "Snowflake", "AWS", "GCP"]),
  ...make("Frameworks", ["React", "Node.js", "Spring Boot", "FastAPI", "REST APIs", "GraphQL", "Microservices Architecture", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "PySpark"]),
  ...make("DevOps", ["Docker", "Kubernetes", "CI/CD", "Git"]),
  ...make("AI/ML", ["PyTorch", "Multi-Task Learning", "Feed Ranking", "Vector Search", "Distributed Training (DDP)", "LLM Workflows", "RAG Pipelines", "Hugging Face"]),
  ...make("Others", ["Full SDLC", "Unit Testing", "Integration Testing", "Debugging", "Code Reviews", "Performance Profiling", "Distributed Systems", "Data Structures", "Algorithms", "AI-Assisted Coding (GitHub Copilot)"]),
];
