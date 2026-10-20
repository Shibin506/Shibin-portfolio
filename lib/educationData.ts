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
    degree: "Master of Science in Applied Data Intelligence",
    location: "San Jose, CA",
    startDateText: "January 2025",
    endDateText: "December 2026 (Expected)",
    grade: "3.5 GPA",
    coursework: [
      "Distributed Systems",
      "Database Management",
      "Algorithms",
      "Cloud Infrastructure",
      "Machine Learning"
    ],
    logo: "/sjsu-logo.svg"
  }
];
