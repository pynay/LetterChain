'use client';

import { useState, useRef } from 'react';
import type { FormData as CoverLetterFormData } from '@/types';

interface CoverLetterFormProps {
  onSubmit: (formData: CoverLetterFormData) => Promise<void>;
  isLoading: boolean;
}

export default function CoverLetterForm({ onSubmit, isLoading }: CoverLetterFormProps) {
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [tone, setTone] = useState('Emotionally intelligent, detailed, and clearly tailored to the role and mission. Shows initiative, reflection, and care — top-tier cover letter.');
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!resumeFile || !jobDescription.trim()) {
      alert('Please upload a resume and provide a job description');
      return;
    }

    const formData: CoverLetterFormData = {
      resumeFile,
      jobDescription,
      tone
    };

    await onSubmit(formData);
    
    // Reset form
    setResumeFile(null);
    setJobDescription('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setResumeFile(file);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">Input Details</h2>
      </div>

      {/* Resume Upload */}
      <div>
        <label htmlFor="resume" className="block text-sm font-medium text-gray-700 mb-2">
          Resume (PDF or TXT)
        </label>
        <input
          ref={fileInputRef}
          type="file"
          id="resume"
          accept=".pdf,.txt"
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          required
        />
        {resumeFile && (
          <p className="mt-2 text-sm text-green-600">
            ✓ {resumeFile.name} selected
          </p>
        )}
      </div>

      {/* Job Description */}
      <div>
        <label htmlFor="jobDescription" className="block text-sm font-medium text-gray-700 mb-2">
          Job Description
        </label>
        <textarea
          id="jobDescription"
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          rows={6}
          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm resize-none"
          placeholder="Paste the job description here..."
          required
        />
      </div>

      {/* Tone Selection */}
      <div>
        <label htmlFor="tone" className="block text-sm font-medium text-gray-700 mb-2">
          Writing Tone
        </label>
        <select
          id="tone"
          value={tone}
          onChange={(e) => setTone(e.target.value)}
          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        >
          <option value="Emotionally intelligent, detailed, and clearly tailored to the role and mission. Shows initiative, reflection, and care — top-tier cover letter.">
            Professional & Detailed
          </option>
          <option value="Confident, enthusiastic, and results-oriented. Emphasizes achievements and impact.">
            Confident & Enthusiastic
          </option>
          <option value="Conversational, authentic, and personable. Shows personality while remaining professional.">
            Conversational & Authentic
          </option>
          <option value="Concise, direct, and focused on key qualifications and achievements.">
            Concise & Direct
          </option>
        </select>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading || !resumeFile || !jobDescription.trim()}
        className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? (
          <div className="flex items-center">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Generating...
          </div>
        ) : (
          'Generate Cover Letter'
        )}
      </button>
    </form>
  );
} 