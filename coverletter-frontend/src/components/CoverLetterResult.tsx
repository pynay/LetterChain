'use client';

import { useState } from 'react';

interface CoverLetterResultProps {
  coverLetter: string;
  isLoading: boolean;
  error: string;
  onFeedback?: (feedback: string) => Promise<void>;
  showFeedback: boolean;
  setShowFeedback: (show: boolean) => void;
}

export default function CoverLetterResult({ 
  coverLetter, 
  isLoading, 
  error, 
  onFeedback,
  showFeedback,
  setShowFeedback
}: CoverLetterResultProps) {
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState('');

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(coverLetter);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([coverLetter], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'cover_letter.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleFeedbackSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (onFeedback && feedback.trim()) {
      await onFeedback(feedback);
      setFeedback('');
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold text-gray-900">Generated Cover Letter</h2>
        {coverLetter && !showFeedback && (
          <div className="flex gap-2">
            <button
              onClick={() => setShowFeedback(true)}
              className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Provide Feedback
            </button>
            <button
              onClick={handleCopy}
              className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              {copied ? '✓ Copied!' : 'Copy'}
            </button>
            <button
              onClick={handleDownload}
              className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Download
            </button>
          </div>
        )}
      </div>

      {showFeedback && coverLetter && (
        <div className="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 className="text-lg font-medium text-blue-900 mb-2">Provide Feedback</h3>
          <p className="text-sm text-blue-700 mb-3">
            Tell us what you'd like to improve about this cover letter. We'll regenerate it with your feedback.
          </p>
          <form onSubmit={handleFeedbackSubmit} className="space-y-3">
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              rows={3}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm resize-none"
              placeholder="e.g., Make it more confident, focus on leadership experience, mention specific projects..."
              required
            />
            <div className="flex gap-2">
              <button
                type="submit"
                disabled={isLoading || !feedback.trim()}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Regenerating...' : 'Regenerate with Feedback'}
              </button>
              <button
                type="button"
                onClick={() => setShowFeedback(false)}
                className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="flex-1 bg-gray-50 rounded-lg p-4 overflow-auto">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <svg className="animate-spin h-8 w-8 text-blue-600 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <p className="text-gray-600">
                {showFeedback ? 'Regenerating your cover letter...' : 'Generating your cover letter...'}
              </p>
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="text-red-500 mb-2">
                <svg className="h-8 w-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <p className="text-red-600 font-medium">Error</p>
              <p className="text-gray-600 text-sm mt-1">{error}</p>
            </div>
          </div>
        ) : coverLetter ? (
          <div className="prose prose-sm max-w-none">
            <pre className="whitespace-pre-wrap font-sans text-gray-800 leading-relaxed">
              {coverLetter}
            </pre>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500">
              <svg className="h-12 w-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-lg font-medium">Ready to generate</p>
              <p className="text-sm">Upload your resume and job description to get started</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 