export interface Skill {
  skill: string;
  category: string;
  order: number;
}

const make = (category: string, skills: string[]): Skill[] =>
  skills.map((skill, i) => ({ skill, category, order: i + 1 }));

export const skillsData: Skill[] = [
  ...make("Languages", ["Go (Golang)", "Python", "TypeScript", "JavaScript", "Java", "C++", "Rust", "SQL", "Bash"]),
  ...make("Database", ["PostgreSQL", "DynamoDB", "Redis", "Cassandra", "Vector Search", "AWS", "GCP"]),
  ...make("Frameworks", ["React", "Next.js", "Node.js", "REST APIs", "gRPC", "Protobuf", "GraphQL", "WebSockets", "Microservices Architecture"]),
  ...make("DevOps", ["Docker", "Kubernetes", "Git", "CI/CD", "Jenkins", "PyTest", "Linux Internals", "System Monitoring"]),
  ...make("AI/ML", ["RAG Pipelines", "LLMs", "LangChain", "Vector Databases", "AI Agents", "PyTorch"]),
  ...make("Others", ["Kafka", "Apache Flink", "Apache Spark", "Trino", "Airflow", "Serverless Architecture", "Distributed Systems", "Unit Testing"]),
];
