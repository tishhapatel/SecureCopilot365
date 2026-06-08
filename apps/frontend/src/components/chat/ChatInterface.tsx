import React, { useState, useRef, useEffect } from 'react';
import { Send, Shield, Sparkles, AlertTriangle, FileText, ChevronRight } from 'lucide-react';
import { api } from '../../lib/api';

interface Message {
  id: string;
  sender: 'user' | 'copilot';
  text: string;
  agent?: string;
  citations?: string[];
  citationDetails?: string[];
}

export default function ChatInterface() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'copilot',
      text: "Hello! I am SecureCopilot 365. I can help you analyze email headers for phishing, check policy compliance, score vendor risks, assess audit readiness, or run a security awareness session. What security query can I help you with today?"
    }
  ]);
  const [loading, setLoading] = useState(false);
  const [activeCitation, setActiveCitation] = useState<string | null>(null);
  
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMsg: Message = {
      id: Math.random().toString(),
      sender: 'user',
      text: query
    };

    setMessages(prev => [...prev, userMsg]);
    setQuery('');
    setLoading(true);

    try {
      const result = await api.sendCopilotChat(userMsg.text);
      const copilotResponse = result.analysis;
      
      let responseText = "";
      let citationsList: string[] = [];
      let detailsList: string[] = [];

      if (result.agent_executed === 'phishing') {
        responseText = `**Verdict:** ${copilotResponse.verdict.toUpperCase()} (Risk Score: ${copilotResponse.risk_score}/100)\n\n${copilotResponse.summary}\n\n**Recommendation:** ${copilotResponse.recommended_action}`;
        citationsList = copilotResponse.citations || [];
        detailsList = (copilotResponse.indicators || []).map((i: any) => `${i.category}: ${i.description} [MITRE: ${i.mitre_technique || 'None'}]`);
      } else if (result.agent_executed === 'compliance') {
        responseText = `**Compliance Assessment** (Score: ${copilotResponse.compliance_score}/100)\n\n${copilotResponse.overall_recommendation}\n\n**Detected Gaps:** ${copilotResponse.gaps.length} gaps identified.`;
        citationsList = (copilotResponse.gaps || []).map((g: any) => g.citation);
        detailsList = (copilotResponse.gaps || []).map((g: any) => `[${g.framework} ${g.control_ref}] ${g.title}: ${g.description}. Remediation: ${g.remediation}`);
      } else if (result.agent_executed === 'vendor') {
        responseText = `**Vendor TPRM Scorecard: ${copilotResponse.vendor_name}**\n\n**Risk Tier:** ${copilotResponse.risk_tier.toUpperCase()} (Score: ${copilotResponse.risk_score}/100)\n\n${copilotResponse.risk_summary}`;
        citationsList = (copilotResponse.findings || []).map((f: any) => f.citation);
        detailsList = (copilotResponse.findings || []).map((f: any) => `[Finding] ${f.finding}. Recommendation: ${f.recommendation}`);
      } else if (result.agent_executed === 'audit') {
        responseText = `**Audit Readiness Report: ${copilotResponse.framework}**\n\n**Status:** ${copilotResponse.readiness_band.toUpperCase()} (Readiness: ${copilotResponse.overall_readiness_score}%)\n\n${copilotResponse.executive_summary}`;
        citationsList = ["ISO 27001 Annex A", "NIST CSF 2.0"];
        detailsList = (copilotResponse.critical_gaps || []).map((g: any) => `Gap: ${g.control_ref} - ${g.control_name}. Needed: ${g.evidence_needed}`);
      } else {
        responseText = `${copilotResponse.learning_objective}\n\n**Scenario:** ${copilotResponse.interactive_scenario.intro}\n\n**Question:** ${copilotResponse.interactive_scenario.question}`;
        citationsList = copilotResponse.citations || [];
        detailsList = [copilotResponse.interactive_scenario.explanation];
      }

      setMessages(prev => [...prev, {
        id: Math.random().toString(),
        sender: 'copilot',
        text: responseText,
        agent: result.agent_executed,
        citations: citationsList,
        citationDetails: detailsList
      }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        id: Math.random().toString(),
        sender: 'copilot',
        text: "I encountered an error processing your query. Please confirm your local backend is running."
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#121724] border-l border-darkBorder w-80 md:w-96">
      {/* Header */}
      <div className="p-4 border-b border-darkBorder bg-[#0a0d16] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-cyberBlue/10 text-cyberBlue">
            <Shield size={18} />
          </div>
          <div>
            <h3 className="font-semibold text-sm">SecureCopilot 365</h3>
            <span className="text-[10px] text-cyberBlue font-medium tracking-wider uppercase flex items-center gap-1">
              <Sparkles size={10} className="animate-pulse" /> Active Guard
            </span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(msg => (
          <div key={msg.id} className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`p-3 rounded-2xl max-w-[85%] text-xs leading-relaxed ${
              msg.sender === 'user' 
                ? 'bg-cyberBlue text-[#0a0d16] font-medium rounded-tr-none' 
                : 'bg-darkBg border border-darkBorder text-gray-200 rounded-tl-none'
            }`}>
              <div className="whitespace-pre-wrap">{msg.text}</div>
              
              {msg.agent && (
                <div className="mt-2 pt-2 border-t border-darkBorder/40 flex justify-between items-center text-[10px] text-gray-400">
                  <span className="capitalize">Agent: {msg.agent}</span>
                </div>
              )}
            </div>

            {/* Grounding Citations */}
            {msg.citations && msg.citations.length > 0 && (
              <div className="mt-1 flex flex-wrap gap-1 max-w-[85%]">
                {msg.citations.map((cit, idx) => (
                  <button
                    key={idx}
                    onClick={() => setActiveCitation(activeCitation === `${msg.id}-${idx}` ? null : `${msg.id}-${idx}`)}
                    className="text-[10px] bg-darkCard hover:bg-darkBorder border border-darkBorder/60 px-2 py-0.5 rounded text-cyberBlue font-medium transition flex items-center gap-0.5"
                  >
                    <FileText size={10} /> {cit.split("—")[0].trim()}
                  </button>
                ))}
              </div>
            )}

            {/* Citation Details Dropdown */}
            {msg.citations && msg.citations.map((cit, idx) => {
              const key = `${msg.id}-${idx}`;
              if (activeCitation !== key) return null;
              const detail = msg.citationDetails?.[idx] || "No detailed citation parameters loaded.";
              return (
                <div key={key} className="mt-2 p-2 rounded bg-darkBg/90 border border-cyberBlue/30 text-[10px] text-gray-300 max-w-[85%] shadow-glow">
                  <div className="font-semibold text-cyberBlue mb-1 flex items-center gap-1">
                    <Sparkles size={10} /> Grounding Source
                  </div>
                  <div>{detail}</div>
                </div>
              );
            })}
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <div className="w-1.5 h-1.5 bg-cyberBlue rounded-full animate-ping" />
            <span>SecureCopilot is analyzing...</span>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSend} className="p-3 border-t border-darkBorder bg-[#0a0d16]">
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Ask Copilot to analyze email, vendor..."
            className="w-full bg-darkBg border border-darkBorder rounded-xl py-2 pl-3 pr-10 text-xs focus:outline-none focus:border-cyberBlue transition text-gray-200"
          />
          <button
            type="submit"
            className="absolute right-1.5 top-1/2 -translate-y-1/2 p-1.5 rounded-lg bg-cyberBlue/10 hover:bg-cyberBlue/20 text-cyberBlue transition"
          >
            <Send size={12} />
          </button>
        </div>
      </form>
    </div>
  );
}
