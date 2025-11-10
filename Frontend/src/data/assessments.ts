export interface Assessment {
  id: string;
  name: string;
  url: string;
  description: string;
  keywords: string[];
  category: string;
}

export const assessments: Assessment[] = [
  {
    id: "1",
    name: "Verify Interactive - Numerical Reasoning",
    url: "https://www.shl.com/solutions/products/assessments/cognitive/verify-interactive-numerical/",
    description: "Measures numerical reasoning and ability to work with numerical data",
    keywords: ["numerical", "math", "data analysis", "quantitative", "statistics", "analytical", "numbers", "calculations", "finance", "accounting", "analyst", "engineer"],
    category: "Cognitive"
  },
  {
    id: "2",
    name: "Verify Interactive - Verbal Reasoning",
    url: "https://www.shl.com/solutions/products/assessments/cognitive/verify-interactive-verbal/",
    description: "Measures verbal reasoning and ability to understand written information",
    keywords: ["verbal", "reading", "comprehension", "language", "communication", "writing", "editorial", "content", "documentation", "lawyer", "writer", "communication"],
    category: "Cognitive"
  },
  {
    id: "3",
    name: "Verify Interactive - Inductive Reasoning",
    url: "https://www.shl.com/solutions/products/assessments/cognitive/verify-interactive-inductive/",
    description: "Measures logical thinking and pattern recognition abilities",
    keywords: ["logical", "pattern", "abstract", "problem solving", "analytical", "strategic", "critical thinking", "developer", "engineer", "scientist", "research", "innovation"],
    category: "Cognitive"
  },
  {
    id: "4",
    name: "Verify Interactive - Deductive Reasoning",
    url: "https://www.shl.com/solutions/products/assessments/cognitive/verify-interactive-deductive/",
    description: "Measures ability to draw logical conclusions from given information",
    keywords: ["deductive", "logical", "reasoning", "analytical", "problem solving", "critical thinking", "investigation", "detective", "analyst", "auditor", "compliance"],
    category: "Cognitive"
  },
  {
    id: "5",
    name: "Occupational Personality Questionnaire (OPQ)",
    url: "https://www.shl.com/solutions/products/assessments/personality/opq/",
    description: "Comprehensive personality assessment for workplace behaviors and preferences",
    keywords: ["personality", "behavior", "traits", "workplace", "culture fit", "leadership", "teamwork", "motivation", "management", "supervisor", "director", "executive", "soft skills"],
    category: "Personality"
  },
  {
    id: "6",
    name: "Situational Judgment Test - Customer Service",
    url: "https://www.shl.com/solutions/products/assessments/situational-judgment/customer-service/",
    description: "Assesses decision-making in customer service scenarios",
    keywords: ["customer service", "customer support", "client relations", "service", "support", "help desk", "customer experience", "hospitality", "retail", "call center"],
    category: "Situational Judgment"
  },
  {
    id: "7",
    name: "Situational Judgment Test - Leadership",
    url: "https://www.shl.com/solutions/products/assessments/situational-judgment/leadership/",
    description: "Evaluates leadership competencies and decision-making",
    keywords: ["leadership", "management", "supervisor", "team lead", "director", "executive", "manager", "people management", "decision making", "strategic"],
    category: "Situational Judgment"
  },
  {
    id: "8",
    name: "Mechanical Comprehension",
    url: "https://www.shl.com/solutions/products/assessments/technical/mechanical-comprehension/",
    description: "Tests understanding of mechanical and physical principles",
    keywords: ["mechanical", "technical", "engineering", "machinery", "physics", "maintenance", "technician", "engineer", "manufacturing", "operations", "industrial"],
    category: "Technical"
  },
  {
    id: "9",
    name: "Checking and Calculation",
    url: "https://www.shl.com/solutions/products/assessments/cognitive/checking-calculation/",
    description: "Measures accuracy and speed in checking and calculating",
    keywords: ["attention to detail", "accuracy", "data entry", "clerical", "administrative", "bookkeeping", "verification", "quality control", "proofreading", "detailed"],
    category: "Cognitive"
  },
  {
    id: "10",
    name: "IT Skills Assessment - Programming",
    url: "https://www.shl.com/solutions/products/assessments/technical/programming/",
    description: "Evaluates programming knowledge and coding abilities",
    keywords: ["programming", "coding", "developer", "software", "engineer", "java", "python", "javascript", "development", "technical", "computer science", "IT"],
    category: "Technical"
  },
  {
    id: "11",
    name: "Sales Skills Assessment",
    url: "https://www.shl.com/solutions/products/assessments/skills/sales/",
    description: "Measures sales competencies and customer persuasion abilities",
    keywords: ["sales", "selling", "business development", "account management", "revenue", "negotiation", "persuasion", "closing", "sales representative", "account executive"],
    category: "Skills"
  },
  {
    id: "12",
    name: "Situational Judgment Test - Teamwork",
    url: "https://www.shl.com/solutions/products/assessments/situational-judgment/teamwork/",
    description: "Assesses collaboration and teamwork abilities",
    keywords: ["teamwork", "collaboration", "team player", "cooperative", "group work", "interpersonal", "team member", "colleague", "coordination", "project team"],
    category: "Situational Judgment"
  },
  {
    id: "13",
    name: "Graduate Reasoning Test Battery",
    url: "https://www.shl.com/solutions/products/assessments/cognitive/graduate-reasoning/",
    description: "Comprehensive cognitive assessment for graduate-level positions",
    keywords: ["graduate", "entry level", "junior", "cognitive", "reasoning", "assessment", "graduate program", "trainee", "intern", "fresh graduate"],
    category: "Cognitive"
  },
  {
    id: "14",
    name: "Emotional Intelligence Assessment",
    url: "https://www.shl.com/solutions/products/assessments/personality/emotional-intelligence/",
    description: "Measures emotional intelligence and interpersonal awareness",
    keywords: ["emotional intelligence", "EQ", "empathy", "self-awareness", "social skills", "interpersonal", "counselor", "HR", "therapist", "coach", "relationship"],
    category: "Personality"
  },
  {
    id: "15",
    name: "Data Analysis and Interpretation",
    url: "https://www.shl.com/solutions/products/assessments/cognitive/data-analysis/",
    description: "Tests ability to analyze and interpret complex data sets",
    keywords: ["data analysis", "data science", "analytics", "statistics", "BI", "business intelligence", "data analyst", "insights", "metrics", "KPI", "reporting"],
    category: "Cognitive"
  },
  {
    id: "16",
    name: "Motivation Questionnaire (MQ)",
    url: "https://www.shl.com/solutions/products/assessments/personality/motivation-questionnaire/",
    description: "Identifies what motivates individuals in the workplace",
    keywords: ["motivation", "engagement", "drive", "values", "workplace satisfaction", "incentives", "career goals", "ambition", "retention", "job satisfaction"],
    category: "Personality"
  },
  {
    id: "17",
    name: "Excel Skills Assessment",
    url: "https://www.shl.com/solutions/products/assessments/technical/excel/",
    description: "Evaluates Microsoft Excel proficiency and data manipulation skills",
    keywords: ["excel", "spreadsheet", "microsoft office", "data manipulation", "formulas", "pivot tables", "vlookup", "office skills", "administrative", "analyst"],
    category: "Technical"
  },
  {
    id: "18",
    name: "Situational Judgment Test - Safety",
    url: "https://www.shl.com/solutions/products/assessments/situational-judgment/safety/",
    description: "Assesses safety awareness and risk management capabilities",
    keywords: ["safety", "health", "security", "risk", "compliance", "OSHA", "workplace safety", "hazard", "prevention", "safety officer", "security"],
    category: "Situational Judgment"
  },
  {
    id: "19",
    name: "Critical Thinking Assessment",
    url: "https://www.shl.com/solutions/products/assessments/cognitive/critical-thinking/",
    description: "Measures critical thinking and analytical reasoning abilities",
    keywords: ["critical thinking", "analytical", "problem solving", "reasoning", "logic", "evaluation", "strategic thinking", "consultant", "analyst", "research", "complex"],
    category: "Cognitive"
  },
  {
    id: "20",
    name: "Customer Contact Skills Assessment",
    url: "https://www.shl.com/solutions/products/assessments/skills/customer-contact/",
    description: "Evaluates communication and interpersonal skills for customer-facing roles",
    keywords: ["customer contact", "communication", "interpersonal", "client facing", "customer service", "front desk", "reception", "hospitality", "representative", "service"],
    category: "Skills"
  }
];
