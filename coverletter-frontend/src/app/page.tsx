'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import CoverLetterForm from '@/components/CoverLetterForm';
import CoverLetterResult from '@/components/CoverLetterResult';
import AgentsExplanation from '@/components/AgentsExplanation';
import type { FormData as CoverLetterFormData } from '@/types';

export default function Home() {
  const [coverLetter, setCoverLetter] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [hasError, setHasError] = useState(false);
  const [originalFormData, setOriginalFormData] = useState<CoverLetterFormData | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [progressMessage, setProgressMessage] = useState<string>('');

  const handleGenerateCoverLetter = async (formData: CoverLetterFormData) => {
    setIsLoading(true);
    setError('');
    setHasError(false);
    setShowFeedback(false);
    setProgressMessage('');
    setCoverLetter('');
    setOriginalFormData(formData);
    try {
      const data = new FormData();
      data.append('resume', formData.resumeFile!);
      const jobBlob = new Blob([formData.jobDescription], { type: 'text/plain' });
      const jobFile = new File([jobBlob], 'job_description.txt', { type: 'text/plain' });
      data.append('job', jobFile);
      data.append('tone', formData.tone);

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/generate-stream`, {
        method: 'POST',
        body: data,
      });
      if (!response.ok) {
        const errorText = await response.text();
        setError(errorText || 'An error occurred');
        setHasError(true);
        setIsLoading(false);
        return;
      }
      if (!response.body) throw new Error('No response body');
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      let done = false;
      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        buffer += value ? decoder.decode(value, { stream: true }) : '';
        const lines = buffer.split(/\n\n/);
        buffer = lines.pop() || '';
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const msg = line.slice(6);
            
            // Handle the new backend format with JSON messages
            if (msg === 'done') {
              setIsLoading(false);
            } else {
              try {
                const jsonData = JSON.parse(msg);
                
                // Handle status updates
                if (jsonData.status) {
                  setProgressMessage(jsonData.status);
                }
                
                // Handle final result with cover letter
                if (jsonData.cover_letter) {
                  setCoverLetter(jsonData.cover_letter);
                  setShowFeedback(true);
                  setIsLoading(false);
                }
                
                // Handle error messages
                if (jsonData.error) {
                  setError(jsonData.error.message || 'An error occurred');
                  setHasError(true);
                  setIsLoading(false);
                }
                
                // Handle the full state object (backend sends this at the end)
                if (jsonData.resume_posting && jsonData.job_posting && jsonData.cover_letter) {
                  setCoverLetter(jsonData.cover_letter);
                  setShowFeedback(true);
                  setIsLoading(false);
                }
                
              } catch {
                // Fallback to old format for backward compatibility
                if (msg.startsWith('FINAL_COVER_LETTER::')) {
                  const jsonStr = msg.replace('FINAL_COVER_LETTER::', '');
                  try {
                    const obj = JSON.parse(jsonStr);
                    setCoverLetter(obj.cover_letter);
                    setShowFeedback(true);
                  } catch {
                    setError('Error parsing cover letter result');
                    setHasError(true);
                  }
                } else if (msg.startsWith('ERROR::')) {
                  const errorMsg = msg.replace('ERROR::', '');
                  setError(errorMsg);
                  setHasError(true);
                  setIsLoading(false);
                } else {
                  setProgressMessage(msg);
                }
              }
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setHasError(true);
      setIsLoading(false);
    }
  };

  const handleFeedback = async (feedback: string) => {
    if (!originalFormData) return;
    
    setIsLoading(true);
    setError('');
    
    try {
      const data = new FormData();
      data.append('resume', originalFormData.resumeFile!);
      
      // Create a text file for job description
      const jobBlob = new Blob([originalFormData.jobDescription], { type: 'text/plain' });
      const jobFile = new File([jobBlob], 'job_description.txt', { type: 'text/plain' });
      data.append('job', jobFile);
      data.append('tone', originalFormData.tone);
      data.append('user_feedback', feedback);
      data.append('current_cover_letter', coverLetter);

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/feedback`, {
        method: 'POST',
        body: data,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setCoverLetter(result.cover_letter);
      setShowFeedback(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        duration: 0.8,
        staggerChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6 }
    }
  };

  return (
    <motion.main 
      className="min-h-screen bg-gradient-to-br from-gray-50 to-slate-100 py-8 px-4"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <div className="max-w-xl mx-auto">
        {/* Show the form if not loading and no cover letter */}
        {(!isLoading && !coverLetter && !hasError) && (
          <motion.div
            className="bg-white rounded-2xl shadow-lg border border-neutral-200/50 p-8"
            variants={itemVariants}
          >
            <CoverLetterForm
              onSubmit={handleGenerateCoverLetter}
              isLoading={isLoading}
            />
          </motion.div>
        )}

        {/* Show the result/progress if loading or after generation */}
        {(isLoading || coverLetter || hasError) && (
          <motion.div
            className="relative bg-white rounded-2xl shadow-lg border border-neutral-200/50 p-8 max-w-4xl mx-auto"
            variants={itemVariants}
          >
            {/* Start Over button at top, centered */}
            {!isLoading && (
              <div className="flex justify-center mb-8">
                <button
                  className="btn-accent text-base px-6 py-3 rounded-full font-semibold flex items-center gap-2 shadow-md"
                  onClick={() => {
                    setCoverLetter('');
                    setError('');
                    setHasError(false);
                    setShowFeedback(false);
                    setProgressMessage('');
                    setOriginalFormData(null);
                  }}
                  title="Start Over"
                >
                  <span className="text-lg">🔄</span>
                  <span>Start Over</span>
                </button>
              </div>
            )}
            <CoverLetterResult
              coverLetter={coverLetter}
              isLoading={isLoading}
              error={error}
              onFeedback={handleFeedback}
              showFeedback={showFeedback}
              setShowFeedback={setShowFeedback}
              progressMessage={progressMessage}
            />
          </motion.div>
        )}
      </div>

      {/* Agents Explanation Section */}
      <motion.div
        variants={itemVariants}
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.6 }}
      >
        <AgentsExplanation />
      </motion.div>
    </motion.main>
  );
}
