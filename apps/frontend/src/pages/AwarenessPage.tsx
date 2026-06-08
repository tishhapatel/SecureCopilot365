import React, { useState, useEffect } from 'react';
import { Award, BookOpen, AlertTriangle, Sparkles, HelpCircle, Check, X } from 'lucide-react';
import { api } from '../lib/api';

export default function AwarenessPage() {
  const [topic, setTopic] = useState('');
  const [scenario, setScenario] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [responseStatus, setResponseStatus] = useState<any>(null);

  const loadScenario = async (topicTitle?: string) => {
    setLoading(true);
    setScenario(null);
    setSelectedOption(null);
    setSubmitted(false);
    setResponseStatus(null);

    try {
      const res = await api.getTrainingScenario(topicTitle || undefined);
      setScenario(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadScenario();
  }, []);

  const handleSubmit = async () => {
    if (selectedOption === null || !scenario) return;

    setSubmitted(true);
    const correct = selectedOption === scenario.interactive_scenario.correct_option_index;

    try {
      const res = await api.submitTrainingAnswer(scenario.topic, correct);
      setResponseStatus(res);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="flex-1 p-6 space-y-6 overflow-y-auto bg-darkBg text-gray-200">
      <div className="flex items-center justify-between border-b border-darkBorder pb-4">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-white flex items-center gap-2">
            Security Awareness Coach
          </h1>
          <p className="text-xs text-gray-400 mt-1">Interactive training modules personalized to your job role. Complete simulations to reduce employee risk indexes.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Left Topics list */}
        <div className="bg-darkCard border border-darkBorder rounded-2xl p-5 space-y-4 xl:col-span-1 h-fit">
          <h3 className="font-semibold text-sm text-white flex items-center gap-2">
            <BookOpen size={16} className="text-cyberBlue" /> Select Training Module
          </h3>
          <div className="space-y-2">
            {[
              "Business Email Compromise (BEC)",
              "GDPR Personal Data Protection",
              "OWASP Top 10 & API Secret Management",
              "Credential Phishing & Social Engineering"
            ].map(mod => (
              <button
                key={mod}
                onClick={() => { setTopic(mod); loadScenario(mod); }}
                className={`w-full text-left p-3 rounded-xl border text-xs font-semibold transition ${
                  topic === mod || (topic === '' && mod.includes("BEC"))
                    ? 'bg-cyberBlue/10 border-cyberBlue text-cyberBlue'
                    : 'border-darkBorder bg-darkBg/60 text-gray-400 hover:text-gray-300'
                }`}
              >
                {mod}
              </button>
            ))}
          </div>
        </div>

        {/* Right Sandbox Quiz */}
        <div className="bg-darkCard border border-darkBorder rounded-2xl p-5 xl:col-span-2 flex flex-col gap-4">
          <h3 className="font-semibold text-sm text-white flex items-center gap-2">
            <Award size={16} className="text-cyberGreen" /> Interactive Simulation
          </h3>

          {loading && (
            <div className="flex-1 flex flex-col items-center justify-center text-cyberBlue gap-2 py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyberBlue" />
              <span className="text-xs">Generating interactive role-specific dilemma...</span>
            </div>
          )}

          {!loading && !scenario && (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-500 text-xs py-12">
              <HelpCircle size={36} className="mb-2 text-darkBorder" />
              <span>Select training module to start training.</span>
            </div>
          )}

          {!loading && scenario && (
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-darkBorder pb-3">
                <div>
                  <span className="text-[10px] text-cyberBlue uppercase font-bold tracking-wider">{scenario.topic}</span>
                  <div className="text-xs font-semibold text-gray-300 mt-0.5">Objective: {scenario.learning_objective}</div>
                </div>
                <div className="text-right text-[10px] text-gray-400 font-medium bg-darkBg px-2 py-1 rounded-lg border border-darkBorder">
                  {scenario.role_relevance}
                </div>
              </div>

              {/* Scenario description */}
              <div className="p-4 bg-darkBg/60 rounded-2xl border border-darkBorder/40 leading-relaxed text-xs text-gray-200">
                <span className="font-bold text-cyberBlue mb-1 block">Context Scenario:</span>
                {scenario.interactive_scenario.intro}
              </div>

              {/* Options */}
              <div className="space-y-2.5">
                <span className="text-xs font-bold text-gray-400 uppercase">{scenario.interactive_scenario.question}</span>
                <div className="grid gap-2">
                  {scenario.interactive_scenario.options.map((opt: string, idx: number) => (
                    <button
                      key={idx}
                      onClick={() => !submitted && setSelectedOption(idx)}
                      disabled={submitted}
                      className={`w-full text-left p-3 rounded-xl border text-xs font-medium transition flex items-center justify-between ${
                        selectedOption === idx
                          ? submitted
                            ? idx === scenario.interactive_scenario.correct_option_index
                              ? 'bg-emerald-500/10 border-emerald-500 text-emerald-400'
                              : 'bg-red-500/10 border-red-500 text-red-400'
                            : 'bg-cyberBlue/10 border-cyberBlue text-cyberBlue'
                          : 'border-darkBorder bg-darkBg/30 text-gray-300 hover:border-darkBorder'
                      }`}
                    >
                      <span>{opt}</span>
                      {submitted && idx === scenario.interactive_scenario.correct_option_index && (
                        <Check size={14} className="text-emerald-400" />
                      )}
                      {submitted && selectedOption === idx && idx !== scenario.interactive_scenario.correct_option_index && (
                        <X size={14} className="text-red-400" />
                      )}
                    </button>
                  ))}
                </div>
              </div>

              {/* Action and feedback */}
              <div className="pt-2">
                {!submitted ? (
                  <button
                    onClick={handleSubmit}
                    disabled={selectedOption === null}
                    className="w-full bg-cyberBlue hover:bg-cyberBlue/90 disabled:bg-darkBorder disabled:text-gray-500 text-[#0a0d16] font-bold py-2 rounded-xl text-xs transition"
                  >
                    Submit Answer
                  </button>
                ) : (
                  <div className="space-y-4">
                    <div className="p-3 bg-darkBg/60 border border-darkBorder rounded-xl text-xs leading-relaxed text-gray-300">
                      <span className="font-semibold text-cyberBlue block mb-1">Explanation & Grounding:</span>
                      {scenario.interactive_scenario.explanation}
                    </div>

                    {responseStatus && (
                      <div className="p-3 bg-darkBg/30 border border-darkBorder rounded-xl flex items-center justify-between text-[10px]">
                        <span className="text-gray-400">Scorecard:</span>
                        <div className="flex gap-3 text-gray-300">
                          <span>New Awareness Score: <strong className="text-cyberBlue">{responseStatus.new_awareness_score}</strong></span>
                          <span>New Risk Score: <strong className="text-red-400">{responseStatus.new_risk_score}</strong></span>
                        </div>
                      </div>
                    )}

                    <button
                      onClick={() => loadScenario(scenario.topic)}
                      className="w-full bg-cyberGreen hover:bg-cyberGreen/90 text-[#0a0d16] font-bold py-2 rounded-xl text-xs transition shadow-glow"
                    >
                      Next Scenario Challenge
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
