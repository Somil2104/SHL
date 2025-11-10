import React, { useState } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './ui/tooltip';
import { ExternalLink, Copy, CheckCircle2, Award, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';

interface RecommendedAssessment {
  url: string;
  assessment_name: string;
  adaptive_support: string;
  description: string;
  duration: string;
  remote_support: string;
  test_type: string[];
}

interface ResultsTableProps {
  results: RecommendedAssessment[];
  query: string;
}

export function ResultsTable({ results, query }: ResultsTableProps) {
  const [copiedUrl, setCopiedUrl] = useState<string | null>(null);

  const copyToClipboard = async (url: string) => {
    try {
      await navigator.clipboard.writeText(url);
      setCopiedUrl(url);
      toast.success('Link copied to clipboard!');
      setTimeout(() => setCopiedUrl(null), 2000);
    } catch (err) {
      toast.error('Failed to copy link');
    }
  };

  if (!results || results.length === 0) {
    return (
      <Card className="p-6 sm:p-8 text-center border-2 border-orange-100 bg-gradient-to-br from-orange-50 to-red-50">
        <div className="max-w-md mx-auto space-y-2 sm:space-y-3">
          <div className="text-3xl sm:text-4xl">🔍</div>
          <h3 className="text-base sm:text-lg">No Matches Found</h3>
          <p className="text-xs sm:text-sm text-muted-foreground">
            Try adjusting your query or using different keywords.
          </p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Summary Card */}
      <Card className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200">
        <div className="flex items-start gap-3">
          <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-green-500 text-white shadow-md flex-shrink-0">
            <CheckCircle2 className="h-6 w-6" />
          </div>
          <div>
            <h3 className="text-green-800 text-sm sm:text-base">
              Found {results.length} relevant assessment{results.length > 1 ? 's' : ''}
            </h3>
            <p className="text-xs sm:text-sm text-green-700 mt-1 italic">
              “{query.substring(0, 80)}{query.length > 80 ? '...' : ''}”
            </p>
            <div className="flex items-center gap-2 mt-2 text-xs text-green-700">
              <Award className="h-3 w-3" /> Top matches first • <TrendingUp className="h-3 w-3" /> Ranked by relevance
            </div>
          </div>
        </div>
      </Card>

      {/* Mobile Cards */}
      <div className="block lg:hidden space-y-3">
        {results.map((assessment, index) => (
          <Card key={index} className="p-4 border border-indigo-100 hover:border-indigo-200 transition-colors">
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center gap-2">
                <Badge className="bg-indigo-600 text-white">#{index + 1}</Badge>
                {index < 3 && (
                  <Badge variant="outline" className="text-xs bg-yellow-50 border-yellow-300 text-yellow-700">
                    ⭐ Top
                  </Badge>
                )}
              </div>
              <div className="flex items-center gap-1">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => copyToClipboard(assessment.url)}
                        className="h-7 w-7 p-0 hover:bg-indigo-100"
                      >
                        {copiedUrl === assessment.url ? (
                          <CheckCircle2 className="h-4 w-4 text-green-600" />
                        ) : (
                          <Copy className="h-4 w-4 text-indigo-600" />
                        )}
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>Copy link</TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <a
                        href={assessment.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="h-7 w-7 inline-flex items-center justify-center rounded-md hover:bg-indigo-100 text-indigo-600 transition"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    </TooltipTrigger>
                    <TooltipContent>View details</TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-medium">{assessment.assessment_name}</h4>
              <p className="text-xs text-muted-foreground mt-1">{assessment.description}</p>
            </div>

            <div className="mt-2 flex flex-wrap gap-1">
              {assessment?.test_type?.length && assessment?.test_type?.map((type, i) => (
                <Badge key={i} variant="outline" className="text-[10px] bg-indigo-50 border-indigo-200 text-indigo-700">
                  {type}
                </Badge>
              ))}
            </div>

            <div className="mt-3 text-xs text-gray-600">
              <div><strong>Duration:</strong> {assessment.duration || 'N/A'}</div>
              <div><strong>Adaptive:</strong> {assessment.adaptive_support}</div>
              <div><strong>Remote:</strong> {assessment.remote_support}</div>
            </div>
          </Card>
        ))}
      </div>

      {/* Desktop Table */}
      <div className="hidden lg:block border-2 border-indigo-100 rounded-lg overflow-hidden bg-white shadow-md">
        <Table>
          <TableHeader>
            <TableRow className="bg-gradient-to-r from-indigo-50 to-purple-50 border-b-2 border-indigo-200">
              <TableHead className="w-[50px]">Rank</TableHead>
              <TableHead>Assessment Name</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Skills / Test Type</TableHead>
              <TableHead>Duration</TableHead>
              <TableHead>Adaptive</TableHead>
              <TableHead>Remote</TableHead>
              <TableHead>Link</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {results.map((assessment, index) => (
              <TableRow key={index} className="hover:bg-indigo-50/40 transition">
                <TableCell>#{index + 1}</TableCell>
                <TableCell className="font-medium">{assessment.assessment_name}</TableCell>
                <TableCell>{assessment.description}</TableCell>
                <TableCell>
                  <div className="flex flex-wrap gap-1">
                    {assessment.test_type.map((type, i) => (
                      <Badge key={i} variant="outline" className="text-[10px] bg-indigo-50 border-indigo-200 text-indigo-700">
                        {type}
                      </Badge>
                    ))}
                  </div>
                </TableCell>
                <TableCell>{assessment.duration || 'N/A'}</TableCell>
                <TableCell>{assessment.adaptive_support}</TableCell>
                <TableCell>{assessment.remote_support}</TableCell>
                <TableCell>
                  <div className="flex gap-1">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => copyToClipboard(assessment.url)}
                      className="h-8 w-8 p-0 hover:bg-indigo-100"
                    >
                      {copiedUrl === assessment.url ? (
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                      ) : (
                        <Copy className="h-4 w-4 text-indigo-600" />
                      )}
                    </Button>
                    <a
                      href={assessment.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center justify-center rounded-md h-8 w-8 hover:bg-indigo-100 text-indigo-600 transition"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
