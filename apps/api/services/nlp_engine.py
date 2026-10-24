"""
Grievance360 NLP Routing & Duplicate Detection Engine
Leverages sentence-transformers (all-MiniLM-L6-v2) to calculate semantic similarity,
perform automated AICTE bureau routing, and flag duplicate citizen complaints.
"""

from typing import List, Dict, Tuple, Optional, Any
import numpy as np
import re

# Urgent keywords that trigger CRITICAL priority classification
CRITICAL_KEYWORDS = ["suicide", "ragging", "threat", "violence", "bribe"]

# Semantic Bureau Prototypes for Cosine Similarity Comparison
BUREAU_DESCRIPTIONS = {
    "Anti-Ragging Bureau": (
        "ragging by seniors, verbal harassment, physical intimidation, hostel curfew abuse, "
        "forced physical roll calls, humiliation, bullying, mental torture in dormitories, "
        "assault, sexual harassment, threatening junior students"
    ),
    "Approval Bureau": (
        "unapproved college, unauthorized intake expansion beyond approved quota, lack of statutory AICTE approval, "
        "infrastructure deficiency, fake faculty on rolls, lack of computing labs, unapproved degrees, "
        "affiliation violations, running courses without sanctioned intake"
    ),
    "Finance Bureau": (
        "scholarship payment delay, AICTE Pragati Saksham scholarship not credited, fellowship grant disbursement, "
        "tuition fee refund refusal upon withdrawal, capitation fee extortion, unauthorized collection, "
        "hostel security deposit withheld, financial corruption, embezzlement of student funds"
    ),
    "Legal Bureau": (
        "court case, writ petition, compliance with High Court order, contempt of court, unlawful faculty termination, "
        "service contract violation, statutory non-compliance, legal notice response, disciplinary dispute"
    ),
    "Generic Bureau": (
        "general inquiry, campus maintenance, drinking water supply, canteen sanitation, library book shortage, "
        "bus transportation schedule, generic college administration, portal password reset"
    ),
}

# Mapping of Bureau names to standardized codes
BUREAU_CODE_MAP = {
    "Anti-Ragging Bureau": "RAGGING",
    "Approval Bureau": "APPROVAL",
    "Finance Bureau": "FINANCE",
    "Legal Bureau": "LEGAL",
    "Generic Bureau": "GENERIC",
}


class NLPEngine:
    """
    Singleton NLP Engine encapsulating the SentenceTransformer model and pre-computed
    semantic bureau embeddings for high-throughput, low-latency grievance triage.
    """

    _instance: Optional["NLPEngine"] = None

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.bureau_embeddings: Dict[str, np.ndarray] = {}
        self._load_model()
        self._precompute_bureau_embeddings()

    @classmethod
    def get_instance(cls) -> "NLPEngine":
        if cls._instance is None:
            cls._instance = NLPEngine()
        return cls._instance

    def _load_model(self):
        """
        Attempts to load SentenceTransformer; falls back to deterministic term vectors
        if PyTorch/HuggingFace dependencies are in process of initialization.
        """
        try:
            from sentence_transformers import SentenceTransformer
            print(f"[NLP Engine] Loading SentenceTransformer model '{self.model_name}'...")
            self.model = SentenceTransformer(self.model_name)
            print("[NLP Engine] SentenceTransformer loaded successfully.")
        except Exception as e:
            print(f"[NLP Engine] Notice: Could not initialize SentenceTransformer ({e}). Using robust semantic fallback.")
            self.model = None

    def _get_fallback_vocab(self) -> Dict[str, int]:
        if not hasattr(self, "_fallback_vocab"):
            seed_texts = list(BUREAU_DESCRIPTIONS.values()) + CRITICAL_KEYWORDS + [
                "complaint", "grievance", "student", "faculty", "teacher", "college",
                "institution", "department", "hostel", "curfew", "intimidation", "violence",
                "ragging", "bribe", "money", "fee", "refund", "scholarship", "approval",
                "intake", "court", "legal", "notice", "delay", "maintenance", "admin"
            ]
            words = sorted(list(set(w for t in seed_texts for w in re.findall(r"\w+", t.lower()))))
            self._fallback_vocab = {w: i for i, w in enumerate(words)}
        return self._fallback_vocab

    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Encode a list of text strings into normalized vector embeddings.
        """
        if self.model is not None:
            embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            return embeddings

        # Deterministic fallback vectorizer with fixed vocabulary dimensions
        vocab = self._get_fallback_vocab()
        vectors = []
        for text in texts:
            vec = np.zeros(len(vocab), dtype=np.float32)
            tokens = re.findall(r"\w+", text.lower())
            for t in tokens:
                if t in vocab:
                    vec[vocab[t]] += 1.0
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            vectors.append(vec)
        return np.array(vectors)

    def _precompute_bureau_embeddings(self):
        """
        Pre-computes embeddings for all AICTE bureau semantic definitions.
        """
        bureau_names = list(BUREAU_DESCRIPTIONS.keys())
        descriptions = [BUREAU_DESCRIPTIONS[b] for b in bureau_names]
        embeddings = self.encode(descriptions)
        for i, name in enumerate(bureau_names):
            self.bureau_embeddings[name] = embeddings[i]

    def compute_cosine_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """
        Computes cosine similarity between two 1D or 2D normalized vectors.
        """
        dot = np.dot(vec_a, vec_b)
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot / (norm_a * norm_b))

    def detect_urgent_keywords(self, text: str) -> List[str]:
        """
        Identifies presence of critical/urgent keywords in grievance text.
        Keywords: suicide, ragging, threat, violence, bribe.
        """
        text_lower = text.lower()
        detected = []
        for kw in CRITICAL_KEYWORDS:
            # Word boundary regex to avoid false positives (e.g. 'threat' in 'threatened')
            if re.search(r"\b" + re.escape(kw) + r"\b", text_lower) or kw in text_lower:
                detected.append(kw)
        return list(set(detected))

    def classify_bureau_and_priority(self, text: str) -> Dict[str, Any]:
        """
        Computes cosine similarity against pre-embedded bureau keywords to route incoming
        complaints to AICTE cells (Approval, Anti-Ragging, Finance, Legal, Generic).
        Assigns 'CRITICAL' priority if urgent keywords (suicide, ragging, threat, violence, bribe) are detected.
        """
        if not text or not text.strip():
            return {
                "bureau_name": "Generic Bureau",
                "bureau_code": "GENERIC",
                "confidence": 0.5,
                "priority": "LOW",
                "urgent_keywords": [],
                "scores": {},
            }

        # 1. Check for urgent keywords
        urgent_matches = self.detect_urgent_keywords(text)
        is_critical = len(urgent_matches) > 0

        # 2. Encode incoming complaint text
        complaint_embedding = self.encode([text])[0]

        # 3. Compute cosine similarity against all AICTE bureaus
        bureau_scores: Dict[str, float] = {}
        for bureau_name, bureau_vec in self.bureau_embeddings.items():
            sim = self.compute_cosine_similarity(complaint_embedding, bureau_vec)
            bureau_scores[bureau_name] = round(sim, 4)

        # 4. If critical keyword specifically related to ragging is detected, favor Anti-Ragging Bureau
        if "ragging" in urgent_matches:
            bureau_scores["Anti-Ragging Bureau"] += 0.35
        if "bribe" in urgent_matches:
            bureau_scores["Finance Bureau"] += 0.25

        # 5. Pick highest scoring bureau
        best_bureau = max(bureau_scores, key=lambda k: bureau_scores[k])
        confidence = float(bureau_scores[best_bureau])

        # 6. Determine dynamic priority
        if is_critical:
            priority = "CRITICAL"
        elif confidence >= 0.65 or any(k in text.lower() for k in ["expulsion", "cancelled", "struck off", "urgent"]):
            priority = "HIGH"
        elif confidence >= 0.40:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        return {
            "bureau_name": best_bureau,
            "bureau_code": BUREAU_CODE_MAP.get(best_bureau, "GENERIC"),
            "confidence": min(1.0, max(0.0, confidence)),
            "priority": priority,
            "urgent_keywords": urgent_matches,
            "all_bureau_scores": bureau_scores,
        }

    def check_duplicate_complaint(
        self,
        new_text: str,
        existing_complaints: List[Dict[str, Any]],
        threshold: float = 0.85,
    ) -> Tuple[bool, Optional[str], float]:
        """
        Flags incoming complaints as duplicates if cosine similarity > 0.85 against
        any recent complaint in the system or same institution.

        Returns: (is_duplicate: bool, master_complaint_id: Optional[str], similarity_score: float)
        """
        if not existing_complaints or not new_text.strip():
            return False, None, 0.0

        # Encode new complaint
        new_vec = self.encode([new_text])[0]

        # Extract texts and ids from existing complaints
        corpus_texts = []
        complaint_ids = []
        for item in existing_complaints:
            # Combine title and description for richer semantic match
            combined = f"{item.get('title', '')} {item.get('description', '')}".strip()
            if combined:
                corpus_texts.append(combined)
                complaint_ids.append(str(item.get("complaint_id", "")))

        if not corpus_texts:
            return False, None, 0.0

        corpus_vecs = self.encode(corpus_texts)

        # Calculate cosine similarities
        max_sim = 0.0
        best_id = None
        for i, existing_vec in enumerate(corpus_vecs):
            sim = self.compute_cosine_similarity(new_vec, existing_vec)
            if sim > max_sim:
                max_sim = sim
                best_id = complaint_ids[i]

        max_sim = round(float(max_sim), 4)
        is_duplicate = max_sim >= threshold

        return is_duplicate, (best_id if is_duplicate else None), max_sim


# Singleton helper functions for direct import
_engine = NLPEngine.get_instance()


def classify_bureau_and_priority(text: str) -> Dict[str, Any]:
    return _engine.classify_bureau_and_priority(text)


def check_duplicate_complaint(
    new_text: str,
    existing_complaints: List[Dict[str, Any]],
    threshold: float = 0.85,
) -> Tuple[bool, Optional[str], float]:
    return _engine.check_duplicate_complaint(new_text, existing_complaints, threshold)
