export interface Education {
  institution: string;
  degree: string;
  location: string;
  startDateText: string;
  endDateText: string;
  grade: string;
  coursework: string[];
  logo: string;
}

export const educationData: Education[] = [
  {
    institution: "San Jose State University",
    degree: "Masters in Applied Data Science",
    location: "San Jose, CA",
    startDateText: "January 2025",
    endDateText: "Present",
    grade: "In Progress",
    coursework: [
      "Data Science Fundamentals",
      "Machine Learning",
      "Statistical Analysis",
      "Big Data Processing",
      "Data Visualization",
      "Database Systems"
    ],
    logo: "/sjsu-logo.svg"
  }
]; 