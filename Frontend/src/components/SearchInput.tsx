import { useState } from 'react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Search, Loader2, Sparkles, Info } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './ui/tooltip';

interface SearchInputProps {
  onSearch: (query: string) => void;
  isLoading?: boolean;
}

export function SearchInput({ onSearch, isLoading = false }: SearchInputProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query);
    }
  };

  const examples = [
    { text: "Data analyst with Excel skills", icon: "📊" },
    { text: "Software developer", icon: "💻" },
    { text: "Customer service rep", icon: "🎧" },
    { text: "Leadership role", icon: "👔" },
    { text: "Graduate position", icon: "🎓" }
  ];

  const characterCount = query.length;
  const isQueryValid = query.trim().length >= 10;

  return (
    <div className="w-full space-y-3 sm:space-y-4">
      <form onSubmit={handleSubmit} className="space-y-3 sm:space-y-4">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label htmlFor="query" className="block flex items-center gap-1.5 sm:gap-2">
              <Sparkles className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-indigo-600" />
              <span className="text-sm sm:text-base">Step 1: Describe the Role</span>
            </label>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger type="button" className="text-muted-foreground hover:text-foreground transition-colors">
                  <Info className="h-4 w-4" />
                </TooltipTrigger>
                <TooltipContent className="max-w-xs">
                  <p>Enter keywords, skills, or a full job description. The more details you provide, the better the recommendations!</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          <div className="relative">
            <Textarea
              id="query"
              placeholder="Example: We're looking for a data analyst with Excel skills and numerical reasoning..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="min-h-[100px] sm:min-h-[120px] resize-none border-2 focus:border-indigo-400 transition-colors text-sm sm:text-base"
              disabled={isLoading}
            />
            <div className="absolute bottom-2 sm:bottom-3 right-2 sm:right-3 flex items-center gap-2">
              {characterCount > 0 && (
                <span className={`text-[10px] sm:text-xs ${isQueryValid ? 'text-green-600' : 'text-amber-600'}`}>
                  {isQueryValid ? '✓ Good to go' : 'Add details'}
                </span>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-2 sm:gap-3">
          <Button 
            type="submit" 
            size="lg"
            className="flex-1 sm:flex-none bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all text-sm sm:text-base"
            disabled={isLoading || !query.trim()}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 sm:h-5 sm:w-5 animate-spin" />
                <span className="hidden sm:inline">Finding Perfect Matches...</span>
                <span className="sm:hidden">Searching...</span>
              </>
            ) : (
              <>
                <Search className="mr-2 h-4 w-4 sm:h-5 sm:w-5" />
                <span className="hidden sm:inline">Get Assessment Recommendations</span>
                <span className="sm:hidden">Find Assessments</span>
              </>
            )}
          </Button>
          {query.trim() && !isLoading && (
            <Button 
              type="button"
              variant="outline"
              onClick={() => setQuery('')}
              className="border-gray-300 text-sm"
            >
              Clear
            </Button>
          )}
        </div>
      </form>

      <div className="space-y-2 sm:space-y-3 pt-2">
        <div className="flex items-center gap-2">
          <div className="h-px flex-1 bg-gradient-to-r from-transparent via-indigo-200 to-transparent" />
          <p className="text-[10px] sm:text-xs text-muted-foreground whitespace-nowrap">Quick Examples</p>
          <div className="h-px flex-1 bg-gradient-to-r from-transparent via-indigo-200 to-transparent" />
        </div>
        <div className="flex flex-wrap gap-1.5 sm:gap-2">
          {examples.map((example, index) => (
            <Button
              key={index}
              variant="outline"
              size="sm"
              onClick={() => setQuery(example.text)}
              disabled={isLoading}
              className="text-[10px] sm:text-xs border-indigo-200 hover:bg-indigo-50 hover:border-indigo-300 transition-colors group h-7 sm:h-8 px-2 sm:px-3"
            >
              <span className="mr-1">{example.icon}</span>
              <span className="hidden xs:inline">{example.text}</span>
              <span className="xs:hidden">{example.text.split(' ')[0]}</span>
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
}
