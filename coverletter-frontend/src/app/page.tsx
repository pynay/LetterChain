'use client';

import { useState } from 'react';
import CoverLetterForm from '@/components/CoverLetterForm';
import CoverLetterResult from '@/components/CoverLetterResult';
import type { FormData as CoverLetterFormData } from '@/types';

export default function Home() {
  const [coverLetter, setCoverLetter] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [originalFormData, setOriginalFormData] = useState<CoverLetterFormData | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);

  const handleGenerateCoverLetter = async (formData: CoverLetterFormData) => {
    setIsLoading(true);
    setError('');
    setShowFeedback(false);
    
    // Store original form data for feedback
    setOriginalFormData(formData);
    
    try {
      const data = new FormData();
      data.append('resume', formData.resumeFile!);
      
      // Create a text file for job description
      const jobBlob = new Blob([formData.jobDescription], { type: 'text/plain' });
      const jobFile = new File([jobBlob], 'job_description.txt', { type: 'text/plain' });
      data.append('job', jobFile);
      data.append('tone', formData.tone);

      const response = await fetch('http://localhost:8000/generate', {
        method: 'POST',
        body: data,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.text();
      setCoverLetter(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
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

      const response = await fetch('http://localhost:8000/feedback', {
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

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Cover Letter Generator
          </h1>
          <p className="text-lg text-gray-600">
            Upload your resume and job description to generate a personalized cover letter
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <CoverLetterForm 
              onSubmit={handleGenerateCoverLetter}
              isLoading={isLoading}
            />
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <CoverLetterResult 
              coverLetter={coverLetter}
              isLoading={isLoading}
              error={error}
              onFeedback={handleFeedback}
              showFeedback={showFeedback}
              setShowFeedback={setShowFeedback}
            />
          </div>
        </div>
      </div>
    </main>
  );
}
