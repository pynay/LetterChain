'use client';

import { motion } from 'framer-motion';

const technicalAgents = [
  {
    id: 1,
    name: 'Job Parser Node',
    description: 'Extracts structured information from job postings',
    technicalDetails: [
      'Parses job descriptions into structured JSON format',
      'Extracts: title, company, required_skills[], values[], summary',
      'Uses regex pattern matching for response extraction',
      'Implements error handling for malformed responses'
    ],
    icon: '🔍',
    color: 'from-blue-500 to-blue-600',
    delay: 0.1,
    model: 'Claude-3-Sonnet'
  },
  {
    id: 2,
    name: 'Resume Parser Node',
    description: 'Extracts candidate information from resumes',
    technicalDetails: [
      'Converts resume text into structured candidate data',
      'Extracts: name, summary, experiences[], skills[], education[]',
      'Deduplicates skills and experiences automatically',
      'Handles missing or incomplete data gracefully'
    ],
    icon: '📄',
    color: 'from-purple-500 to-purple-600',
    delay: 0.2,
    model: 'Claude-3-Sonnet'
  },
  {
    id: 3,
    name: 'Relevance Matcher Node',
    description: 'Matches candidate experiences to job requirements',
    technicalDetails: [
      'Compares resume data with job requirements',
      'Selects 2-3 highly relevant experiences',
      'Maps skills to specific job responsibilities',
      'Returns matched experiences with reasoning'
    ],
    icon: '🎯',
    color: 'from-emerald-500 to-emerald-600',
    delay: 0.3,
    model: 'Claude-3-Sonnet'
  },
  {
    id: 4,
    name: 'Cover Letter Generator',
    description: 'Generates personalized cover letter content',
    technicalDetails: [
      'Creates tailored cover letter using matched experiences',
      'Incorporates tone preferences and company information',
      'Supports iterative refinement with feedback',
      'Maintains optimal length and structure'
    ],
    icon: '✍️',
    color: 'from-orange-500 to-orange-600',
    delay: 0.4,
    model: 'Claude-Opus'
  },
  {
    id: 5,
    name: 'Validator Node',
    description: 'Quality assurance and validation',
    technicalDetails: [
      'Validates cover letter against strict criteria',
      'Checks company/job mention accuracy',
      'Ensures experience relevance and tone consistency',
      'Provides detailed feedback for improvements'
    ],
    icon: '✅',
    color: 'from-red-500 to-red-600',
    delay: 0.5,
    model: 'Claude-3-Sonnet'
  }
];

const langGraphFlow = [
  { step: 1, node: 'parse_job', description: 'Job Parser Node', next: 'parse_resume' },
  { step: 2, node: 'parse_resume', description: 'Resume Parser Node', next: 'match' },
  { step: 3, node: 'match', description: 'Relevance Matcher Node', next: 'generate' },
  { step: 4, node: 'generate', description: 'Cover Letter Generator', next: 'validate' },
  { step: 5, node: 'validate', description: 'Validator Node', next: 'conditional' },
  { step: 6, node: 'export', description: 'Export Node', next: 'finish' }
];

export default function AgentsExplanation() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="mt-16 bg-white rounded-xl shadow-lg p-8"
    >
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="text-center mb-8"
      >
        <h2 className="text-3xl font-bold text-navy-blue mb-3">
          LangGraph Architecture
        </h2>
        <p className="text-lg text-slate-gray max-w-3xl mx-auto">
          Multi-agent system built with LangGraph, featuring specialized AI models for each processing stage
        </p>
      </motion.div>

      {/* Technical Architecture Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.6 }}
        className="mb-12 p-6 bg-gradient-to-r from-slate-50 to-blue-50 rounded-lg border border-slate-200"
      >
        <h3 className="text-xl font-semibold text-navy-blue mb-4">How It Works</h3>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-navy-blue mb-2">Smart, Seamless Experience</h4>
            <div className="bg-slate-100 p-3 rounded text-sm">
              <div className="mb-2">Upload your resume (PDF, Word, or TXT) and paste in a job description.</div>
              <ul className="list-disc ml-6 text-slate-600">
                <li>Our system instantly reads and understands your resume—no manual reformatting required.</li>
                <li>Advanced AI matches your experience to the job, then writes a tailored, confident cover letter in real time.</li>
                <li>See your letter stream in live, so you're never left waiting in the dark.</li>
                <li>Want changes? Suggest improvements and get a new draft instantly—no need to start over.</li>
                <li>All your data is processed securely and never used for training.</li>
              </ul>
            </div>
          </div>
          <div>
            <h4 className="font-semibold text-navy-blue mb-2">What Makes It Special?</h4>
            <div className="bg-slate-100 p-3 rounded text-sm">
              <ul className="list-disc ml-6 text-slate-600">
                <li><span className="font-semibold text-emerald-green">Real-time AI:</span> See your cover letter generate as you watch.</li>
                <li><span className="font-semibold text-emerald-green">Multi-format support:</span> Upload PDF, DOCX, or TXT resumes—no conversion needed.</li>
                <li><span className="font-semibold text-emerald-green">Validation loop:</span> Every letter is double-checked by a second AI for quality and honesty. If it doesn't meet the bar, the system automatically revises and improves it before you see the result.</li>
                <li><span className="font-semibold text-emerald-green">Feedback loop:</span> Instantly refine your letter with your own suggestions.</li>
                <li><span className="font-semibold text-emerald-green">Reliable & secure:</span> Built with robust cloud tech, so your data and experience are always safe.</li>
                <li><span className="font-semibold text-emerald-green">Powered by top-tier AI:</span> Uses advanced models for the best results.</li>
              </ul>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Technical Agent Details */}
      <div className="grid lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-12">
        {technicalAgents.map((agent) => (
          <motion.div
            key={agent.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: agent.delay, duration: 0.5 }}
            whileHover={{ 
              scale: 1.02,
              transition: { duration: 0.2 }
            }}
            className="bg-white rounded-lg p-6 border border-gray-200 shadow-sm hover:shadow-lg transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-4">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: agent.delay + 0.1, type: "spring", stiffness: 200 }}
                className="text-3xl"
              >
                {agent.icon}
              </motion.div>
              <div className="text-xs bg-slate-100 px-2 py-1 rounded font-mono">
                {agent.model}
              </div>
            </div>
            
            <h3 className="text-lg font-semibold text-navy-blue mb-2">
              {agent.name}
            </h3>
            
            <p className="text-sm text-slate-gray mb-3 leading-relaxed">
              {agent.description}
            </p>

            <div className="space-y-2">
              {agent.technicalDetails.map((detail, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: agent.delay + 0.2 + idx * 0.1 }}
                  className="text-xs text-slate-600 flex items-start"
                >
                  <span className="text-emerald-green mr-2">•</span>
                  {detail}
                </motion.div>
              ))}
            </div>

            <motion.div
              initial={{ width: 0 }}
              animate={{ width: "100%" }}
              transition={{ delay: agent.delay + 0.5, duration: 0.8 }}
              className={`mt-4 h-1 bg-gradient-to-r ${agent.color} rounded-full`}
            />
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
} 