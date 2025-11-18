'''
AI Handler Module - OpenAI and Gemini Integration

Author:     AI Integration Team
Version:    1.0.0

This module provides AI integration for:
- Testing API connections
- Answering application questions
- Resume customization
- Job matching analysis
'''

import sys
from typing import Optional, Dict, Any
from config.secrets import (
    use_AI, ai_provider, llm_api_url, llm_api_key, 
    llm_model, stream_output
)


class AIHandler:
    """Handler for AI provider integrations"""
    
    def __init__(self):
        """Initialize AI handler with configured provider"""
        self.enabled = use_AI
        self.provider = ai_provider
        self.api_url = llm_api_url
        self.api_key = llm_api_key
        self.model = llm_model
        self.stream = stream_output
        self.client = None
        
        if self.enabled:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the AI client based on provider"""
        try:
            if self.provider == "openai":
                self._init_openai()
            elif self.provider == "gemini":
                self._init_gemini()
            elif self.provider == "deepseek":
                self._init_deepseek()
            else:
                print(f"Warning: Unknown AI provider '{self.provider}', defaulting to OpenAI-compatible")
                self._init_openai()
        except Exception as e:
            print(f"Error initializing AI client: {e}")
            self.enabled = False
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        try:
            from openai import OpenAI
            
            # Handle local LLM APIs (like Ollama)
            if self.api_key in ["not-needed", "", None]:
                self.client = OpenAI(
                    base_url=self.api_url,
                    api_key="not-needed"  # Local APIs don't need key
                )
            else:
                # Official OpenAI API
                self.client = OpenAI(api_key=self.api_key)
            
            print(f"OpenAI client initialized (Model: {self.model or 'default'})")
        except ImportError:
            print("Error: openai library not installed. Run: pip install openai")
            self.enabled = False
        except Exception as e:
            print(f"Error initializing OpenAI: {e}")
            self.enabled = False
    
    def _init_gemini(self):
        """Initialize Google Gemini client"""
        try:
            import google.generativeai as genai
            
            if not self.api_key or self.api_key == "not-needed":
                print("Error: Gemini requires a valid API key")
                self.enabled = False
                return
            
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model or 'gemini-pro')
            print(f"Gemini client initialized (Model: {self.model or 'gemini-pro'})")
        except ImportError:
            print("Error: google-generativeai library not installed. Run: pip install google-generativeai")
            self.enabled = False
        except Exception as e:
            print(f"Error initializing Gemini: {e}")
            self.enabled = False
    
    def _init_deepseek(self):
        """Initialize DeepSeek client (OpenAI-compatible)"""
        try:
            from openai import OpenAI
            
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_url or "https://api.deepseek.com"
            )
            print(f"DeepSeek client initialized (Model: {self.model or 'deepseek-chat'})")
        except ImportError:
            print("Error: openai library not installed. Run: pip install openai")
            self.enabled = False
        except Exception as e:
            print(f"Error initializing DeepSeek: {e}")
            self.enabled = False
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the AI connection with a simple query
        
        Returns:
            dict: {"success": bool, "message": str, "details": dict}
        """
        if not self.enabled:
            return {
                "success": False,
                "message": "AI is disabled in config",
                "details": {"use_AI": use_AI}
            }
        
        if not self.client:
            return {
                "success": False,
                "message": "AI client not initialized",
                "details": {"provider": self.provider}
            }
        
        try:
            # Test with a simple query
            test_query = "Respond with just 'OK' if you can read this message."
            
            if self.provider == "gemini":
                response = self._test_gemini(test_query)
            else:
                response = self._test_openai_compatible(test_query)
            
            return {
                "success": True,
                "message": "AI connection successful!",
                "details": {
                    "provider": self.provider,
                    "model": self.model or "default",
                    "api_url": self.api_url,
                    "response": response[:100]  # First 100 chars
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection test failed: {str(e)}",
                "details": {
                    "provider": self.provider,
                    "error_type": type(e).__name__
                }
            }
    
    def _test_openai_compatible(self, query: str) -> str:
        """Test OpenAI-compatible API"""
        try:
            completion = self.client.chat.completions.create(
                model=self.model or "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": query}
                ],
                max_tokens=50,
                temperature=0.7
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def _test_gemini(self, query: str) -> str:
        """Test Gemini API"""
        try:
            response = self.client.generate_content(query)
            return response.text.strip()
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def answer_question(self, question: str, job_context: Optional[str] = None) -> str:
        """
        Use AI to answer an application question
        
        Args:
            question: The application question
            job_context: Optional job description context
            
        Returns:
            str: AI-generated answer
        """
        if not self.enabled or not self.client:
            return ""
        
        try:
            prompt = f"Answer this job application question professionally and concisely:\n\nQuestion: {question}"
            
            if job_context:
                prompt += f"\n\nJob Context: {job_context}"
            
            prompt += "\n\nProvide only the answer, no explanation."
            
            if self.provider == "gemini":
                response = self.client.generate_content(prompt)
                return response.text.strip()
            else:
                completion = self.client.chat.completions.create(
                    model=self.model or "gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert at answering job application questions."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating answer: {e}")
            return ""
    
    def customize_resume(self, resume_text: str, job_description: str) -> str:
        """
        Use AI to customize resume for a specific job
        
        Args:
            resume_text: Current resume content
            job_description: Target job description
            
        Returns:
            str: Customized resume suggestions
        """
        if not self.enabled or not self.client:
            return resume_text
        
        try:
            prompt = f"""Given this resume and job description, provide 3-5 specific bullet points 
that could be added or emphasized to better match the job requirements:

Resume:
{resume_text[:1000]}

Job Description:
{job_description[:1000]}

Provide only the bullet points, no explanation."""
            
            if self.provider == "gemini":
                response = self.client.generate_content(prompt)
                return response.text.strip()
            else:
                completion = self.client.chat.completions.create(
                    model=self.model or "gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a professional resume writer."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error customizing resume: {e}")
            return resume_text
    
    def match_job(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """
        Use AI to analyze job match score
        
        Args:
            resume_text: Current resume content
            job_description: Target job description
            
        Returns:
            dict: {"score": int, "strengths": list, "gaps": list}
        """
        if not self.enabled or not self.client:
            return {"score": 50, "strengths": [], "gaps": []}
        
        try:
            prompt = f"""Analyze the match between this resume and job description. 
Provide:
1. Match score (0-100)
2. Top 3 strengths
3. Top 3 skill gaps

Resume:
{resume_text[:1000]}

Job Description:
{job_description[:1000]}

Format: Score: X\nStrengths: bullet, bullet, bullet\nGaps: bullet, bullet, bullet"""
            
            if self.provider == "gemini":
                response = self.client.generate_content(prompt)
                text = response.text.strip()
            else:
                completion = self.client.chat.completions.create(
                    model=self.model or "gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a job matching expert."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                text = completion.choices[0].message.content.strip()
            
            # Parse response
            score = 50
            strengths = []
            gaps = []
            
            for line in text.split('\n'):
                if 'score' in line.lower():
                    try:
                        score = int(''.join(filter(str.isdigit, line)))
                    except:
                        pass
                elif 'strength' in line.lower():
                    strengths = [s.strip(' -•') for s in line.split(':')[1].split(',') if s.strip()]
                elif 'gap' in line.lower():
                    gaps = [g.strip(' -•') for g in line.split(':')[1].split(',') if g.strip()]
            
            return {
                "score": min(100, max(0, score)),
                "strengths": strengths[:3],
                "gaps": gaps[:3]
            }
        except Exception as e:
            print(f"Error matching job: {e}")
            return {"score": 50, "strengths": [], "gaps": []}


# Global AI handler instance
ai_handler = AIHandler()


# Convenience functions
def test_ai_connection() -> Dict[str, Any]:
    """Test AI connection - convenience function"""
    return ai_handler.test_connection()


def answer_with_ai(question: str, context: Optional[str] = None) -> str:
    """Answer question with AI - convenience function"""
    return ai_handler.answer_question(question, context)


def customize_resume_with_ai(resume: str, job_desc: str) -> str:
    """Customize resume with AI - convenience function"""
    return ai_handler.customize_resume(resume, job_desc)


def match_job_with_ai(resume: str, job_desc: str) -> Dict[str, Any]:
    """Match job with AI - convenience function"""
    return ai_handler.match_job(resume, job_desc)
