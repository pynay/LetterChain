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
  const [originalFormData, setOriginalFormData] = useState<CoverLetterFormData | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [progressMessage, setProgressMessage] = useState<string>('');

  const handleGenerateCoverLetter = async (formData: CoverLetterFormData) => {
    setIsLoading(true);
    setError('');
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

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/generate-stream`, {
        method: 'POST',
        body: data,
      });
      if (!response.body) throw new Error('No response body');
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      let done = false;
      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        buffer += value ? decoder.decode(value, { stream: true }) : '';
        let lines = buffer.split(/\n\n/);
        buffer = lines.pop() || '';
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const msg = line.slice(6);
            if (msg.startsWith('FINAL_COVER_LETTER::')) {
              const jsonStr = msg.replace('FINAL_COVER_LETTER::', '');
              try {
                const obj = JSON.parse(jsonStr);
                setCoverLetter(obj.cover_letter);
              } catch (e) {
                setError('Error parsing cover letter result');
              }
            } else if (msg === 'done') {
              setIsLoading(false);
            } else {
              setProgressMessage(msg);
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
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
      <div className="max-w-4xl mx-auto">
        <motion.div 
          className="text-center mb-8"
          variants={itemVariants}
        >
          <motion.h1 
            className="text-4xl font-bold text-navy-blue mb-2"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            Cover Letter Generator
          </motion.h1>
          <motion.p 
            className="text-lg text-slate-gray"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            Upload your resume and job description to generate a personalized cover letter
          </motion.p>
        </motion.div>

        <motion.div 
          className="grid lg:grid-cols-2 gap-8"
          variants={itemVariants}
        >
          <motion.div 
            className="bg-white rounded-xl shadow-lg p-6"
            whileHover={{ 
              y: -5,
              boxShadow: "0 20px 40px rgba(0,0,0,0.1)"
            }}
            transition={{ duration: 0.3 }}
          >
            <CoverLetterForm 
              onSubmit={handleGenerateCoverLetter}
              isLoading={isLoading}
            />
          </motion.div>

          <motion.div 
            className="bg-white rounded-xl shadow-lg p-6"
            whileHover={{ 
              y: -5,
              boxShadow: "0 20px 40px rgba(0,0,0,0.1)"
            }}
            transition={{ duration: 0.3 }}
          >
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
        </motion.div>

        {/* Agents Explanation Section */}
        <motion.div
          variants={itemVariants}
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          <AgentsExplanation />
        </motion.div>
      </div>
    </motion.main>
  );
}
