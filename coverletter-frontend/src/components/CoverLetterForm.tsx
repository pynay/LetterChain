'use client';

import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import type { FormData as CoverLetterFormData } from '@/types';

interface CoverLetterFormProps {
  onSubmit: (formData: CoverLetterFormData) => Promise<void>;
  isLoading: boolean;
}

export default function CoverLetterForm({ onSubmit, isLoading }: CoverLetterFormProps) {
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [tone, setTone] = useState('Professional, concise, and clearly tailored to the role. Direct, specific, and achievement-focused. Avoids filler, excessive warmth, or verbosity.');
  
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
    hidden: { opacity: 0, x: -20 },
    visible: {
      opacity: 1,
      x: 0,
      transition: { duration: 0.5 }
    }
  };

  return (
    <motion.form
      onSubmit={handleSubmit}
      className="space-y-6"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={itemVariants}>
        <h2 className="text-2xl font-bold text-navy-blue mb-4 tracking-tight">Upload & Details</h2>
      </motion.div>

      {/* Resume Upload */}
      <motion.div variants={itemVariants}>
        <label htmlFor="resume" className="block text-sm font-medium text-navy-blue mb-2">
          Resume (PDF, DOCX, or TXT)
        </label>
        <p className="text-xs text-slate-gray mb-2">
          Upload your resume in PDF, Word, or text format. We&apos;ll extract your experience and skills to match with the job.
        </p>
        <motion.div
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <input
            ref={fileInputRef}
            type="file"
            id="resume"
            accept=".pdf,.docx,.txt"
            onChange={handleFileChange}
            className="file-input-styled"
            required
          />
        </motion.div>
        {resumeFile && (
          <motion.p
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className="mt-2 text-sm text-emerald-green"
          >
            ✓ {resumeFile.name} selected
          </motion.p>
        )}
        <p className="text-xs text-slate-gray mt-1">
          💡 <span className="font-medium">Tip:</span> Make sure your resume includes your work experience, skills, and education
        </p>
      </motion.div>

      {/* Job Description */}
      <motion.div variants={itemVariants}>
        <label htmlFor="jobDescription" className="block text-sm font-medium text-navy-blue mb-2">
          Job Description
        </label>
        <p className="text-xs text-slate-gray mb-2">
          Paste the complete job description from LinkedIn, company website, or job board.
        </p>
        <motion.div
          whileFocus={{ scale: 1.01 }}
          transition={{ duration: 0.2 }}
        >
          <textarea
            id="jobDescription"
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            rows={6}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-green focus:ring-emerald-green sm:text-sm resize-none bg-white text-navy-blue"
            placeholder="Paste the full job description here... Include job title, company name, responsibilities, requirements, and any company information."
            required
          />
        </motion.div>
        <p className="text-xs text-slate-gray mt-1">
          💡 <span className="font-medium">Tip:</span> The more detailed the job description, the better we can tailor your cover letter
        </p>
      </motion.div>

      {/* Tone Selection */}
      <motion.div variants={itemVariants}>
        <label htmlFor="tone" className="block text-sm font-medium text-navy-blue mb-2">
          Writing Tone
        </label>
        <p className="text-xs text-slate-gray mb-2">
          Choose the tone that best matches your personality and the company culture.
        </p>
        <motion.div
          whileHover={{ scale: 1.01 }}
          whileFocus={{ scale: 1.01 }}
        >
          <select
            id="tone"
            value={tone}
            onChange={(e) => setTone(e.target.value)}
            className="block w-full rounded-md border-neutral-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm bg-white text-neutral-900"
          >
            <option value="Professional, concise, and clearly tailored to the role. Direct, specific, and achievement-focused. Avoids filler, excessive warmth, or verbosity.">
              🧑‍💼 Professional & Concise — Direct, specific, and achievement-focused
            </option>
            <option value="Emotionally intelligent, detailed, and clearly tailored to the role and mission. Shows initiative, reflection, and care — top-tier cover letter.">
              🧠 Emotionally Intelligent & Detailed — Insightful and thorough
            </option>
            <option value="Confident, enthusiastic, and results-oriented. Emphasizes achievements and impact.">
              💪 Confident & Enthusiastic — Bold and achievement-focused
            </option>
            <option value="Creative, innovative, and forward-thinking. Shows unique perspective and problem-solving approach.">
              🚀 Creative & Innovative — Unique perspective and problem-solving
            </option>
          </select>
        </motion.div>
      </motion.div>

      {/* Submit Button */}
      <motion.div variants={itemVariants}>
        <motion.button
          type="submit"
          disabled={isLoading || !resumeFile || !jobDescription.trim()}
          className="w-full btn-primary flex justify-center items-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          whileHover={{ 
            scale: 1.02,
            boxShadow: "0 10px 25px rgba(0,0,0,0.15)"
          }}
          whileTap={{ scale: 0.98 }}
          transition={{ duration: 0.2 }}
        >
          {isLoading ? (
            <motion.div 
              className="flex items-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <motion.svg 
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" 
                xmlns="http://www.w3.org/2000/svg" 
                fill="none" 
                viewBox="0 0 24 24"
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              >
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </motion.svg>
              Generating...
            </motion.div>
          ) : (
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              Generate Cover Letter
            </motion.span>
          )}
        </motion.button>
      </motion.div>
    </motion.form>
  );
} 