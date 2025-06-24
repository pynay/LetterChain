'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

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

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, x: 20 },
    visible: {
      opacity: 1,
      x: 0,
      transition: { duration: 0.5 }
    }
  };

  return (
    <motion.div 
      className="h-full flex flex-col"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={itemVariants} className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-navy-blue tracking-tight">Your Cover Letter</h2>
        <AnimatePresence>
          {coverLetter && !showFeedback && (
            <motion.div 
              className="flex gap-2"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.3 }}
            >
              <motion.button
                onClick={() => setShowFeedback(true)}
                className="btn-accent px-3 py-1.5 text-xs"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Provide Feedback
              </motion.button>
              <motion.button
                onClick={handleCopy}
                className={`btn-accent px-3 py-1.5 text-xs ${copied ? 'ring-2 ring-emerald-green' : ''}`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {copied ? '✓ Copied!' : 'Copy'}
              </motion.button>
              <motion.button
                onClick={handleDownload}
                className="btn-accent px-3 py-1.5 text-xs"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Download
              </motion.button>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      <AnimatePresence>
        {showFeedback && coverLetter && (
          <motion.div 
            className="mb-4 p-4 bg-emerald-green/10 rounded-lg border border-emerald-green"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <h3 className="text-lg font-semibold text-emerald-green mb-2">Provide Feedback</h3>
            <p className="text-sm text-navy-blue mb-3">
              Tell us what you'd like to improve about this cover letter. We'll regenerate it with your feedback.
            </p>
            <form onSubmit={handleFeedbackSubmit} className="space-y-3">
              <textarea
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                rows={3}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-green focus:ring-emerald-green sm:text-sm resize-none bg-white text-navy-blue"
                placeholder="e.g., Make it more confident, focus on leadership experience, mention specific projects..."
                required
              />
              <div className="flex gap-2">
                <motion.button
                  type="submit"
                  disabled={isLoading || !feedback.trim()}
                  className="btn-primary px-4 py-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {isLoading ? 'Regenerating...' : 'Regenerate with Feedback'}
                </motion.button>
                <motion.button
                  type="button"
                  onClick={() => setShowFeedback(false)}
                  className="btn-accent px-4 py-2 text-sm"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Cancel
                </motion.button>
              </div>
            </form>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div 
        className="flex-1 bg-white rounded-lg p-4 overflow-auto border border-gray-200"
        variants={itemVariants}
      >
        <AnimatePresence mode="wait">
          {isLoading ? (
            <motion.div 
              key="loading"
              className="flex items-center justify-center h-full"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.3 }}
            >
              <div className="text-center">
                <motion.svg 
                  className="h-8 w-8 text-navy-blue mx-auto mb-4" 
                  xmlns="http://www.w3.org/2000/svg" 
                  fill="none" 
                  viewBox="0 0 24 24"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                >
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </motion.svg>
                <motion.p 
                  className="text-navy-blue"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.2 }}
                >
                  {showFeedback ? 'Regenerating your cover letter...' : 'Generating your cover letter...'}
                </motion.p>
              </div>
            </motion.div>
          ) : error ? (
            <motion.div 
              key="error"
              className="flex items-center justify-center h-full"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <div className="text-center">
                <motion.div 
                  className="text-red-500 mb-2"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.1, type: "spring" }}
                >
                  <svg className="h-8 w-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </motion.div>
                <p className="text-red-600 font-medium">Error</p>
                <p className="text-navy-blue text-sm mt-1">{error}</p>
              </div>
            </motion.div>
          ) : coverLetter ? (
            <motion.div 
              key="result"
              className="prose prose-sm max-w-none"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
            >
              <pre className="whitespace-pre-wrap font-sans text-navy-blue leading-relaxed">
                {coverLetter}
              </pre>
            </motion.div>
          ) : (
            <motion.div 
              key="empty"
              className="flex items-center justify-center h-full"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.3 }}
            >
              <div className="text-center text-slate-gray">
                <motion.svg 
                  className="h-12 w-12 mx-auto mb-4 text-emerald-green" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.2, type: "spring" }}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </motion.svg>
                <motion.p 
                  className="text-lg font-medium"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.3 }}
                >
                  Ready to generate
                </motion.p>
                <motion.p 
                  className="text-sm"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.4 }}
                >
                  Upload your resume and job description to get started
                </motion.p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  );
} 