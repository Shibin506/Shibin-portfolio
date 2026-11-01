export interface Project {
  title: string;
  description: string[];
  techStack: string[];
  github?: string;
  demo?: string;
}

export const projectsData: Project[] = [
  {
    title: "Minutes: AI Meeting Copilot",
    description: [
      "Built an AI meeting copilot that turns Zoom, Meet and Teams transcripts into summaries, decisions and owner-assigned action items, each linked to the exact moment it was said.",
      "Designed retrieval-augmented Q&A across meetings with SQLite FTS5 (BM25) over speaker-turn chunks, streaming cited answers from Claude over server-sent events; an offline eval finds the answer in the top 3 results for 20/20 questions.",
      "Used Claude structured outputs validated with Pydantic, with the model citing transcript segment numbers that the server maps to exact timestamps, plus a no-API-key demo mode, 40 backend tests, Docker Compose and GitHub Actions CI."
    ],
    techStack: ["Python", "FastAPI", "Claude API", "RAG", "SQLite FTS5", "Pydantic", "React", "TypeScript", "Vite", "Docker", "GitHub Actions"],
    github: "https://github.com/Shibin506/minutes-ai",
    demo: ""
  },
  {
    title: "Autonomous AI Agent & Serverless Workflow Engine",
    description: [
      "Engineered an autonomous AI agent framework and serverless workflow engine in Go, Python, and Rust, utilizing custom RAG pipelines, LLMs, and Kafka to automate complex manual handoffs.",
      "Designed custom concurrency handlers and event-driven streaming in Apache Flink, lowering real-time queuing latency from 150ms to 95ms across distributed deployments.",
      "Deployed containerized microservice nodes on AWS EKS and Kubernetes with Docker, sustaining 99.5% node reliability in production environments."
    ],
    techStack: ["Go (Golang)", "Python", "Rust", "AWS Lambda", "RAG Pipelines", "Vector Databases", "Kafka", "Apache Flink", "Docker", "Kubernetes", "AWS EKS"]
  },
  {
    title: "Lumen: RAG Analytics & Client Integration Platform",
    description: [
      "Built a Go ingestion gateway (gRPC + REST) that validates client events against per-tenant JSON Schemas and lands them in an S3 data lake, backed by a Java GraphQL schema registry that blocks breaking schema changes.",
      "Orchestrated a nightly Airflow + Apache Spark pipeline that compacts raw JSON into partitioned Parquet and rollups for Trino, cutting dashboard query time by 70% (4.0s to 1.2s across five queries on 2.35M events).",
      "Shipped a RAG assistant (FastAPI, pgvector, hybrid vector + keyword retrieval) that streams cited answers and learns from user feedback, with a React + TypeScript dashboard for telemetry, analytics and schema editing."
    ],
    techStack: ["Go (Golang)", "Java", "Python", "TypeScript", "React.js", "GraphQL", "gRPC", "Apache Spark", "Trino", "Airflow", "PostgreSQL", "pgvector", "AWS S3", "RAG"],
    github: "https://github.com/Shibin506/rag-analytics-platform",
    demo: ""
  },
  {
    title: "GlobalGuide AI Travel Planner",
    description: [
      "Developed an advanced AI application leveraging Groq LLM and LangGraph for comprehensive, personalized travel itinerary generation, integrating real-time data from various APIs.",
      "Architected and implemented a robust agentic workflow using LangGraph enabling multi-step AI reasoning and dynamic tool utilization across 9 distinct custom tools.",
      "Built a full-stack solution with a high-performance FastAPI backend handling API requests in milliseconds."
    ],
    techStack: ["Python", "FastAPI", "Streamlit", "Groq LLM", "LangGraph", "Pydantic", "Requests", "OpenWeatherMap API", "Google Places API", "ExchangeRate-API"],
    github: "https://github.com/Shibin506/globalguide-ai-travel-planner",
    demo: ""
  },
  {
    title: "AI Medical Chatbot with RAG",
    description: [
      "Deployed a medical chatbot powered by RAG architecture to assist patients and healthcare providers by retrieving and summarizing relevant medical documents in real time.",
      "Utilized HuggingFace Transformers for text embedding and Faiss for vector search, achieving 91% semantic retrieval accuracy across 5K+ healthcare records."
    ],
    techStack: ["HuggingFace", "Faiss", "LangChain", "Mistral 7B", "Streamlit", "Python"],
    github: "https://github.com/Shibin506/ai-medical-chatbot",
    demo: ""
  },
  {
    title: "Spotify Data Analysis",
    description: [
      "Designed and developed a complete data warehousing solution to analyze Spotify streaming data and deliver actionable insights for music trends.",
      "Utilized Spotify API and Python to extract and preprocess real-time track metadata including artist, genre, popularity.",
      "Modeled data using a star schema in Snowflake, improving query efficiency by 30% for genre/artist insights.",
      "Built over 20+ compelling visualizations using Matplotlib and Power BI, showcasing trends in genres, top artists, and track popularity."
    ],
    techStack: ["AWS S3", "Glue", "Snowflake", "Python", "Matplotlib", "Power BI", "Spotify API"],
    github: "https://github.com/Shibin506/spotify-data-analysis",
    demo: ""
  },
  {
    title: "Sentiment Analysis on Yelp Reviews",
    description: [
      "Built a real-time sentiment analysis pipeline to classify 5,000+ Yelp reviews as positive, negative, or neutral with 90%+ accuracy, using TextBlob and VADER.",
      "Ingested live review data via Apache NiFi and classified sentiment using PySpark and Python socket programming.",
      "Stored results in AWS S3 for further analysis and historical tracking.",
      "Developed a Streamlit dashboard to visualize sentiment trends in real time, updated every 60 seconds."
    ],
    techStack: ["Python", "PySpark", "TextBlob", "VADER", "Apache NiFi", "AWS S3", "Streamlit"],
    github: "https://github.com/Shibin506/yelp-sentiment-analysis",
    demo: ""
  }
]; 