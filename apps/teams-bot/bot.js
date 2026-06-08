/**
 * SecureCopilot 365 — Teams Bot Application
 * Handles incoming chat activities, invokes AI agents, and returns adaptive cards.
 */

const express = require('express');
const { BotFrameworkAdapter, CardFactory } = require('botbuilder');
const fetch = require('node-fetch');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

// Create adapter. See https://aka.ms/about-bot-adapter to learn more about adapters.
const adapter = new BotFrameworkAdapter({
    appId: process.env.MicrosoftAppId || '',
    appPassword: process.env.MicrosoftAppPassword || ''
});

// Catch-all for errors.
adapter.onTurnError = async (context, error) => {
    console.error(`\n [onTurnError] Unhandled error: ${error}`);
    // Send a message to the user
    await context.sendActivity('The bot encountered an error or bug. Please check logs.');
};

// Create the Express server
const server = express();
const port = process.env.port || process.env.PORT || 3978;
server.listen(port, () => {
    console.log(`\nSecureCopilot 365 Teams Bot listening to http://localhost:${port}`);
});

server.use(express.json());

// Listen for incoming activities
server.post('/api/messages', (req, res) => {
    adapter.processActivity(req, res, async (context) => {
        if (context.activity.type === 'message') {
            const query = context.activity.text ? context.activity.text.trim() : '';

            // Handle card submissions (actions)
            if (context.activity.value && context.activity.value.action) {
                await handleCardAction(context, context.activity.value);
                return;
            }

            if (!query) {
                await context.sendActivity('Please type a security query or check an email.');
                return;
            }

            await context.sendActivity('🔍 Processing query with SecureCopilot 365 AI Orchestrator...');

            try {
                // Call local FastAPI backend Orchestrator endpoint
                const backendUrl = process.env.BACKEND_API_URL || 'http://localhost:8000/api/v1';
                
                // Set up authorization header. In development, the backend automatically uses mock fallback.
                const headers = {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${process.env.MOCK_ACCESS_TOKEN || 'mock-token'}`
                };

                const response = await fetch(`${backendUrl}/agents/chat`, {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({ query: query })
                });

                if (!response.ok) {
                    const errText = await response.text();
                    throw new Error(`Backend response failed (${response.status}): ${errText}`);
                }

                const data = await response.json();
                
                // Handle response depending on which agent executed
                const agent = data.agent_executed;
                const analysis = data.analysis;

                if (agent === 'phishing') {
                    // Load and bind adaptive card
                    const cardTemplatePath = path.join(__dirname, 'cards', 'phishing_card.json');
                    let cardJsonString = fs.readFileSync(cardTemplatePath, 'utf8');

                    // Simple string replacement for template variables
                    cardJsonString = cardJsonString
                        .replace(/\${emailSubject}/g, analysis.email_subject || 'Urgent Security Notice')
                        .replace(/\${senderDomain}/g, analysis.sender_domain || 'external-spoof.com')
                        .replace(/\${riskScore}/g, analysis.risk_score || '90')
                        .replace(/\${riskLevel}/g, (analysis.risk_level || 'CRITICAL').toUpperCase())
                        .replace(/\${mitreTechniques}/g, JSON.stringify(analysis.mitre_techniques || ['T1566.002']))
                        .replace(/\${indicators}/g, (analysis.indicators || []).map(ind => `• [${ind.category}] ${ind.description}`).join('\\n'));

                    const cardJson = JSON.parse(cardJsonString);
                    const attachment = CardFactory.adaptiveCard(cardJson);
                    await context.sendActivity({ attachments: [attachment] });
                } else if (agent === 'compliance') {
                    let msg = `📋 **Compliance Advice & Verification**\n\n`;
                    msg += `**Gaps Found**: ${analysis.gaps_found || 0}\n\n`;
                    if (analysis.gap_details && analysis.gap_details.length > 0) {
                        analysis.gap_details.forEach((gap, index) => {
                            msg += `**${index + 1}. [${gap.framework}] ${gap.title}** (Risk: ${gap.risk_level})\n`;
                            msg += `*Description*: ${gap.description}\n`;
                            msg += `*Remediation*: _${gap.remediation}_\n\n`;
                        });
                    } else {
                        msg += `✅ No compliance gaps identified in the input document context.`;
                    }
                    await context.sendActivity(msg);
                } else if (agent === 'vendor') {
                    let msg = `🏢 **Vendor Risk Management Assessment**\n\n`;
                    msg += `**Vendor**: ${analysis.vendor_name || 'Vendor'}\n`;
                    msg += `**Risk Score**: **${analysis.risk_score}/100** (${analysis.risk_level})\n`;
                    msg += `**Questionnaire Score**: ${analysis.questionnaire_score}%\n`;
                    msg += `**ISO 27001 Certified**: ${analysis.iso27001_certified ? 'Yes ✅' : 'No ❌'}\n`;
                    msg += `**SOC 2 Type II**: ${analysis.soc2_type2 ? 'Yes ✅' : 'No ❌'}\n`;
                    msg += `**GDPR DPA Signed**: ${analysis.gdpr_dpa_signed ? 'Yes ✅' : 'No ❌'}\n\n`;
                    msg += `**Assessment Notes**: ${analysis.notes || 'N/A'}`;
                    await context.sendActivity(msg);
                } else if (agent === 'audit') {
                    let msg = `📊 **M365 Audit Readiness Summary**\n\n`;
                    msg += `**Framework**: ${analysis.framework || 'ISO27001'}\n`;
                    msg += `**Overall Score**: **${analysis.overall_score}%**\n`;
                    msg += `**Controls Evidenced**: ${analysis.controls_evidenced} / ${analysis.controls_total}\n`;
                    msg += `**Controls Missing**: ${analysis.controls_missing}\n\n`;
                    if (analysis.critical_gaps && analysis.critical_gaps.length > 0) {
                        msg += `⚠️ **Critical Gaps identified**:\n`;
                        analysis.critical_gaps.forEach(gap => {
                            msg += `• [${gap.control_ref}] ${gap.control_name}: ${gap.gap_description} (Needs: ${gap.evidence_needed})\n`;
                        });
                    }
                    await context.sendActivity(msg);
                } else {
                    // Default / Awareness coach
                    let msg = `💡 **SecureCopilot Awareness Coach**\n\n`;
                    msg += `${analysis.feedback || analysis.scenario || 'Please start an interactive training session!'}\n\n`;
                    if (analysis.quiz) {
                        msg += `**Quiz Question**: ${analysis.quiz.question}\n\n`;
                        analysis.quiz.options.forEach((opt, idx) => {
                            msg += `${idx + 1}. ${opt}\n`;
                        });
                        msg += `\n*Reply with the correct option number to answer.*`;
                    }
                    await context.sendActivity(msg);
                }
            } catch (error) {
                console.error('Error contacting backend:', error);
                await context.sendActivity(`❌ Unable to reach SecureCopilot 365 backend services. Details: ${error.message}`);
            }
        }
    });
});

// Handle submit action from adaptive cards
async function handleCardAction(context, data) {
    if (data.action === 'report_soc') {
        await context.sendActivity(`🚨 **Threat Reported to SOC**\nSubject: _${data.subject}_\nSender: _${data.sender}_\n\nThank you for securing our workspace!`);
    } else if (data.action === 'mark_safe') {
        await context.sendActivity(`✅ **Marked as Safe**\nSubject: _${data.subject}_\n\nThe sender has been temporarily whitelisted.`);
    } else {
        await context.sendActivity(`Unknown action received: ${JSON.stringify(data)}`);
    }
}
