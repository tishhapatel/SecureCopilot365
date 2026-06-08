"""
Fabric IQ Layer
Semantic Ontology. Links security findings, MITRE ATT&CK techniques, and compliance controls.
"""
class FabricIQ:
    def __init__(self):
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

    def get_controls_for_technique(self, technique_id: str) -> list:
        """
        Returns compliance mappings for a detected MITRE technique.
        """
        return self.mitre_to_compliance.get(technique_id, [])

    def map_threat_to_risk(self, threat_name: str) -> str:
        """
        Estimates risk category based on threat keywords.
        """
        t = threat_name.lower()
        if "bec" in t or "wire" in t or "cfo" in t:
            return "critical"
        if "phish" in t or "credential" in t:
            return "high"
        return "medium"
