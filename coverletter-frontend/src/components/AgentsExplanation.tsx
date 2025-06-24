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
        <h3 className="text-xl font-semibold text-navy-blue mb-4">System Architecture</h3>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-navy-blue mb-2">State Management</h4>
            <div className="bg-slate-100 p-3 rounded text-sm font-mono">
              <div>CoverLetterState(TypedDict):</div>
              <div className="ml-4 text-slate-600">
                job_posting: str<br/>
                resume_posting: str<br/>
                tone: str<br/>
                job_info: dict<br/>
                resume_info: dict<br/>
                matched_experiences: List[dict]<br/>
                cover_letter: str<br/>
                validation_result: dict<br/>
                prior_issues: Optional[List[str]]<br/>
                export_path: Optional[str]<br/>
                user_name: Optional[str]
              </div>
            </div>
          </div>
          <div>
            <h4 className="font-semibold text-navy-blue mb-2">Flow Control</h4>
            <div className="bg-slate-100 p-3 rounded text-sm font-mono">
              <div>Conditional Edge Logic:</div>
              <div className="ml-4 text-slate-600">
                validate_branch(state) →<br/>
                <span className="ml-4">if validation_result.valid:</span><br/>
                <span className="ml-6">return "export"</span><br/>
                <span className="ml-4">else:</span><br/>
                <span className="ml-6">return "generate"</span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Technical Agent Details */}
      <div className="grid lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-12">
        {technicalAgents.map((agent, index) => (
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

      {/* LangGraph Flow Diagram */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8, duration: 0.6 }}
        className="mb-12 p-6 bg-gradient-to-r from-emerald-green/5 to-blue-500/5 rounded-lg border border-emerald-green/20"
      >
        <div className="text-center mb-6">
          <h3 className="text-xl font-semibold text-navy-blue mb-2">
            LangGraph Execution Flow
          </h3>
          <p className="text-slate-gray">
            StateGraph with conditional edges and iterative refinement
          </p>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-4">
          {langGraphFlow.map((flow, index) => (
            <motion.div
              key={flow.step}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 1 + index * 0.1, duration: 0.5 }}
              className="flex flex-col items-center"
            >
              <motion.div
                whileHover={{ scale: 1.1 }}
                className={`w-16 h-16 rounded-full flex items-center justify-center text-white font-semibold text-lg
                  ${
                    flow.node === 'export'
                      ? 'bg-emerald-green'
                      : flow.node === 'conditional'
                      ? 'bg-orange-500'
                      : 'bg-navy-blue'
                  }
                `}
              >
                {flow.step}
              </motion.div>
              <span className="text-xs text-slate-gray mt-2 text-center max-w-20">
                {flow.description}
              </span>
              <span className="text-xs font-mono text-emerald-green mt-1">
                {flow.node}
              </span>
              
              {index < langGraphFlow.length - 1 && (
                <motion.div
                  initial={{ scaleX: 0 }}
                  animate={{ scaleX: 1 }}
                  transition={{ delay: 1.2 + index * 0.1, duration: 0.3 }}
                  className="w-12 h-0.5 bg-gradient-to-r from-emerald-green to-navy-blue mt-4"
                />
              )}
            </motion.div>
          ))}
        </div>

        {/* Conditional Flow Explanation */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.8, duration: 0.6 }}
          className="mt-8 p-4 bg-slate-100 rounded-lg"
        >
          <h4 className="font-semibold text-navy-blue mb-2">Conditional Logic</h4>
          <div className="text-sm text-slate-600 font-mono">
            <div>validate_branch(state) →</div>
            <div className="ml-4">
              if validation_result.get("valid", False):<br/>
              <span className="ml-6 text-emerald-green">→ "export" (success)</span><br/>
              else:<br/>
              <span className="ml-6 text-orange-600">→ "generate" (retry with prior_issues)</span>
            </div>
          </div>
        </motion.div>
      </motion.div>

      {/* Technical Specifications */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.5, duration: 0.6 }}
        className="grid md:grid-cols-3 gap-6"
      >
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="text-center p-4 bg-emerald-green/10 rounded-lg"
        >
          <div className="text-2xl mb-2">⚡</div>
          <h4 className="font-semibold text-navy-blue">State Management</h4>
          <p className="text-sm text-slate-gray">TypedDict with optional fields</p>
          <div className="text-xs font-mono text-emerald-green mt-2">
            CoverLetterState
          </div>
        </motion.div>
        
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="text-center p-4 bg-blue-500/10 rounded-lg"
        >
          <div className="text-2xl mb-2">🔄</div>
          <h4 className="font-semibold text-navy-blue">Iterative Refinement</h4>
          <p className="text-sm text-slate-gray">Validation-driven retry loop</p>
          <div className="text-xs font-mono text-blue-600 mt-2">
            prior_issues[]
          </div>
        </motion.div>
        
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="text-center p-4 bg-purple-500/10 rounded-lg"
        >
          <div className="text-2xl mb-2">🎯</div>
          <h4 className="font-semibold text-navy-blue">Model Optimization</h4>
          <p className="text-sm text-slate-gray">Specialized models per task</p>
          <div className="text-xs font-mono text-purple-600 mt-2">
            Claude-3-Sonnet + Opus
          </div>
        </motion.div>
      </motion.div>

      {/* Response Processing */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 2.0, duration: 0.6 }}
        className="mt-8 p-6 bg-slate-50 rounded-lg border border-slate-200"
      >
        <h4 className="font-semibold text-navy-blue mb-3">Response Processing</h4>
        <div className="grid md:grid-cols-2 gap-4 text-sm">
          <div>
            <h5 className="font-semibold text-slate-700 mb-2">Data Extraction</h5>
            <div className="bg-slate-100 p-3 rounded font-mono text-xs">
              <div>Structured JSON extraction from AI responses</div>
              <div className="text-slate-500 mt-1">Pattern matching and validation</div>
            </div>
          </div>
          <div>
            <h5 className="font-semibold text-slate-700 mb-2">Error Handling</h5>
            <div className="bg-slate-100 p-3 rounded font-mono text-xs">
              <div>Graceful fallback for malformed responses</div>
              <div className="text-slate-500 mt-1">State preservation and recovery</div>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
} 