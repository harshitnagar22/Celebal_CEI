import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from src.agent.graph import chat

class Evaluator:
    def __init__(self):
        # using flash because it's fast and cheap for grading
        self.judge_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0
        )
        
        self.test_cases = [
            {
                "query": "What is the definition of a Large Language Model?",
                "expected_focus": "RAG / Static Knowledge"
            },
            {
                "query": "Who is the current CEO of Google?",
                "expected_focus": "Dynamic Tools / Real-time"
            },
            {
                "query": "What are the relationships between Machine Learning and Artificial Intelligence?",
                "expected_focus": "Knowledge Graph"
            }
        ]

    def _evaluate_response(self, query: str, response: str) -> dict:
        # prompt the llm to act as a judge for the bot
        prompt = f"""
        You are an impartial expert evaluator judging a chatbot's response.
        
        User Query: {query}
        Chatbot Response: {response}
        
        Evaluate the chatbot's response on the following three metrics from 1 to 5:
        1. Context Relevance: How relevant is the response to the user's query?
        2. Faithfulness: Does the response stick to facts and avoid hallucinating?
        3. Answer Correctness: Is the answer factually correct and helpful?
        
        Respond ONLY with a valid JSON object matching this schema exactly. No markdown, no backticks, just the JSON string:
        {{
            "context_relevance": 5,
            "faithfulness": 5,
            "answer_correctness": 5,
            "reasoning": "brief 1-sentence explanation"
        }}
        """
        
        try:
            eval_result = self.judge_llm.invoke([HumanMessage(content=prompt)])
            text = eval_result.content.strip()
            
            # strip markdown if gemini randomly decides to wrap it in ```json
            if text.startswith("```json"):
                text = text[7:-3]
            elif text.startswith("```"):
                text = text[3:-3]
                
            return json.loads(text.strip())
        except Exception as e:
            # fallback if it crashes
            return {
                "context_relevance": 0,
                "faithfulness": 0,
                "answer_correctness": 0,
                "reasoning": f"Evaluation failed: {str(e)}"
            }

    def evaluate(self):
        print("\n" + "="*60)
        print("Starting Automated LLM-Based Evaluation Framework...")
        print("Evaluating: Context Relevance, Faithfulness, Correctness")
        print("="*60 + "\n")
        
        results = []
        overall_scores = {"context_relevance": 0, "faithfulness": 0, "answer_correctness": 0}
        successful_evals = 0
        
        for idx, test in enumerate(self.test_cases):
            query = test["query"]
            print(f"[{idx+1}/{len(self.test_cases)}] Testing: '{query}'")
            print(f"   => Focus: {test['expected_focus']}")
            
            try:
                # get bot response
                bot_response = chat(query, thread_id="automated_eval_user")
                
                # grade it
                scores = self._evaluate_response(query, bot_response)
                
                results.append({
                    "query": query,
                    "response": bot_response,
                    "scores": scores
                })
                
                if scores["context_relevance"] > 0:
                    overall_scores["context_relevance"] += scores["context_relevance"]
                    overall_scores["faithfulness"] += scores["faithfulness"]
                    overall_scores["answer_correctness"] += scores["answer_correctness"]
                    successful_evals += 1
                
                print(f"   => Relevance: {scores['context_relevance']}/5 | Faithfulness: {scores['faithfulness']}/5 | Correctness: {scores['answer_correctness']}/5")
                print(f"   => Reasoning: {scores['reasoning']}")
                print("-" * 60)
                
            except Exception as e:
                print(f"   => [ERROR] Failed to process query: {str(e)}")
                print("-" * 60)
            
            # rate limit hack for free tier gemini so it doesn't 429
            if idx < len(self.test_cases) - 1:
                print("Waiting 15 seconds to respect free-tier API rate limits...")
                import time
                time.sleep(15)

        # print the final stats
        if successful_evals > 0:
            print("\n=== FINAL EVALUATION REPORT ===")
            print(f"Average Context Relevance: {overall_scores['context_relevance'] / successful_evals:.1f} / 5.0")
            print(f"Average Faithfulness:      {overall_scores['faithfulness'] / successful_evals:.1f} / 5.0")
            print(f"Average Correctness:       {overall_scores['answer_correctness'] / successful_evals:.1f} / 5.0")
            print("===============================\n")
            
        return results

if __name__ == "__main__":
    evaluator = Evaluator()
    evaluator.evaluate()
