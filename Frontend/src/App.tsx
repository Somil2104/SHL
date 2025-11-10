import React, { useState } from 'react';
import { SearchInput } from './components/SearchInput';
import { ResultsTable } from './components/ResultsTable';
import { assessments } from './data/assessments';
import { matchAssessments, ScoredAssessment } from './utils/matcher';
import { Card } from './components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { FileText, Lightbulb, ArrowRight } from 'lucide-react';
import { Toaster } from './components/ui/sonner';
import react from '@vitejs/plugin-react-swc';

export default function App() {
  const [results, setResults] = useState<ScoredAssessment[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [currentQuery, setCurrentQuery] = useState('');

  const handleSearch = async (query: string) => {
    setIsLoading(true);
    setCurrentQuery(query);
    setHasSearched(false);

    // Scroll to top for better UX
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Simulate API delay for better UX
    await new Promise(resolve => setTimeout(resolve, 800));
    console.log("called")
    try {
      const response = await fetch("http://localhost:8000/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
    
      if (!response.ok) throw new Error("Backend error");
      const data = await response.json();
    
      setResults(data.recommended_assessments || []);
    } catch (error) {
      console.error("Error fetching recommendations:", error);
    } finally {
      setIsLoading(false);
      setHasSearched(true);
    }
    setIsLoading(false);
    setHasSearched(true);

    // Scroll to results after loading
    setTimeout(() => {
      document.getElementById('results-section')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50">
      {/* Header */}
      <header className="border-b bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white shadow-lg">
        <div className="container mx-auto px-3 sm:px-4 py-4 sm:py-6">
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="flex items-center justify-center w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-white/20 backdrop-blur-sm shadow-lg flex-shrink-0">
              <Lightbulb className="h-5 w-5 sm:h-7 sm:w-7" />
            </div>
            <div className="min-w-0">
              <h1 className="text-white text-lg sm:text-2xl lg:text-3xl">SHL Assessment Recommender</h1>
              <p className="text-xs sm:text-sm text-white/90 hidden sm:block">
                Find the most relevant individual test solutions for your hiring needs
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-3 sm:px-4 py-4 sm:py-8">
        <div className="max-w-7xl mx-auto space-y-6 sm:space-y-8">
          {/* Search Section */}
          <Card className="p-4 sm:p-6 border-2 border-indigo-100 shadow-xl bg-gradient-to-br from-white to-indigo-50/30">
            <div className="space-y-3 sm:space-y-4">
              <div className="flex items-start gap-2 sm:gap-3">
                <div className="flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-md flex-shrink-0">
                  <FileText className="h-4 w-4 sm:h-5 sm:w-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <h2 className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent text-lg sm:text-xl">Describe Your Role or Requirements</h2>
                  <p className="text-xs sm:text-sm text-muted-foreground mt-1">
                    Enter a job description or requirements to get personalized assessment recommendations.
                  </p>
                </div>
              </div>
              
              <SearchInput onSearch={handleSearch} isLoading={isLoading} />
            </div>
          </Card>

          {/* Results Section */}
          {hasSearched && (
            <div id="results-section" className="space-y-3 sm:space-y-4 scroll-mt-8">
              <div className="flex items-center gap-2 sm:gap-3">
                <div className="flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600 text-white shadow-md flex-shrink-0">
                  <span className="text-sm sm:text-base">2</span>
                </div>
                <div className="flex-1 min-w-0">
                  <h2 className="bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent text-lg sm:text-xl">Your Personalized Results</h2>
                  {results.length > 0 && (
                    <p className="text-xs sm:text-sm text-muted-foreground">
                      {results.length} perfect match{results.length !== 1 ? 'es' : ''} found from {assessments.length} assessments
                    </p>
                  )}
                </div>
              </div>
              
              <ResultsTable results={results} query={currentQuery} />
            </div>
          )}

          {/* Info Section */}
          {!hasSearched && (
            <Card className="p-4 sm:p-6 border-2 border-purple-100 shadow-xl bg-gradient-to-br from-white to-purple-50/30">
              <Tabs defaultValue="how-it-works" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="how-it-works" className="text-xs sm:text-sm">How It Works</TabsTrigger>
                  <TabsTrigger value="about" className="text-xs sm:text-sm">About</TabsTrigger>
                </TabsList>
                
                <TabsContent value="how-it-works" className="space-y-3 sm:space-y-4 mt-3 sm:mt-4">
                  <div className="space-y-3 sm:space-y-4">
                    <h3 className="text-base sm:text-lg">How the Recommender Works</h3>
                    <div className="grid gap-3 sm:gap-4 md:grid-cols-2">
                      <Card className="p-3 sm:p-4 bg-gradient-to-br from-indigo-50 to-purple-50 border-2 border-indigo-200">
                        <div className="flex items-start gap-2 sm:gap-3">
                          <div className="flex items-center justify-center w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-indigo-600 text-white flex-shrink-0 text-xs sm:text-sm">
                            1
                          </div>
                          <div className="space-y-0.5 sm:space-y-1">
                            <h4 className="text-xs sm:text-sm text-indigo-900">Describe Your Needs</h4>
                            <p className="text-[10px] sm:text-xs text-indigo-700">
                              Enter job requirements, skills, or a full job description
                            </p>
                          </div>
                        </div>
                      </Card>
                      <Card className="p-3 sm:p-4 bg-gradient-to-br from-blue-50 to-cyan-50 border-2 border-blue-200">
                        <div className="flex items-start gap-2 sm:gap-3">
                          <div className="flex items-center justify-center w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-blue-600 text-white flex-shrink-0 text-xs sm:text-sm">
                            2
                          </div>
                          <div className="space-y-0.5 sm:space-y-1">
                            <h4 className="text-xs sm:text-sm text-blue-900">AI Matching</h4>
                            <p className="text-[10px] sm:text-xs text-blue-700">
                              Our algorithm matches against 20+ SHL assessments
                            </p>
                          </div>
                        </div>
                      </Card>
                      <Card className="p-3 sm:p-4 bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200">
                        <div className="flex items-start gap-2 sm:gap-3">
                          <div className="flex items-center justify-center w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-green-600 text-white flex-shrink-0 text-xs sm:text-sm">
                            3
                          </div>
                          <div className="space-y-0.5 sm:space-y-1">
                            <h4 className="text-xs sm:text-sm text-green-900">Ranked Results</h4>
                            <p className="text-[10px] sm:text-xs text-green-700">
                              Get 5-10 best matches ranked by relevance
                            </p>
                          </div>
                        </div>
                      </Card>
                      <Card className="p-3 sm:p-4 bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200">
                        <div className="flex items-start gap-2 sm:gap-3">
                          <div className="flex items-center justify-center w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-purple-600 text-white flex-shrink-0 text-xs sm:text-sm">
                            4
                          </div>
                          <div className="space-y-0.5 sm:space-y-1">
                            <h4 className="text-xs sm:text-sm text-purple-900">Take Action</h4>
                            <p className="text-[10px] sm:text-xs text-purple-700">
                              Copy links or visit SHL's site to learn more
                            </p>
                          </div>
                        </div>
                      </Card>
                    </div>
                  </div>
                </TabsContent>
                
                <TabsContent value="about" className="space-y-3 sm:space-y-4 mt-3 sm:mt-4">
                  <div className="space-y-3 sm:space-y-4">
                    <h3 className="text-base sm:text-lg">Assessment Categories</h3>
                    <div className="grid gap-2 sm:gap-3 grid-cols-2 md:grid-cols-3">
                      <Card className="p-3 sm:p-4 bg-blue-50 border-2 border-blue-200">
                        <div className="space-y-1 sm:space-y-2">
                          <div className="text-xl sm:text-2xl">🧠</div>
                          <h4 className="text-xs sm:text-sm text-blue-900">Cognitive</h4>
                          <p className="text-[10px] sm:text-xs text-blue-700">
                            Numerical, verbal, logical reasoning
                          </p>
                        </div>
                      </Card>
                      <Card className="p-3 sm:p-4 bg-purple-50 border-2 border-purple-200">
                        <div className="space-y-1 sm:space-y-2">
                          <div className="text-xl sm:text-2xl">🎭</div>
                          <h4 className="text-xs sm:text-sm text-purple-900">Personality</h4>
                          <p className="text-[10px] sm:text-xs text-purple-700">
                            Behavioral traits & preferences
                          </p>
                        </div>
                      </Card>
                      <Card className="p-3 sm:p-4 bg-green-50 border-2 border-green-200">
                        <div className="space-y-1 sm:space-y-2">
                          <div className="text-xl sm:text-2xl">🎯</div>
                          <h4 className="text-xs sm:text-sm text-green-900">Situational</h4>
                          <p className="text-[10px] sm:text-xs text-green-700">
                            Real-world scenarios
                          </p>
                        </div>
                      </Card>
                      <Card className="p-3 sm:p-4 bg-orange-50 border-2 border-orange-200">
                        <div className="space-y-1 sm:space-y-2">
                          <div className="text-xl sm:text-2xl">⚙️</div>
                          <h4 className="text-xs sm:text-sm text-orange-900">Technical</h4>
                          <p className="text-[10px] sm:text-xs text-orange-700">
                            Job-specific skills
                          </p>
                        </div>
                      </Card>
                      <Card className="p-3 sm:p-4 bg-pink-50 border-2 border-pink-200">
                        <div className="space-y-1 sm:space-y-2">
                          <div className="text-xl sm:text-2xl">💡</div>
                          <h4 className="text-xs sm:text-sm text-pink-900">Skills</h4>
                          <p className="text-[10px] sm:text-xs text-pink-700">
                            Competency-based
                          </p>
                        </div>
                      </Card>
                      <Card className="p-3 sm:p-4 bg-gradient-to-br from-indigo-50 to-purple-50 border-2 border-indigo-200">
                        <div className="space-y-1 sm:space-y-2">
                          <div className="text-xl sm:text-2xl">📚</div>
                          <h4 className="text-xs sm:text-sm text-indigo-900">20+ Tests</h4>
                          <p className="text-[10px] sm:text-xs text-indigo-700">
                            Individual solutions
                          </p>
                        </div>
                      </Card>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </Card>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t mt-8 sm:mt-16 bg-white">
        <div className="container mx-auto px-3 sm:px-4 py-4 sm:py-6">
          <p className="text-center text-xs sm:text-sm text-muted-foreground">
            Assessment data based on SHL's catalog. 
            Visit <a href="https://www.shl.com" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-700 hover:underline transition-colors">
              shl.com
            </a> for details.
          </p>
        </div>
      </footer>
      <Toaster position="top-right" />
    </div>
  );
}
