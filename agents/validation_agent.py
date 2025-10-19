"""Validation Agent - Validates extracted fields against policies using RAG"""
import json
from typing import Dict, List, Any
from groq import Groq
import config
from rag.vector_store import VectorStore

class ValidationAgent:
    """Agent for validating form fields against bank policies"""
    
    def __init__(self, vector_store: VectorStore = None):
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = config.LLM_MODEL
        
        # Load vector store
        if vector_store:
            self.vector_store = vector_store
        else:
            self.vector_store = VectorStore()
            try:
                self.vector_store.load()
            except FileNotFoundError:
                print("⚠️ Vector store not found. Please build it first.")
                self.vector_store = None
    
    def validate(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted form data against policies"""
        print("🔍 Validating form data...")
        
        if not self.vector_store:
            return {
                "error": "Vector store not available",
                "status": "ERROR"
            }
        
        # Step 1: Retrieve relevant policies
        form_type = extracted_data.get('form_type', 'Unknown')
        relevant_policies = self._retrieve_policies(form_type, extracted_data)
        
        print(f"📚 Retrieved {len(relevant_policies)} relevant policy documents")
        
        # Step 2: Validate using LLM with retrieved context
        validation_result = self._validate_with_llm(extracted_data, relevant_policies)
        
        return validation_result
    
    def _retrieve_policies(self, form_type: str, extracted_data: Dict) -> List[Dict]:
        """Retrieve relevant policies from vector store"""
        
        # Create search queries
        queries = [
            f"{form_type} requirements eligibility",
            f"{form_type} documents needed",
            f"{form_type} age limits",
            f"{form_type} validation rules"
        ]
        
        # Add specific field-based queries
        if 'extracted_fields' in extracted_data:
            for field_name in list(extracted_data['extracted_fields'].keys())[:5]:
                queries.append(f"{form_type} {field_name} requirements")
        
        # Retrieve documents
        all_results = []
        seen_docs = set()
        
        for query in queries:
            results = self.vector_store.search(query, top_k=3)
            for result in results:
                doc_text = result['document']
                if doc_text not in seen_docs:
                    seen_docs.add(doc_text)
                    all_results.append(result)
        
        return all_results[:config.TOP_K_RESULTS * 2]  # Return top results
    
    def _validate_with_llm(self, extracted_data: Dict, policies: List[Dict]) -> Dict:
        """Validate form data using LLM with policy context"""
        
        # Prepare context from policies
        policy_context = "\n\n".join([
            f"POLICY DOCUMENT {i+1}:\n{policy['document']}"
            for i, policy in enumerate(policies)
        ])
        
        # Prepare extracted data summary
        form_summary = json.dumps(extracted_data, indent=2)
        
        prompt = f"""You are a bank form validation expert. Your task is to validate the extracted form data against the bank's policies.

EXTRACTED FORM DATA:
{form_summary}

RELEVANT BANK POLICIES:
{policy_context}

Based on the policies, validate the form and provide:

1. **Completeness Check**: Are all required fields filled?
2. **Policy Compliance**: Does the data comply with bank policies?
3. **Specific Violations**: List any policy violations with details
4. **Missing Information**: What information is missing?
5. **Recommendations**: What should be corrected or added?
6. **Final Status**: APPROVED / REJECTED / NEEDS_REVIEW

Return your analysis in the following JSON format:
{{
  "status": "APPROVED/REJECTED/NEEDS_REVIEW",
  "completeness_score": 0-100,
  "compliance_score": 0-100,
  "missing_fields": ["list of missing required fields"],
  "policy_violations": [
    {{
      "field": "field name",
      "issue": "description of violation",
      "policy": "relevant policy rule",
      "severity": "high/medium/low"
    }}
  ],
  "recommendations": ["list of recommendations"],
  "summary": "Brief summary of validation result"
}}

Be thorough and specific in your validation."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a bank form validation expert. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content
            
            # Extract JSON from response
            result = self._extract_json(result_text)
            
            # Add metadata
            result['form_type'] = extracted_data.get('form_type', 'Unknown')
            result['policies_checked'] = len(policies)
            
            return result
            
        except Exception as e:
            print(f"❌ Error validating form: {e}")
            return {
                "error": str(e),
                "status": "ERROR",
                "summary": "Validation failed due to technical error"
            }
    
    def _extract_json(self, text: str) -> Dict:
        """Extract JSON from LLM response"""
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
            else:
                return json.loads(text)
        except json.JSONDecodeError:
            print("⚠️ Could not parse JSON from response")
            return {
                "error": "JSON parsing failed",
                "raw_response": text,
                "status": "ERROR"
            }
    
    def generate_report(self, extracted_data: Dict, validation_result: Dict) -> str:
        """Generate a human-readable validation report"""
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║           BANK FORM VALIDATION REPORT                        ║
╚══════════════════════════════════════════════════════════════╝

Form Type: {extracted_data.get('form_type', 'Unknown')}
Status: {validation_result.get('status', 'Unknown')}

SCORES:
  • Completeness: {validation_result.get('completeness_score', 0)}%
  • Compliance: {validation_result.get('compliance_score', 0)}%

"""
        
        # Missing fields
        missing = validation_result.get('missing_fields', [])
        if missing:
            report += "⚠️  MISSING REQUIRED FIELDS:\n"
            for field in missing:
                report += f"  • {field}\n"
            report += "\n"
        
        # Policy violations
        violations = validation_result.get('policy_violations', [])
        if violations:
            report += "❌ POLICY VIOLATIONS:\n"
            for v in violations:
                report += f"  • {v.get('field', 'Unknown')}: {v.get('issue', 'Unknown issue')}\n"
                report += f"    Policy: {v.get('policy', 'N/A')}\n"
                report += f"    Severity: {v.get('severity', 'Unknown')}\n\n"
        
        # Recommendations
        recommendations = validation_result.get('recommendations', [])
        if recommendations:
            report += "💡 RECOMMENDATIONS:\n"
            for rec in recommendations:
                report += f"  • {rec}\n"
            report += "\n"
        
        # Summary
        report += f"SUMMARY:\n{validation_result.get('summary', 'No summary available')}\n"
        
        report += "\n" + "="*60 + "\n"
        
        return report

if __name__ == "__main__":
    # Test validation agent
    agent = ValidationAgent()
    
    # Example extracted data
    test_data = {
        "form_type": "Personal Loan Application",
        "extracted_fields": {
            "name": {"value": "John Doe", "type": "text"},
            "age": {"value": "17", "type": "number"},
            "loan_amount": {"value": "500000", "type": "number"}
        },
        "unfilled_fields": ["signature", "pan_number"]
    }
    
    result = agent.validate(test_data)
    print(json.dumps(result, indent=2))
