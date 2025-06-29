'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PDFDownloadLink, Document, Page, Text, StyleSheet } from '@react-pdf/renderer';

interface CoverLetterResultProps {
  coverLetter: string;
  isLoading: boolean;
  error: string;
  onFeedback?: (feedback: string) => Promise<void>;
  showFeedback: boolean;
  setShowFeedback: (show: boolean) => void;
  progressMessage?: string;
}

// PDF styles
const pdfStyles = StyleSheet.create({
  page: {
    padding: 40,
    fontSize: 12,
    fontFamily: 'Helvetica',
    lineHeight: 1.6,
  },
  heading: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
    color: '#1A1A40',
  },
  body: {
    fontSize: 12,
    color: '#22223B',
  },
});

function CoverLetterPDF({ coverLetter }: { coverLetter: string }) {
  return (
    <Document>
      <Page size="A4" style={pdfStyles.page}>
        <Text style={pdfStyles.heading}>Cover Letter</Text>
        <Text style={pdfStyles.body}>{coverLetter}</Text>
      </Page>
    </Document>
  );
}

export default function CoverLetterResult({ 
  coverLetter, 
  isLoading, 
  error, 
  onFeedback,
  showFeedback,
  setShowFeedback,
  progressMessage
}: CoverLetterResultProps) {
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [showRating, setShowRating] = useState(false);
  const [rating, setRating] = useState<number | null>(null);

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

  // Progress bar steps for LangGraph flow
  const progressSteps = [
    { step: "Parsing resume...", icon: "📄", description: "Extracting your experience and skills" },
    { step: "Parsing job description...", icon: "🏢", description: "Analyzing job requirements" },
    { step: "Matching experiences...", icon: "🎯", description: "Finding relevant matches" },
    { step: "Generating cover letter...", icon: "✍️", description: "Creating your personalized letter" },
    { step: "Validating output...", icon: "✅", description: "Quality checking the result" }
  ];
  const currentStep = progressSteps.findIndex(step => progressMessage && progressMessage.trim().startsWith(step.step));
  const progressPercent = currentStep === -1 ? 0 : ((currentStep + 1) / progressSteps.length) * 100;

  return (
    <motion.div 
      className="h-full flex flex-col"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Disclaimer */}
      <motion.div
        className="mb-3 px-4 py-2 bg-yellow-50 border-l-4 border-yellow-400 text-yellow-800 rounded shadow-sm text-xs"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <span className="font-semibold">Note:</span> Generating your cover letter may take up to 30 seconds, especially during busy times.
      </motion.div>

      <motion.div variants={itemVariants} className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-navy-blue tracking-tight">Your Cover Letter</h2>
        <AnimatePresence>
          {coverLetter && !showFeedback && (
            <motion.div 
              className="flex items-center gap-2"
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
                title="Suggest changes or request a different tone, focus, etc."
              >
                Suggest Improvements
              </motion.button>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      <motion.div className="flex-1 flex flex-row gap-4">
        {/* Action Buttons: Always visible if coverLetter exists */}
        <div className="flex flex-col gap-2 items-center justify-start pt-2">
          {coverLetter && (
            <>
              <motion.button
                onClick={handleCopy}
                className={`btn-accent px-3 py-1.5 text-xs w-24 ${copied ? 'ring-2 ring-emerald-green' : ''}`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {copied ? '✓ Copied!' : 'Copy'}
              </motion.button>
              <motion.button
                onClick={handleDownload}
                className="btn-accent px-3 py-1.5 text-xs w-24"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Download
              </motion.button>
              <PDFDownloadLink
                document={<CoverLetterPDF coverLetter={coverLetter} />}
                fileName="cover_letter.pdf"
              >
                {({ loading }) => (
                  <motion.button
                    className="btn-accent px-3 py-1.5 text-xs w-24"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    {loading ? 'Preparing PDF...' : 'Download as PDF'}
                  </motion.button>
                )}
              </PDFDownloadLink>
            </>
          )}
        </div>
        <motion.div 
          className="flex-1 bg-white rounded-lg p-4 overflow-auto border border-gray-200"
          variants={itemVariants}
        >
          <AnimatePresence>
            {showFeedback && coverLetter && (
              <motion.div 
                className="mb-4 p-4 bg-emerald-green/10 rounded-lg border border-emerald-green"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3 }}
              >
                <h3 className="text-lg font-semibold text-emerald-green mb-2">Provide Feedback</h3>
                <p className="text-sm text-navy-blue mb-3">
                  Tell us what you&apos;d like to improve about this cover letter. We&apos;ll regenerate it with your feedback.
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
            {isLoading ? (
              <motion.div 
                key="loading"
                className="flex flex-col items-center justify-center h-full w-full"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.3 }}
              >
                {/* Enhanced Progress Steps */}
                <div className="w-full max-w-md mb-6">
                  <div className="space-y-3">
                    {progressSteps.map((step, index) => {
                      const isActive = index === currentStep;
                      const isCompleted = index < currentStep;
                      
                      return (
                        <motion.div
                          key={index}
                          className={`flex items-center space-x-3 p-2 rounded-lg transition-all duration-300 ${
                            isActive ? 'bg-emerald-green/10 border border-emerald-green' :
                            isCompleted ? 'bg-emerald-green/5' : 'bg-gray-50'
                          }`}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                        >
                          <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                            isActive ? 'bg-emerald-green text-white animate-pulse' :
                            isCompleted ? 'bg-emerald-green text-white' : 'bg-gray-200 text-gray-500'
                          }`}>
                            {isCompleted ? '✓' : step.icon}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className={`text-sm font-medium ${
                              isActive ? 'text-emerald-green' :
                              isCompleted ? 'text-navy-blue' : 'text-gray-500'
                            }`}>
                              {step.step}
                            </p>
                            <p className={`text-xs ${
                              isActive ? 'text-emerald-green' : 'text-gray-400'
                            }`}>
                              {step.description}
                            </p>
                          </div>
                          {isActive && (
                            <motion.div
                              className="w-2 h-2 bg-emerald-green rounded-full"
                              animate={{ scale: [1, 1.5, 1] }}
                              transition={{ duration: 1, repeat: Infinity }}
                            />
                          )}
                        </motion.div>
                      );
                    })}
                  </div>
                </div>
                
                {/* Overall Progress Bar */}
                <div className="w-full max-w-xs mb-4">
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <motion.div
                      className="h-2 bg-emerald-green"
                      initial={{ width: 0 }}
                      animate={{ width: `${progressPercent}%` }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
                  <div className="text-xs text-slate-gray mt-1 text-center">
                    {progressMessage || 'Starting generation...'}
                  </div>
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
                <div className="bg-white rounded-lg p-6 border border-gray-200">
                  <div className="space-y-4">
                    {coverLetter.split('\n\n').map((paragraph, index) => {
                      const isFirstParagraph = index === 0;
                      
                      return (
                        <motion.div
                          key={index}
                          className={`${
                            isFirstParagraph ? 'font-semibold text-navy-blue' : 'text-navy-blue'
                          } leading-relaxed`}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.1 }}
                        >
                          {paragraph.split('\n').map((line, lineIndex) => (
                            <p key={lineIndex} className="mb-2">
                              {line}
                            </p>
                          ))}
                        </motion.div>
                      );
                    })}
                  </div>
                  
                  {/* Letter Structure Guide */}
                  <motion.div
                    className="mt-6 p-3 bg-emerald-green/5 rounded-lg border border-emerald-green/20"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 }}
                  >
                    <p className="text-xs text-emerald-green font-medium mb-1">📋 Letter Structure</p>
                    <div className="text-xs text-slate-gray space-y-1">
                      <p>• <span className="font-medium">Opening:</span> Greeting and position statement</p>
                      <p>• <span className="font-medium">Body:</span> Relevant experiences, <span className='font-medium'>or</span> transferable skills and strengths honestly drawn from your resume</p>
                      <p>• <span className="font-medium">Closing:</span> Interest reinforcement and call to action</p>
                    </div>
                    <p className="text-xs text-slate-gray mt-2">
                      <span className="font-medium">Note:</span> If you don't have direct experience for the job, your letter will honestly highlight transferable skills, strengths, or relevant qualities from your resume. We never fabricate experience, but always do our best to connect your real background to the job requirements.
                    </p>
                  </motion.div>
                  
                  {/* Rating and Feedback */}
                  {!showRating && (
                    <motion.div
                      className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.7 }}
                    >
                      <p className="text-sm font-medium text-navy-blue mb-3">Was this cover letter helpful?</p>
                      <div className="flex items-center justify-between">
                        <div className="flex space-x-2">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <motion.button
                              key={star}
                              onClick={() => {
                                setRating(star);
                                setShowRating(true);
                              }}
                              className={`text-2xl ${
                                star <= (rating || 0) ? 'text-yellow-400' : 'text-gray-300'
                              } hover:text-yellow-400 transition-colors`}
                              whileHover={{ scale: 1.1 }}
                              whileTap={{ scale: 0.9 }}
                            >
                              ★
                            </motion.button>
                          ))}
                        </div>
                        <motion.button
                          onClick={() => setShowFeedback(true)}
                          className="text-sm text-emerald-green hover:text-emerald-600 font-medium"
                          whileHover={{ scale: 1.05 }}
                        >
                          Suggest improvements →
                        </motion.button>
                      </div>
                    </motion.div>
                  )}
                  
                  {/* Rating Feedback */}
                  {showRating && rating && (
                    <motion.div
                      className="mt-6 p-4 bg-emerald-green/10 rounded-lg border border-emerald-green"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      <p className="text-sm text-emerald-green font-medium mb-2">
                        {rating >= 4 ? '🎉 Great!' : rating >= 3 ? '👍 Good!' : '🤔 Thanks for the feedback!'}
                      </p>
                      <p className="text-xs text-navy-blue">
                        {rating >= 4 
                          ? 'We\'re glad this cover letter meets your needs!' 
                          : 'We\'d love to improve it. Try the "Suggest improvements" button above.'
                        }
                      </p>
                    </motion.div>
                  )}
                </div>
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
    </motion.div>
  );
} 