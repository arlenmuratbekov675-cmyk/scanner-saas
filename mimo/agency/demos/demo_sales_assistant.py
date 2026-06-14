"""
Demo 1: AI Sales Assistant
Simulates a 24/7 AI chatbot that handles customer inquiries.
"""
import json
from datetime import datetime


class AISalesAssistant:
    def __init__(self, business_name: str, industry: str):
        self.business_name = business_name
        self.industry = industry
        self.conversation = []
        
    def greet(self) -> str:
        msg = f"Hello! I'm the AI assistant for {self.business_name}. How can I help you today?"
        self.conversation.append({"role": "assistant", "message": msg})
        return msg
    
    def respond(self, user_message: str) -> str:
        # Simple keyword-based responses (in production, use LLM)
        msg_lower = user_message.lower()
        
        if any(w in msg_lower for w in ["price", "cost", "how much"]):
            response = f"Great question! Our pricing starts at $99/month. Would you like me to explain what's included?"
        
        elif any(w in msg_lower for w in ["demo", "show", "see"]):
            response = f"I'd love to show you a demo! We can schedule a 15-minute call. What time works best for you?"
        
        elif any(w in msg_lower for w in ["book", "appointment", "schedule"]):
            response = f"Perfect! I can book you right now. What's your preferred date and time?"
        
        elif any(w in msg_lower for w in ["help", "support", "issue"]):
            response = f"I'm here to help! What specific issue are you experiencing?"
        
        elif any(w in msg_lower for w in ["hi", "hello", "hey"]):
            response = f"Hi there! What can I help you with regarding {self.business_name}?"
        
        else:
            response = f"Thank you for your interest in {self.business_name}! Let me connect you with our team. Can you share your email and phone number?"
        
        self.conversation.append({"role": "user", "message": user_message})
        self.conversation.append({"role": "assistant", "message": response})
        return response
    
    def get_transcript(self) -> str:
        lines = []
        for msg in self.conversation:
            role = "Customer" if msg["role"] == "user" else "AI Bot"
            lines.append(f"{role}: {msg['message']}")
        return "\n".join(lines)
    
    def qualify_lead(self) -> dict:
        """Analyze conversation and qualify the lead."""
        user_msgs = [m["message"] for m in self.conversation if m["role"] == "user"]
        full_text = " ".join(user_msgs).lower()
        
        score = 50  # Base score
        
        # Positive signals
        if any(w in full_text for w in ["price", "cost", "demo", "book"]):
            score += 20
        if any(w in full_text for w in ["email", "phone", "contact"]):
            score += 15
        if "@" in full_text:
            score += 10
        if len(user_msgs) >= 3:
            score += 10
        
        return {
            "score": min(score, 100),
            "qualified": score >= 70,
            "signals": {
                "asked_pricing": "price" in full_text,
                "asked_demo": "demo" in full_text,
                "provided_contact": "@" in full_text,
                "engagement_level": len(user_msgs)
            }
        }


def run_demo():
    print("=" * 60)
    print("DEMO: AI Sales Assistant")
    print("=" * 60)
    
    bot = AISalesAssistant("TechCorp Solutions", "SaaS")
    print(f"\n{bot.greet()}\n")
    
    # Simulated conversation
    test_messages = [
        "Hi, I saw your ad about AI automation",
        "What are your prices?",
        "That sounds interesting, can you show me a demo?",
        "Yes, my email is john@example.com"
    ]
    
    for msg in test_messages:
        print(f"Customer: {msg}")
        response = bot.respond(msg)
        print(f"AI Bot: {response}\n")
    
    # Lead qualification
    qualification = bot.qualify_lead()
    print("=" * 60)
    print("LEAD QUALIFICATION RESULT")
    print("=" * 60)
    print(f"Score: {qualification['score']}/100")
    print(f"Qualified: {'YES' if qualification['qualified'] else 'NO'}")
    print(f"Signals: {json.dumps(qualification['signals'], indent=2)}")
    
    print("\n" + "=" * 60)
    print("FULL TRANSCRIPT")
    print("=" * 60)
    print(bot.get_transcript())


if __name__ == "__main__":
    run_demo()
