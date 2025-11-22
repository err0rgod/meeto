"""
LLM service for extracting action items from transcripts
Supports Groq API, OpenAI API (optional), and local models via Ollama
"""
import json
import re
from typing import List, Dict, Any, Optional
from app.config import settings
import os

# Try to import Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None

# Optional OpenAI support for backward compatibility
try:
    from openai import OpenAI as OpenAIClient
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class LLMService:
    """Service for extracting action items using LLM (Groq by default)"""
    
    def __init__(self):
        self.client = None
        self.model = settings.LLM_MODEL
        self.provider = None
        
        if settings.GROQ_API_KEY and GROQ_AVAILABLE:
            # Use Groq API (recommended)
            self.client = Groq(api_key=settings.GROQ_API_KEY)
            self.provider = "groq"
            # Default Groq models if not specified
            if not settings.LLM_MODEL or settings.LLM_MODEL.startswith("gpt-"):
                self.model = "llama-3.1-70b-versatile"
        elif settings.OPENAI_API_KEY and OPENAI_AVAILABLE:
            # Fallback to OpenAI API
            self.client = OpenAIClient(api_key=settings.OPENAI_API_KEY)
            self.provider = "openai"
            self.model = settings.LLM_MODEL or "gpt-4o-mini"
        elif settings.ENABLE_LOCAL_MODE:
            # Try to use local Ollama if available
            if OPENAI_AVAILABLE:
                self.client = OpenAIClient(
                    base_url="http://localhost:11434/v1",
                    api_key="ollama"  # Not used but required
                )
                self.provider = "ollama"
                self.model = "llama3.2"  # Default local model
            else:
                raise ValueError("OpenAI library required for local Ollama mode. Install: pip install openai")
        else:
            error_msg = "LLM service requires one of:"
            if not GROQ_AVAILABLE:
                error_msg += "\n- Install Groq: pip install groq (and set GROQ_API_KEY)"
            else:
                error_msg += "\n- GROQ_API_KEY"
            error_msg += "\n- OPENAI_API_KEY"
            error_msg += "\n- ENABLE_LOCAL_MODE (with Ollama)"
            raise ValueError(error_msg)
    
    def extract_action_items(self, transcript: str) -> Dict[str, Any]:
        """
        Extract action items from meeting transcript
        
        Args:
            transcript: Meeting transcript text
        
        Returns:
            Dictionary with extracted tasks in the required format
        """
        prompt = self._build_extraction_prompt(transcript)
        
        try:
            if self.client:
                # Prepare request parameters with a strict system prompt
                request_params = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are an expert at analyzing meeting transcripts and extracting clear, actionable tasks.\n\n"
                                "Requirements:\n"
                                "- Extract only explicit action items or tasks mentioned in the transcript. Do NOT hallucinate.\n"
                                "- Each task must be a single concise one-line description (preferably under 140 characters).\n"
                                "- Identify responsible person if mentioned (owner). If not clearly stated, set owner to null.\n"
                                "- Identify a deadline if mentioned and normalize to YYYY-MM-DD; otherwise null.\n"
                                "- Assign priority: one of \"low\"|\"medium\"|\"high\"|\"critical\". Default to \"medium\" when unclear.\n"
                                "- Provide a confidence score between 0.0 and 1.0.\n\n"
                                "Return ONLY valid JSON in this exact format (no extra text):\n"
                                "{\n  \"tasks\": [\n    {\n      \"description\": \"...\",\n      \"owner\": \"...\" or null,\n      \"deadline\": \"YYYY-MM-DD\" or null,\n      \"priority\": \"low|medium|high|critical\",\n      \"confidence\": 0.0-1.0\n    }\n  ]\n}\n\n"
                                "If there are no action items, return {\"tasks\": []}. Be conservative and prefer omitting unclear items."
                            )
                        },
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                }

                # Request structured response where supported
                if self.provider in ("groq", "openai"):
                    request_params["response_format"] = {"type": "json_object"}

                response = self.client.chat.completions.create(**request_params)
                content = response.choices[0].message.content

                # Try strict JSON parse first
                tasks_out = []
                try:
                    parsed = json.loads(content)
                except Exception:
                    # Try to extract JSON substring if model added surrounding text
                    m = re.search(r"\{\s*\"tasks\"[\s\S]*\}\s*$", content)
                    if not m:
                        m = re.search(r"\{\s*\"tasks\"[\s\S]*\}", content)
                    if m:
                        try:
                            parsed = json.loads(m.group(0))
                        except Exception:
                            parsed = {"tasks": []}
                    else:
                        parsed = {"tasks": []}

                for t in parsed.get("tasks", []):
                    # Normalize and enforce one-line concise descriptions
                    desc = t.get("description") if isinstance(t.get("description"), str) else ""
                    desc = re.sub(r"\s+", ' ', desc).strip()
                    # If long, take the first sentence or truncate
                    if len(desc) > 140:
                        first_sent = re.split(r"[\.\!\?]\s", desc)[0]
                        if len(first_sent) >= 10:
                            desc = first_sent.strip()
                        desc = (desc[:137].rstrip() + '...') if len(desc) > 140 else desc

                    owner = t.get("owner") if t.get("owner") else None

                    # Normalize deadline
                    deadline = None
                    if t.get("deadline"):
                        dl = str(t.get("deadline"))
                        from datetime import datetime
                        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y"):
                            try:
                                dt = datetime.strptime(dl, fmt)
                                deadline = dt.strftime("%Y-%m-%d")
                                break
                            except Exception:
                                continue

                    priority = (t.get("priority") or "medium").lower()
                    if priority not in ("low", "medium", "high", "critical"):
                        priority = "medium"

                    try:
                        confidence = float(t.get("confidence", 0.5))
                    except Exception:
                        confidence = 0.5

                    tasks_out.append({
                        "description": desc,
                        "owner": owner,
                        "deadline": deadline,
                        "priority": priority,
                        "confidence": round(confidence, 2)
                    })

                # Confidence filtering and deterministic normalization
                filtered = []
                threshold = getattr(settings, "TASK_CONFIDENCE_THRESHOLD", 0.4)
                normalize_enabled = getattr(settings, "NORMALIZE_TASKS", True)

                def normalize_description(d, owner_val=None):
                    d = d or ""
                    d = d.strip()
                    # Remove polite prefixes
                    d = re.sub(r'^(please|pls|kindly|could you|can you|would you|let\'s|let us|we should|we need to)\b[:,]?\s*', '', d, flags=re.I)
                    # If starts with "we" remove leading "we (should|will|need to)" to make imperative
                    d = re.sub(r'^(we\s+(should|will|need to)\s+)', '', d, flags=re.I)
                    # If starts with "NAME will ..." or "NAME to ..." try to extract owner and make rest imperative
                    m = re.match(r'^([A-Z][a-zA-Z]+)\s+(will|shall|should|to)\s+(.*)$', d)
                    if m:
                        possible_owner = m.group(1)
                        rest = m.group(3).strip()
                        if not owner_val:
                            owner_val = possible_owner
                        d = rest
                    # Ensure starts with a verb: if starts with gerund or noun phrases, try to prefix with verb 'Do' (fallback)
                    if d and not re.match(r'^[A-Za-z]+\s', d):
                        d = d
                    # Capitalize first letter
                    if d:
                        d = d[0].upper() + d[1:]
                    # Collapse whitespace and keep one-line
                    d = re.sub(r"\s+", ' ', d).strip()
                    if len(d) > 140:
                        d = d[:137].rstrip() + '...'
                    return d, owner_val

                for t in tasks_out:
                    conf = t.get("confidence", 0.5) or 0.5
                    if conf < threshold:
                        # Skip low confidence items
                        continue

                    desc = t.get("description", "")
                    owner = t.get("owner")
                    if normalize_enabled:
                        desc, owner = normalize_description(desc, owner)

                    filtered.append({
                        "description": desc,
                        "owner": owner,
                        "deadline": t.get("deadline"),
                        "priority": t.get("priority", "medium"),
                        "confidence": t.get("confidence", 0.5)
                    })

                return {"tasks": filtered}

                return {"tasks": tasks_out}
            else:
                # Fallback: Simple regex-based extraction
                return self._extract_simple(transcript)

        except Exception as e:
            print(f"Error extracting action items with {self.provider}: {e}")
            # Fallback to simple extraction
            return self._extract_simple(transcript)

    def summarize_transcript(self, transcript: str) -> str:
        """
        Create a concise meeting summary/minutes from a transcript using the configured LLM.

        Returns a plain text summary.
        """
        # Keep the prompt focused and ask for short bullet points with clear one-line action summaries
        sample = transcript if len(transcript) < 12000 else transcript[:12000]
        prompt = (
            "Produce concise meeting minutes from the transcript below. Respond with short bullet points under these headings (if present): Attendees, Decisions, Action Items (one-line per item), Key Takeaways. "
            "Action items must be one-line, start with a verb, and be under 140 characters. Do not add any tasks not present in the transcript. "
            f"Transcript:\n{sample}"
        )

        try:
            if self.client:
                request_params = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are an assistant that summarizes meeting transcripts into concise minutes with bullets."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2,
                }

                if self.provider == "groq":
                    request_params["response_format"] = {"type": "text"}
                elif self.provider == "openai":
                    request_params["response_format"] = {"type": "text"}

                response = self.client.chat.completions.create(**request_params)
                content = response.choices[0].message.content
                return content.strip()
            else:
                # Fallback simple summary: first 400 chars
                return transcript.strip()[:400] + ("..." if len(transcript) > 400 else "")

        except Exception as e:
            print(f"Error summarizing transcript with {self.provider}: {e}")
            return transcript.strip()[:400] + ("..." if len(transcript) > 400 else "")
    
    def _build_extraction_prompt(self, transcript: str) -> str:
        """Build the prompt for action item extraction"""
        # Truncate very long transcripts to keep prompts within model context windows
        sample = transcript if len(transcript) < 20000 else transcript[:20000]
        return f"Analyze the following meeting transcript and extract all explicit action items. Return only JSON as instructed in the system prompt.\n\nTranscript:\n{sample}"
    
    def _extract_simple(self, transcript: str) -> Dict[str, Any]:
        """Fallback simple extraction using regex patterns"""
        tasks = []
        
        # Look for common patterns
        action_patterns = [
            r"(?:need to|will|should|must|have to)\s+([^.!?]+(?:\.|!|\?))",
            r"action item[:\s]+([^.!?]+(?:\.|!|\?))",
            r"todo[:\s]+([^.!?]+(?:\.|!|\?))",
            r"task[:\s]+([^.!?]+(?:\.|!|\?))",
        ]
        
        for pattern in action_patterns:
            matches = re.finditer(pattern, transcript, re.IGNORECASE)
            for match in matches:
                description = match.group(1).strip()
                # Collapse whitespace and keep only the first sentence-like fragment
                description = re.sub(r"\s+", ' ', description)
                parts = re.split(r"[\.\!\?]\s", description)
                short = parts[0].strip() if parts and len(parts[0].strip()) > 6 else description

                if len(short) < 6:
                    continue

                if len(short) > 140:
                    short = short[:137].rstrip() + '...'

                tasks.append({
                    "description": short,
                    "owner": None,
                    "deadline": None,
                    "priority": "medium",
                    "confidence": 0.5
                })
        
        return {"tasks": tasks[:10]}  # Limit to 10 tasks


# Singleton instance
llm_service = LLMService() if (settings.GROQ_API_KEY or settings.OPENAI_API_KEY or settings.ENABLE_LOCAL_MODE) else None

