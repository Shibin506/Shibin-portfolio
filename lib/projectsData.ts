export interface Project {
  title: string;
  description: string[];
  techStack: string[];
  github: string;
  demo: string;
}

export const projectsData: Project[] = [
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