import { Assessment } from '../data/assessments';

export interface ScoredAssessment extends Assessment {
  score: number;
  matchedKeywords: string[];
}

export function matchAssessments(
  query: string,
  assessments: Assessment[],
  minResults: number = 5,
  maxResults: number = 10
): ScoredAssessment[] {
  const normalizedQuery = query.toLowerCase().trim();
  
  if (!normalizedQuery) {
    return [];
  }

  // Extract words from the query (remove common stop words)
  const stopWords = new Set([
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 
    'to', 'was', 'will', 'with', 'we', 'our', 'who', 'this', 'their'
  ]);
  
  const queryWords = normalizedQuery
    .split(/\W+/)
    .filter(word => word.length > 2 && !stopWords.has(word));

  // Score each assessment
  const scoredAssessments: ScoredAssessment[] = assessments.map(assessment => {
    let score = 0;
    const matchedKeywords: string[] = [];

    // Check each keyword against query words
    assessment.keywords.forEach(keyword => {
      const normalizedKeyword = keyword.toLowerCase();
      
      // Exact match in query (higher score)
      if (normalizedQuery.includes(normalizedKeyword)) {
        score += 10;
        matchedKeywords.push(keyword);
      } 
      // Partial word match
      else {
        const keywordWords = normalizedKeyword.split(/\s+/);
        let partialMatches = 0;
        
        keywordWords.forEach(kw => {
          if (queryWords.some(qw => qw.includes(kw) || kw.includes(qw))) {
            partialMatches++;
          }
        });
        
        if (partialMatches > 0) {
          score += partialMatches * 3;
          matchedKeywords.push(keyword);
        }
      }
    });

    // Boost score if assessment name matches
    const normalizedName = assessment.name.toLowerCase();
    queryWords.forEach(word => {
      if (normalizedName.includes(word)) {
        score += 5;
      }
    });

    // Boost score if description matches
    const normalizedDesc = assessment.description.toLowerCase();
    queryWords.forEach(word => {
      if (normalizedDesc.includes(word)) {
        score += 2;
      }
    });

    return {
      ...assessment,
      score,
      matchedKeywords: [...new Set(matchedKeywords)]
    };
  });

  // Filter and sort by score
  const filtered = scoredAssessments
    .filter(a => a.score > 0)
    .sort((a, b) => b.score - a.score);

  // Return between minResults and maxResults
  if (filtered.length < minResults) {
    // If we don't have enough matches, return top assessments anyway
    return scoredAssessments
      .sort((a, b) => b.score - a.score)
      .slice(0, minResults);
  }

  return filtered.slice(0, maxResults);
}
