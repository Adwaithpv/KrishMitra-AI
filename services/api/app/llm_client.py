"""
Simple LLM client for generating answers from retrieved evidence.
Supports both Google Gemini and local models.
"""

import os
from typing import List, Dict, Any
import json

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from transformers import pipeline
except ImportError:
    pipeline = None


class LLMClient:
    def __init__(self):
        self.gemini_model = None
        self.local_pipeline = None
        self._setup_client()
    
    def _setup_client(self):
        """Setup either Google Gemini or local model"""
        # Try Gemini first
        if genai and os.getenv("GEMINI_API_KEY"):
            try:
                api_key = os.getenv("GEMINI_API_KEY")
                if api_key:
                    genai.configure(api_key=api_key)
                    self.gemini_model = genai.GenerativeModel('gemini-2.5-flash-lite')
                    print("Gemini client initialized successfully")
                    return
            except Exception as e:
                print(f"Failed to initialize Gemini client: {e}")
                self.gemini_model = None
        
        # Skip local model to avoid TensorFlow issues
        print("Using fallback text generation (no LLM)")
        self.local_pipeline = None
    
    def generate_answer(self, query: str, evidence: List[Dict[str, Any]], language: str | None = None) -> str:
        """Generate an answer from query and evidence"""
        if not evidence:
            return "I don't have enough information to answer this question."
        
        # Format evidence for prompt
        evidence_text = self._format_evidence(evidence)
        
        if self.gemini_model:
            answer = self._generate_gemini(query, evidence_text)
        elif self.local_pipeline:
            answer = self._generate_local(query, evidence_text)
        else:
            answer = self._generate_fallback(query, evidence_text)

        # Translate if requested language is not English
        if language and language != 'en':
            try:
                answer = self._translate_text(answer, language)
            except Exception:
                pass
        return answer
    
    def generate_text(self, prompt: str, language: str | None = None) -> str:
        """Generate text from a prompt without requiring evidence"""
        if self.gemini_model:
            try:
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "1200")),
                        temperature=0.3,
                    )
                )
                text = response.text.strip()
                if language and language != 'en':
                    try:
                        text = self._translate_text(text, language)
                    except Exception:
                        pass
                return text
            except Exception as e:
                print(f"Gemini text generation error: {e}")
                return "Unable to generate response at this time."
        elif self.local_pipeline:
            try:
                response = self.local_pipeline(
                    prompt,
                    max_length=int(os.getenv("LOCAL_MAX_LENGTH", "800")),
                    do_sample=True,
                    temperature=0.7,
                )
                generated_text = response[0]['generated_text']
                answer = generated_text[len(prompt):].strip()
                return answer if answer else "Unable to generate response."
            except Exception as e:
                print(f"Local model text generation error: {e}")
                return "Unable to generate response."
        else:
            text = "No LLM available for text generation."
            if language and language != 'en':
                try:
                    text = self._translate_text(text, language)
                except Exception:
                    pass
            return text

    def generate_agricultural_analysis(self, custom_prompt: str) -> str:
        """Generate agricultural analysis using a custom detailed prompt"""
        if self.gemini_model:
            try:
                response = self.gemini_model.generate_content(
                    custom_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "1200")),  # Longer response for detailed analysis
                        temperature=0.3,
                    )
                )
                return response.text.strip()
            except Exception as e:
                print(f"Gemini agricultural analysis error: {e}")
                return "Unable to generate detailed agricultural analysis at this time. Please consult local weather services and agricultural experts."
        elif self.local_pipeline:
            try:
                response = self.local_pipeline(
                    custom_prompt,
                    max_length=int(os.getenv("LOCAL_MAX_LENGTH", "800")),
                    do_sample=True,
                    temperature=0.7,
                )
                generated_text = response[0]['generated_text']
                answer = generated_text[len(custom_prompt):].strip()
                return answer if answer else "Based on the weather data, please consult agricultural experts for specific advice."
            except Exception as e:
                print(f"Local model agricultural analysis error: {e}")
                return "Unable to generate detailed agricultural analysis. Please consult local agricultural experts."
        else:
            return "Detailed agricultural analysis requires an AI model. Please consult local weather services and agricultural experts."
    
    def _format_evidence(self, evidence: List[Dict[str, Any]]) -> str:
        """Format evidence into a readable string"""
        formatted = []
        for i, e in enumerate(evidence[:3], 1):  # Top 3 pieces of evidence
            excerpt = e.get("excerpt", "")
            source = e.get("source", "unknown")
            formatted.append(f"{i}. {excerpt} (Source: {source})")
        return "\n".join(formatted)
    
    def _generate_gemini(self, query: str, evidence: str) -> str:
        """Generate answer using Google Gemini"""
        prompt = f"""You are an agricultural advisor. Answer the following question based ONLY on the provided evidence. If the evidence doesn't contain enough information, say so. Keep your answer concise and practical.

Question: {query}

Evidence:
{evidence}

Answer:"""
        
        try:
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "1200")),
                    temperature=0.3,
                )
            )
            return response.text.strip()
        except Exception as e:
            print(f"Gemini error: {e}")
            return self._generate_fallback(query, evidence)
    
    def _generate_local(self, query: str, evidence: str) -> str:
        """Generate answer using local model"""
        prompt = f"Question: {query}\nEvidence: {evidence}\nAnswer:"
        
        try:
            response = self.local_pipeline(
                prompt,
                max_length=int(os.getenv("LOCAL_MAX_LENGTH", "800")),
                do_sample=True,
                temperature=0.7,
            )
            # Extract just the generated part
            generated_text = response[0]['generated_text']
            # Remove the original prompt
            answer = generated_text[len(prompt):].strip()
            return answer if answer else "Based on the evidence, I cannot provide a complete answer."
        except Exception as e:
            print(f"Local model error: {e}")
            return self._generate_fallback(query, evidence)
    
    def _generate_fallback(self, query: str, evidence: str) -> str:
        """Simple fallback when no LLM is available"""
        return f"Based on the available evidence:\n{evidence}\n\nThis is a summary of relevant information. For more detailed advice, please consult local agricultural experts."

    def _translate_text(self, text: str, language: str) -> str:
        """Translate English text to target language using the available LLM (best-effort)."""
        if not text.strip():
            return text
        # If Gemini available, request translation; otherwise simple passthrough
        if self.gemini_model:
            try:
                prompt = (
                    f"Translate the following response from English to {language} (Indian locale if applicable).\n"
                    f"Preserve meaning and formatting, keep units and numbers.\n\n{text}"
                )
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "1200")),
                        temperature=0.2,
                    ),
                )
                return response.text.strip()
            except Exception as e:
                print(f"Translation error: {e}")
                return text
        return text
