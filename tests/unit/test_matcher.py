"""
CosineMatcher birim testleri.
"""
import numpy as np
import pytest
from uuid import uuid4

from turtle_id.core.models.embedding import Embedding
from turtle_id.infrastructure.matching.cosine_matcher import CosineMatcher


def _make_embedding(vector: np.ndarray, turtle_id=None) -> Embedding:
    return Embedding(
        turtle_id=turtle_id or uuid4(),
        vector=vector,
        photo_path="test.jpg",
    )


def _unit(v: np.ndarray) -> np.ndarray:
    return (v / np.linalg.norm(v)).astype(np.float32)


class TestCosineMatcher:
    def setup_method(self):
        self.matcher = CosineMatcher()

    def test_ayni_vektor_eslesir(self):
        v = _unit(np.random.randn(1280).astype(np.float32))
        emb = _make_embedding(v)
        result = self.matcher.find_best_match(v, [emb], threshold=0.82)
        assert result.is_match is True
        assert result.similarity_score > 0.99

    def test_tam_zit_vektor_eslesmez(self):
        v = _unit(np.ones(1280, dtype=np.float32))
        anti = _unit(-np.ones(1280, dtype=np.float32))
        emb = _make_embedding(anti)
        result = self.matcher.find_best_match(v, [emb], threshold=0.82)
        assert result.is_match is False
        assert result.similarity_score < 0.0

    def test_bos_aday_listesi(self):
        v = _unit(np.random.randn(1280).astype(np.float32))
        result = self.matcher.find_best_match(v, [], threshold=0.82)
        assert result.is_match is False
        assert result.similarity_score == 0.0

    def test_en_iyi_aday_secilir(self):
        tid_dogru = uuid4()
        tid_yanlis = uuid4()

        v_query = _unit(np.ones(1280, dtype=np.float32))
        v_yakin = _unit(np.ones(1280, dtype=np.float32) + np.random.randn(1280) * 0.01)
        v_uzak = _unit(-np.ones(1280, dtype=np.float32))

        candidates = [
            _make_embedding(v_uzak, tid_yanlis),
            _make_embedding(v_yakin, tid_dogru),
        ]
        result = self.matcher.find_best_match(v_query, candidates, threshold=0.82)
        assert result.is_match is True
        assert result.matched_turtle_id == tid_dogru

    def test_esik_alti_eslesmez(self):
        v1 = _unit(np.random.randn(1280).astype(np.float32))
        v2 = _unit(np.random.randn(1280).astype(np.float32))
        emb = _make_embedding(v2)
        # Rastgele vektörler arasında skor genellikle düşük olur
        result = self.matcher.find_best_match(v1, [emb], threshold=0.999)
        assert result.is_match is False

    def test_top_k_adaylar(self):
        tids = [uuid4() for _ in range(5)]
        candidates = [
            _make_embedding(_unit(np.random.randn(1280).astype(np.float32)), tid)
            for tid in tids
        ]
        v = _unit(np.random.randn(1280).astype(np.float32))
        result = self.matcher.find_best_match(v, candidates, threshold=0.0, top_k=3)
        assert len(result.top_candidates) == 3

    def test_no_match_fabrika(self):
        from turtle_id.core.models.match_result import MatchResult
        mr = MatchResult.no_match(similarity_score=0.45, threshold=0.82)
        assert mr.is_match is False
        assert mr.confidence == 0.0
        assert mr.matched_turtle_id is None
