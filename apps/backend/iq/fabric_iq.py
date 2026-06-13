"""
Fabric IQ Layer
Semantic Ontology. Links security findings, MITRE ATT&CK techniques, and compliance controls.
Enables AI agents to trace business relationships: Employee -> Vendor -> Control -> Framework -> Risk.
"""
import logging
from typing import List, Dict, Any, Set

logger = logging.getLogger(__name__)

class FabricIQ:
    def __init__(self):
        # In-memory graph nodes representation
        self.nodes: Dict[str, Dict[str, Any]] = {}
        # adjacency list for graph edges
        self.edges: Dict[str, List[Dict[str, Any]]] = {}
        
        # Maps MITRE techniques to compliance controls
        self.mitre_to_compliance = {
            "T1566.001": [
                {"framework": "ISO27001", "control": "A.6.3", "title": "Information security awareness"},
                {"framework": "NIST", "control": "PR.AT-1", "title": "Awareness training"}
            ],
            "T1566.002": [
                {"framework": "ISO27001", "control": "A.8.20", "title": "Network security"},
                {"framework": "GDPR", "control": "Article 32", "title": "Security of processing"}
            ],
            "T1598": [
                {"framework": "ISO27001", "control": "A.6.3", "title": "Information security awareness"}
            ],
            "T1534": [
                {"framework": "ISO27001", "control": "A.5.15", "title": "Access control"},
                {"framework": "GDPR", "control": "Article 32", "title": "Security of processing"}
            ]
        }
        
        # Populate initial business ontology
        self._initialize_default_graph()

    def _initialize_default_graph(self):
        # Nodes
        self.add_node("emp-tisha", "Employee", "Tisha Patel", {"department": "Finance", "job_title": "Billing Specialist"})
        self.add_node("vendor-saas", "Vendor", "SaaS Platform Corp", {"risk_score": 58, "data_categories": ["PII", "Billing"]})
        self.add_node("control-mfa", "Control", "MFA Enforcement", {"status": "partial", "framework": "ISO27001", "control_ref": "A.5.15"})
        self.add_node("control-supplier", "Control", "Supplier Security Management", {"status": "missing", "framework": "ISO27001", "control_ref": "A.5.19"})
        self.add_node("framework-iso", "Framework", "ISO 27001", {"version": "2022"})
        self.add_node("framework-gdpr", "Framework", "GDPR", {"compliance_score": 75})
        self.add_node("risk-leakage", "Risk", "Cross-tenant Data Leakage", {"likelihood": "high", "impact": "critical"})
        self.add_node("incident-phish", "Incident", "Credential Phishing Attempt", {"threat_id": "T1566.002"})

        # Edges (Relationships)
        self.add_edge("emp-tisha", "vendor-saas", "USES")
        self.add_edge("vendor-saas", "risk-leakage", "EXPOSES")
        self.add_edge("control-supplier", "vendor-saas", "MITIGATES")
        self.add_edge("control-mfa", "risk-leakage", "MITIGATES")
        self.add_edge("control-supplier", "framework-iso", "MAPPED_TO")
        self.add_edge("control-mfa", "framework-iso", "MAPPED_TO")
        self.add_edge("incident-phish", "emp-tisha", "TARGETS")
        self.add_edge("incident-phish", "control-mfa", "EXPLOITS")

    def add_node(self, node_id: str, node_type: str, label: str, properties: Dict[str, Any] = None):
        """Register a node in the semantic graph."""
        self.nodes[node_id] = {
            "id": node_id,
            "type": node_type,
            "label": label,
            "properties": properties or {}
        }
        if node_id not in self.edges:
            self.edges[node_id] = []

    def add_edge(self, source_id: str, target_id: str, relationship: str, strength: float = 1.0):
        """Register a directed relationship edge between nodes."""
        if source_id in self.nodes and target_id in self.nodes:
            self.edges[source_id].append({
                "target": target_id,
                "relationship": relationship,
                "strength": strength
            })
            # Also register back-relation for easy traversal
            if target_id not in self.edges:
                self.edges[target_id] = []
            self.edges[target_id].append({
                "target": source_id,
                "relationship": f"INVERSE_{relationship}",
                "strength": strength
            })

    def get_controls_for_technique(self, technique_id: str) -> list:
        """Returns compliance mappings for a detected MITRE technique."""
        return self.mitre_to_compliance.get(technique_id, [])

    def map_threat_to_risk(self, threat_name: str) -> str:
        """Estimates risk category based on threat keywords."""
        t = threat_name.lower()
        if "bec" in t or "wire" in t or "cfo" in t:
            return "critical"
        if "phish" in t or "credential" in t:
            return "high"
        return "medium"

    def traverse_impact(self, start_node_id: str, max_depth: int = 3) -> Dict[str, Any]:
        """
        Traverses relationships to evaluate the upstream compliance and risk impacts
        starting from a given node (e.g. an incident or a compromised vendor).
        """
        if start_node_id not in self.nodes:
            return {"error": f"Node {start_node_id} not found in knowledge graph."}

        impacted_nodes: Dict[str, Dict[str, Any]] = {}
        visited: Set[str] = set()

        def dfs(curr_id: str, depth: int):
            if depth > max_depth or curr_id in visited:
                return
            visited.add(curr_id)
            
            for edge in self.edges.get(curr_id, []):
                target_id = edge["target"]
                target_node = self.nodes[target_id]
                rel = edge["relationship"]
                
                # We skip inverse traversals to follow cause -> effect
                if not rel.startswith("INVERSE_"):
                    if target_id not in impacted_nodes:
                        impacted_nodes[target_id] = {
                            "node": target_node,
                            "path": f"{self.nodes[curr_id]['label']} --[{rel}]--> {target_node['label']}"
                        }
                    dfs(target_id, depth + 1)

        dfs(start_node_id, 1)
        return {
            "origin": self.nodes[start_node_id],
            "impacts": list(impacted_nodes.values())
        }

