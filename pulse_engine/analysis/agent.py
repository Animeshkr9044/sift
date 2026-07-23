# pulse_engine/analysis/agent.py

import json
import pandas as pd
import numpy as np
from collections import Counter
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

class ReviewAnalysisAgent:
    def __init__(self, openai_api_key):
        self.client = OpenAI(api_key=openai_api_key)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.seed_topics = [
            "Delivery partner rude",
            "Food stale", 
            "Delivery delay",
            "App crashes",
            "Payment issues",
            "Wrong order",
            "Food quality poor",
            "Customer service bad",
            "App bugs",
            "Pricing high"
        ]
        self.similarity_threshold = 0.75

    def extract_topics_from_reviews(self, reviews_batch):
        """Extract topics from a batch of reviews using GPT"""
        results = []
        for i in tqdm(range(0, len(reviews_batch), 20), desc="Extracting Topics", leave=False):
            batch = reviews_batch[i:i+20]
            prompt = f"""
            Analyze these app store reviews for a food delivery app and extract the main topic/issue from each review.
            Known topic categories: {self.seed_topics}
            For each review, identify:
            1. The main issue/topic (use existing categories if possible, create new if needed)
            2. Whether it's a complaint, request, or compliment
            Reviews:
            {json.dumps([{"id": idx, "text": review} for idx, review in enumerate(batch)], indent=2)}
            Return a JSON list with format:
            [
                {{
                    "review_id": 0,
                    "topic": "topic_name",
                    "type": "complaint|request|compliment",
                    "confidence": 0.9
                }},
                ...
            ]
            Guidelines:
            - Be specific but not overly granular
            - Focus on actionable feedback
            - Group similar issues under same topic name
            - Create new topics only if significantly different from existing ones
            """
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                parsed_json = json.loads(response.choices[0].message.content)
                if isinstance(parsed_json, dict) and 'reviews' in parsed_json:
                    batch_results = parsed_json['reviews']
                else:
                    batch_results = parsed_json
                for res in batch_results:
                    review_index = res.get("review_id")
                    if review_index is not None and review_index < len(batch):
                        res["review"] = batch[review_index]
                results.extend(batch_results)
            except Exception as e:
                print(f"Error processing batch {i}: {e}")
        return results

    def consolidate_similar_topics(self, extracted_topics):
        """Consolidate similar topics using sentence embeddings."""
        if not extracted_topics:
            return []
        df = pd.DataFrame(extracted_topics)
        unique_topics = df['topic'].unique().tolist()
        topic_embeddings = self.embedding_model.encode(unique_topics)
        similarity_matrix = cosine_similarity(topic_embeddings)
        groups = {}
        for i, topic in enumerate(unique_topics):
            if topic not in [item for sublist in groups.values() for item in sublist]:
                similar_indices = np.where(similarity_matrix[i] > self.similarity_threshold)[0]
                similar_topics = [unique_topics[j] for j in similar_indices]
                groups[topic] = similar_topics
        topic_map = {}
        for master_topic, similar_topics in groups.items():
            canonical_name = self.choose_canonical_topic(similar_topics)
            for topic in similar_topics:
                topic_map[topic] = canonical_name
        df['topic'] = df['topic'].map(topic_map).fillna(df['topic'])
        return df.to_dict('records')

    def choose_canonical_topic(self, similar_topics):
        """Choose the best canonical name for a group of similar topics"""
        for topic in similar_topics:
            if topic in self.seed_topics:
                return topic
        return min(similar_topics, key=len)

    def consolidate_topics_with_llm(self, daily_results):
        """Uses an LLM to perform a final consolidation of topics across all days."""
        print("\n--- Consolidating topics with LLM for final report ---")
        all_topics = set()
        for result in daily_results:
            all_topics.update(result['topic_counts'].keys())
        prompt = f"""
        You are an expert data analyst. I have a list of topics from app reviews. Consolidate them into a smaller set of high-level categories.
        Provide a JSON object mapping each original topic to its new, consolidated category.
        Topics to consolidate:
        {json.dumps(list(all_topics), indent=2)}
        Example output format:
        {{
            "Late delivery": "Delivery Issues",
            "Food arrived cold": "Food Quality",
            "App is buggy": "App Performance"
        }}
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            topic_mapping = json.loads(response.choices[0].message.content)
            for result in daily_results:
                for detailed_topic in result['detailed_topics']:
                    old_topic = detailed_topic['topic']
                    if old_topic in topic_mapping:
                        detailed_topic['topic'] = topic_mapping[old_topic]
                new_topic_counts = Counter([t['topic'] for t in result['detailed_topics']])
                result['topic_counts'] = dict(new_topic_counts)
            print("Topic consolidation complete.")
            return daily_results
        except Exception as e:
            print(f"Error during LLM topic consolidation: {e}")
            return daily_results
