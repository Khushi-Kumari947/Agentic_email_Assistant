from langchain.agents import create_react_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from src.config import GOOGLE_API_KEY, GEMINI_MODEL, AGENT_TEMPERATURE, MAX_ITERATIONS
from src.agent.tools import tools
from src.models import EmailResponse, EmailCategory
import json
import re
from typing import Optional


class EmailAssistantAgent:
    def __init__(self):
        # Initialize Gemini
        self.llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=AGENT_TEMPERATURE,
            convert_system_message_to_human=True,
            max_output_tokens=2048
        )

        # Create the prompt template with clearer instructions
        self.prompt = PromptTemplate.from_template(
            """You are an Intelligent Office Email Assistant. You have access to the following tools:

{tools}

IMPORTANT GUIDELINES:
1. Use PolicySearch to find information from company documents
2. You only need 1-2 tool calls maximum to answer most questions
3. Once you have the information, immediately provide the final answer
4. Do not repeat tool calls unnecessarily
5. If information is not found, politely explain that and suggest alternatives

Use this format:

Question: the input question you must answer
Thought: what information do I need and which tool should I use?
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action

Thought: I now have the information needed
Final Answer: A complete, professional email reply that:
- Starts with "Subject: Re: [topic]"
- Uses the sender's name in the greeting (e.g., "Dear John" not "Dear john.doe@company.com")
- Addresses all parts of the question
- Uses information from policy documents when available
- Is friendly and professional
- Ends with an appropriate signature based on the recipient department
- Ends with an offer to help further

Begin!

Question: {input}
Thought: {agent_scratchpad}"""
        )

        # Create agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=tools,
            prompt=self.prompt
        )

        # Create executor with better early stopping
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=MAX_ITERATIONS,
            early_stopping_method="generate",
            return_intermediate_steps=True
        )

    def extract_sender_info(self, email_content: str) -> tuple:
        """Extract sender name and email from email content"""
        # Look for "From: name <email>" or "From: email" patterns
        from_match = re.search(r'From:\s*(?:(.*?)\s*<)?([^>\n]+)>?', email_content, re.IGNORECASE)
        
        sender_name = "there"
        sender_email = None
        
        if from_match:
            # If we have a display name (e.g., "John Doe <john@company.com>")
            if from_match.group(1):
                sender_name = from_match.group(1).strip()
                sender_email = from_match.group(2).strip()
            else:
                # If only email, extract name from email (john.doe@company.com -> John Doe)
                sender_email = from_match.group(2).strip()
                name_part = sender_email.split('@')[0]
                
                # Convert common patterns to names
                if '.' in name_part:
                    parts = name_part.split('.')
                    sender_name = ' '.join([p.capitalize() for p in parts])
                elif '_' in name_part:
                    parts = name_part.split('_')
                    sender_name = ' '.join([p.capitalize() for p in parts])
                elif '-' in name_part:
                    parts = name_part.split('-')
                    sender_name = ' '.join([p.capitalize() for p in parts])
                else:
                    sender_name = name_part.capitalize()
        
        return sender_name, sender_email

    def extract_recipient_info(self, email_content: str) -> tuple:
        """Extract recipient name and email from email content"""
        # Look for "To: name <email>" or "To: email" patterns
        to_match = re.search(r'To:\s*(?:(.*?)\s*<)?([^>\n]+)>?', email_content, re.IGNORECASE)
        
        recipient_name = None
        recipient_email = None
        
        if to_match:
            if to_match.group(1):
                recipient_name = to_match.group(1).strip()
                recipient_email = to_match.group(2).strip()
            else:
                recipient_email = to_match.group(2).strip()
        
        return recipient_name, recipient_email

    def extract_subject(self, email_content: str) -> str:
        """Extract subject from email content"""
        subject_match = re.search(r'Subject:\s*(.+)', email_content, re.IGNORECASE)
        if subject_match:
            return subject_match.group(1).strip()
        return "Your Inquiry"

    def determine_department_from_content(self, email_content: str, retrieved_docs: list, recipient_info: tuple) -> str:
        """Use LLM to determine the appropriate department based on content, retrieved docs, and recipient"""
        
        recipient_name, recipient_email = recipient_info
        
        # Prepare context from retrieved documents
        docs_context = ""
        if retrieved_docs:
            docs_context = "Relevant policy documents:\n"
            for i, doc in enumerate(retrieved_docs[:2]):  # Use first 2 docs
                if isinstance(doc, dict) and "result" in doc:
                    docs_context += f"Document {i+1}: {doc['result'][:200]}...\n"
        
        # Add recipient context
        recipient_context = ""
        if recipient_email:
            recipient_context = f"This email was sent to: {recipient_email}"
            if recipient_name:
                recipient_context += f" ({recipient_name})"
        
        prompt = f"""Based on the following information, determine which department should send the response.

Email content:
{email_content}

{recipient_context}

{docs_context}

Return ONLY the name of the department that should sign the email (e.g., "HR Department", "Finance Team", "IT Support", "Benefits Team", "Office Assistant", etc.).
The department name should be professional and appropriate for the context.

Department:"""
        
        try:
            response = self.llm.invoke(prompt).content.strip()
            # Clean up the response
            response = re.sub(r'^["\']|["\']$', '', response)  # Remove quotes
            return response
        except:
            return "Office Assistant"

    def process_email(self, email_content: str) -> EmailResponse:
        """Process an email and generate response"""
        try:
            # Extract sender and recipient information
            sender_name, sender_email = self.extract_sender_info(email_content)
            recipient_name, recipient_email = self.extract_recipient_info(email_content)
            subject = self.extract_subject(email_content)
            
            # Enhance the input with extracted information for better personalization
            enhanced_input = f"""{email_content}

ADDITIONAL CONTEXT FOR YOUR RESPONSE:
- Sender's name: {sender_name}
- Sender's email: {sender_email}
- This email was sent to: {recipient_email if recipient_email else 'the appropriate department'}
- Subject: {subject}

Please address the sender as "{sender_name}" in your greeting.
"""
            
            # Run the agent with enhanced input
            result = self.agent_executor.invoke({
                "input": enhanced_input
            })
            
            # Extract retrieved docs from intermediate steps
            retrieved_docs = []
            if "intermediate_steps" in result:
                for step in result["intermediate_steps"]:
                    action, observation = step
                    if action.tool == "PolicySearch" and observation:
                        retrieved_docs.append({
                            "tool": "PolicySearch",
                            "result": observation[:300]
                        })
            
            # Determine the appropriate department for signature
            department = self.determine_department_from_content(
                email_content, 
                retrieved_docs, 
                (recipient_name, recipient_email)
            )
            
            # Check if we have a valid output
            if "output" in result and result["output"]:
                response = self._parse_response(result["output"])
                # Ensure the signature is appropriate
                response.draft_reply = self._ensure_proper_signature(response.draft_reply, department)
                response.retrieved_docs = retrieved_docs
                return response
            else:
                # If no output, generate a response from the intermediate steps
                return self._generate_response_from_steps(retrieved_docs, enhanced_input, department, sender_name)

        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "quota" in error_str or "resourceexhausted" in error_str:
                print(f"⚠️ Quota exceeded: {e}")
                return EmailResponse(
                    draft_reply="Subject: Re: Your Email\n\nI'm currently at my API limit for today. Please try again tomorrow, or contact support if this is urgent.\n\nBest regards,\nOffice Assistant",
                    category=EmailCategory.GENERAL_INQUIRY,
                    retrieved_docs=[],
                    confidence_score=0.3,
                    requires_human_review=True,
                    clarification_needed=False,
                    clarification_question=None
                )
            else:
                print(f"Agent error: {e}")
                return self._get_fallback_response()

    def _generate_response_from_steps(self, retrieved_docs, original_query, department, sender_name):
        """Generate a response from intermediate steps if final output is missing"""
        try:
            # Extract information from steps
            retrieved_info = []
            for doc in retrieved_docs:
                if doc.get("result"):
                    retrieved_info.append(doc["result"])
            
            if retrieved_info:
                # Use the LLM to generate a response based on retrieved info
                prompt = f"""Based on this employee question: "{original_query}"

And these policy documents:
{chr(10).join(retrieved_info)}

Generate a professional email reply that:
1. Starts with "Subject: Re:"
2. Addresses the sender as "{sender_name}" in the greeting
3. Answers the question using the policy information
4. Is friendly and helpful
5. Ends with this signature: "Best regards,\n{department}"
6. Ends with an offer to help further

Email reply:"""
                
                response = self.llm.invoke(prompt).content
                parsed = self._parse_response(response)
                parsed.retrieved_docs = retrieved_docs
                return parsed
            else:
                return self._get_fallback_response()
        except:
            return self._get_fallback_response()

    def _ensure_proper_signature(self, draft_reply: str, department: str) -> str:
        """Ensure the email has a proper signature with the determined department"""
        
        # Common signature patterns to look for
        signature_patterns = [
            r'Best regards,?\s*\n\s*[\w\s/\[\]]+$',  # Best regards, [name]
            r'Thanks,?\s*\n\s*[\w\s/\[\]]+$',       # Thanks, [name]
            r'Sincerely,?\s*\n\s*[\w\s/\[\]]+$',    # Sincerely, [name]
            r'Regards,?\s*\n\s*[\w\s/\[\]]+$',      # Regards, [name]
            r'\[\w+\s*\w+\]',                       # [Name/Title] pattern
        ]
        
        # Check if the email already has a signature
        has_signature = False
        for pattern in signature_patterns:
            if re.search(pattern, draft_reply, re.MULTILINE):
                has_signature = True
                # Replace the signature with our department signature
                draft_reply = re.sub(pattern, f"Best regards,\n{department}", draft_reply, flags=re.MULTILINE)
                break
        
        # If no signature found, add one
        if not has_signature:
            draft_reply = draft_reply.rstrip()
            if not draft_reply.endswith('.'):
                draft_reply += '.'
            draft_reply += f"\n\nBest regards,\n{department}"
        
        return draft_reply

    def _parse_response(self, response_text: str) -> EmailResponse:
        """Parse the agent's response into EmailResponse"""
        try:
            # Extract the actual email content
            if "Final Answer:" in response_text:
                draft = response_text.split("Final Answer:")[-1].strip()
            else:
                draft = response_text

            # Remove any "Thought:" or "Action:" lines that might remain
            lines = draft.split('\n')
            cleaned_lines = []
            for line in lines:
                if not any(line.strip().startswith(x) for x in ['Thought:', 'Action:', 'Observation:', 'Question:']):
                    cleaned_lines.append(line)
            
            draft = '\n'.join(cleaned_lines)

            # Clean duplicate subjects
            lines = draft.split('\n')
            cleaned_lines = []
            subject_found = False

            for line in lines:
                if line.startswith('Subject:') and not subject_found:
                    cleaned_lines.append(line)
                    subject_found = True
                elif not line.startswith('Subject:'):
                    cleaned_lines.append(line)

            draft = '\n'.join(cleaned_lines)

            # Ensure exactly one subject line
            if not draft.startswith('Subject:'):
                draft = f"Subject: Re: Your Email\n\n{draft}"

            # Simple category detection
            category = (
                EmailCategory.POLICY_QUERY
                if "policy" in draft.lower() or "sick" in draft.lower() or "leave" in draft.lower()
                else EmailCategory.GENERAL_INQUIRY
            )

            return EmailResponse(
                draft_reply=draft,
                category=category,
                retrieved_docs=[],
                confidence_score=0.85,
                requires_human_review=False,
                clarification_needed=False,
                clarification_question=None
            )

        except Exception as e:
            print(f"Error parsing response: {e}")
            return self._get_fallback_response()

    def _get_fallback_response(self) -> EmailResponse:
        """Return a fallback response when everything fails"""
        return EmailResponse(
            draft_reply="Subject: Re: Your Email\n\nThank you for your email. I have received your message and will respond shortly. If this is urgent, please contact your manager directly.\n\nBest regards,\nOffice Assistant",
            category=EmailCategory.GENERAL_INQUIRY,
            retrieved_docs=[],
            confidence_score=0.5,
            requires_human_review=False,
            clarification_needed=False,
            clarification_question=None
        )


# Global instance
_email_agent_instance: Optional[EmailAssistantAgent] = None


def get_email_agent() -> EmailAssistantAgent:
    """Get or create the email agent singleton"""
    global _email_agent_instance
    if _email_agent_instance is None:
        _email_agent_instance = EmailAssistantAgent()
    return _email_agent_instance


def process_email(email_content: str) -> EmailResponse:
    """Process an email and generate a response"""
    agent = get_email_agent()
    return agent.process_email(email_content)


__all__ = ['process_email', 'EmailAssistantAgent', 'get_email_agent']