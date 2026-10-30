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
    title: "StrataKV — Crash-Safe Storage Engine in Rust",
    description: [
      "Built a crash-safe key-value storage engine as a log-structured merge tree, the design behind LevelDB, RocksDB and Cassandra: checksummed write-ahead log, SSTables with Bloom filters and block index, and levelled background compaction.",
      "Added MVCC snapshots and range scans that stay consistent while writers and compaction keep running; crash tests kill a real process at every step of every disk operation.",
      "Benchmarked against RocksDB and SQLite on 1M keys: level with RocksDB on random writes (381K vs 386K ops/s) and 1.6x faster on in-memory point reads."
    ],
    techStack: ["Rust", "LSM Tree", "Write-Ahead Log", "MVCC", "Bloom Filters", "Criterion"],
    github: "https://github.com/Shibin506/StrataKV",
    demo: ""
  },
  {
    title: "redos-proof — ReDoS Detector with Proofs",
    description: [
      "Built a tool that finds regular expressions vulnerable to catastrophic backtracking (ReDoS) in JavaScript, TypeScript, Python and Ruby code, using a step-counted model of how each engine backtracks.",
      "Proves every finding by generating the attack input and running it on the real Node, Python and Ruby engines at growing lengths; 100% recall and 0 false positives on a self-verifying corpus.",
      "Ships as a CLI, pre-commit hook and GitHub Action with SARIF output, so it can gate CI."
    ],
    techStack: ["Rust", "Regex Engines", "NFA", "Static Analysis", "GitHub Actions", "SARIF"],
    github: "https://github.com/Shibin506/redos-proof",
    demo: ""
  },
  {
    title: "MedBridge — AI Discharge-Care Assistant",
    description: [
      "Turns hospital discharge papers into a plan patients can follow: an LLM extracts medicines, appointments and warning signs with source quotes, and code verifies every item, drug name and number against the original paper.",
      "Generates plain-language plans in 8 languages with code-checked safety rules for duplicate ingredients, stopped medicines and daily dose limits.",
      "Runs daily check-ins over SMS (Twilio) and Telegram, escalating worrying replies to a care-team dashboard; covered by 804 automated tests, including a 336-case safety evaluation."
    ],
    techStack: ["Python", "FastAPI", "Next.js", "TypeScript", "LLMs", "Twilio", "Telegram", "SQLite"],
    github: "https://github.com/Shibin506/MedBridge",
    demo: ""
  },
  {
    title: "Minutes — AI Meeting Copilot",
    description: [
      "Upload a Zoom, Meet or Teams transcript and get a summary, decisions and action items, each linked to the exact transcript timestamp; the model cites segment numbers so timestamps cannot drift.",
      "Ask questions across all meetings and get streamed answers (server-sent events) with numbered citations, retrieved from an SQLite FTS5 BM25 index.",
      "Retrieval scores hit@3 = 1.00 on a 20-question eval that runs in CI; fully Dockerized with GitHub Actions."
    ],
    techStack: ["Python", "FastAPI", "SQLite FTS5", "Claude API", "React", "TypeScript", "Docker", "GitHub Actions"],
    github: "https://github.com/Shibin506/minutes-ai",
    demo: ""
  },
  {
    title: "ScreenSensei — On-Screen AI Tutor (Cal Hacks 13.0)",
    description: [
      "Team project built at Cal Hacks 13.0: a desktop tutor for Windows and macOS that reads your screen, points at what matters, draws hand-drawn marks and working beside the problem, and talks you through it step by step.",
      "Fastify orchestrator streams Claude's answer as structured steps, so voice narration starts about 3 seconds after a question while the rest of the lesson is still being generated.",
      "Cartesia text-to-speech drives the timing: each step's pointer and drawings appear when its audio starts, keeping voice and visuals in sync.",
      "Guided lessons for math, chess, software and languages watch the screen for the user's next action and check it before continuing, backed by a 13-case accuracy eval set and 380+ unit tests."
    ],
    techStack: ["TypeScript", "Electron", "React", "Fastify", "Anthropic Claude", "Cartesia", "Convex", "Elastic / OpenTelemetry", "Vitest", "pnpm"],
    github: "https://github.com/Shibin506/ai-desktop",
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
    github: "https://github.com/Shibin506/GlobalGuide-AI-Travel-Planner",
    demo: ""
  },
  {
    title: "AI Medical Chatbot with RAG",
    description: [
      "Deployed a medical chatbot powered by RAG architecture to assist patients and healthcare providers by retrieving and summarizing relevant medical documents in real time.",
      "Utilized HuggingFace Transformers for text embedding and Faiss for vector search, achieving 91% semantic retrieval accuracy across 5K+ healthcare records."
    ],
    techStack: ["HuggingFace", "Faiss", "LangChain", "Mistral 7B", "Streamlit", "Python"],
    github: "https://github.com/Shibin506/AI-MEDICAL-CHATBOT-with-RAG",
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
    github: "https://github.com/Shibin506/Spotifyzer",
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
    github: "https://github.com/Shibin506/Sentiment-Analysis-on-Yelp-Reviews",
    demo: ""
  }
]; 