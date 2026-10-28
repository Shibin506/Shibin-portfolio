export interface Project {
  title: string;
  description: string[];
  techStack: string[];
  github?: string;
  demo?: string;
}

export const projectsData: Project[] = [
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
    title: "Scalable RAG Analytics & Client Integration Platform",
    description: [
      "Developed a scalable analytics storage and client integration platform in Go, Java, and Python, automating schema validation, vector database indexing, and RAG data pipelines to PostgreSQL and AWS S3.",
      "Orchestrated distributed ETL workflows with Apache Spark, Trino, and Airflow, applying data access optimizations that accelerated analytical query retrieval speed by 35%.",
      "Built customer-facing web interfaces and integration endpoints using TypeScript, React.js, RESTful APIs, GraphQL, and gRPC, integrating real-time telemetry and feedback loops."
    ],
    techStack: ["Go (Golang)", "Java", "TypeScript", "React.js", "GraphQL", "gRPC", "Apache Spark", "Trino", "Airflow", "PostgreSQL", "AWS S3"]
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