import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from core.models import Post

class AIGuardrail:
    _vectorizer = None
    
    @classmethod
    def get_vectorizer(cls):
        if cls._vectorizer is None:
            # Lazy loading để tiết kiệm RAM trên Render Free Tier
            cls._vectorizer = TfidfVectorizer(stop_words=None) # Tiếng Việt có thể không cần stop_words mặc định của sklearn
        return cls._vectorizer

    @staticmethod
    def check_duplicate(new_description, user_id, threshold=0.85):
        """
        Kiểm tra xem tin mới có giống >85% tin cũ của cùng user không.
        """
        # Lấy các bài đăng cũ của user này (chỉ lấy 50 bài gần nhất để tiết kiệm RAM)
        old_posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).limit(50).all()
        
        if not old_posts:
            return False, 0.0
        
        old_descriptions = [post.description for post in old_posts]
        all_texts = old_descriptions + [new_description]
        
        try:
            vectorizer = AIGuardrail.get_vectorizer()
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            
            # So sánh tin cuối cùng (mới) với tất cả tin cũ
            cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
            max_sim = np.max(cosine_sim)
            
            if max_sim > threshold:
                return True, max_sim
            return False, max_sim
        except Exception as e:
            print(f"AI Guardrail Error: {e}")
            return False, 0.0

    @staticmethod
    def smart_matching(target_description, limit=5):
        """
        Gợi ý các bài viết liên quan dựa trên nội dung.
        """
        # Logic similar to duplicate check but for all posts
        # To be implemented with scaling consideration
        pass
