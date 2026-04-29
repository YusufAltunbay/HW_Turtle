"""
Domain modelleri birim testleri.
"""
import pytest
import numpy as np
from uuid import uuid4
from datetime import datetime

from turtle_id.core.models.turtle import Turtle
from turtle_id.core.models.embedding import Embedding
from turtle_id.core.models.match_result import MatchResult


class TestTurtle:
    def test_varsayilan_degerler(self):
        t = Turtle(name="Ninja", primary_photo_path="foto.jpg")
        assert t.name == "Ninja"
        assert t.species == ""
        assert t.notes == ""
        assert t.has_embeddings() is False
        assert isinstance(t.registration_date, datetime)

    def test_embedding_ekleme(self):
        t = Turtle(name="Ninja", primary_photo_path="foto.jpg")
        emb = Embedding(
            turtle_id=t.id,
            vector=np.ones(1280, dtype=np.float32),
            photo_path="foto.jpg",
        )
        t.add_embedding(emb)
        assert t.has_embeddings() is True
        assert len(t.embeddings) == 1

    def test_birden_fazla_embedding(self):
        t = Turtle(name="Turbo", primary_photo_path="foto.jpg")
        for _ in range(3):
            emb = Embedding(
                turtle_id=t.id,
                vector=np.random.randn(1280).astype(np.float32),
                photo_path="foto.jpg",
            )
            t.add_embedding(emb)
        assert len(t.embeddings) == 3

    def test_repr_icinde_id_kisaltilmis(self):
        t = Turtle(name="Kabuk", primary_photo_path="foto.jpg")
        r = repr(t)
        assert "Kabuk" in r
        assert "Turtle(" in r


class TestEmbedding:
    def _unit_vector(self, dim: int = 1280) -> np.ndarray:
        v = np.random.randn(dim).astype(np.float32)
        return v / np.linalg.norm(v)

    def test_normalize_kontrol_basarili(self):
        emb = Embedding(
            turtle_id=uuid4(),
            vector=self._unit_vector(),
            photo_path="foto.jpg",
        )
        assert emb.is_normalized() is True

    def test_normalize_kontrol_basarisiz(self):
        emb = Embedding(
            turtle_id=uuid4(),
            vector=np.ones(1280, dtype=np.float32),  # normalize değil
            photo_path="foto.jpg",
        )
        assert emb.is_normalized() is False

    def test_dimension_ozellik(self):
        v = self._unit_vector(512)
        emb = Embedding(turtle_id=uuid4(), vector=v, photo_path="x.jpg")
        assert emb.dimension == 512

    def test_varsayilan_model_adi(self):
        emb = Embedding(
            turtle_id=uuid4(),
            vector=self._unit_vector(),
            photo_path="x.jpg",
        )
        assert emb.model_name == "efficientnet_b0"

    def test_esitlik_id_bazli(self):
        tid = uuid4()
        v = self._unit_vector()
        emb1 = Embedding(turtle_id=tid, vector=v, photo_path="x.jpg")
        emb2 = Embedding(turtle_id=tid, vector=v, photo_path="x.jpg")
        assert emb1 != emb2   # farklı id → farklı nesne


class TestMatchResult:
    def test_eslesme_var_confidence(self):
        mr = MatchResult(
            is_match=True,
            similarity_score=0.91,
            threshold_used=0.82,
        )
        assert mr.confidence > 0.0
        assert mr.confidence <= 1.0

    def test_eslesme_yok_confidence_sifir(self):
        mr = MatchResult.no_match(similarity_score=0.50, threshold=0.82)
        assert mr.is_match is False
        assert mr.confidence == 0.0
        assert mr.matched_turtle_id is None

    def test_is_identified_property(self):
        from turtle_id.core.use_cases.verify_turtle import VerifyTurtleResponse
        mr = MatchResult(
            is_match=True,
            similarity_score=0.90,
            threshold_used=0.82,
            matched_turtle_id=uuid4(),
        )
        t = Turtle(name="Ninja", primary_photo_path="foto.jpg")
        mr.matched_turtle = t
        resp = VerifyTurtleResponse(success=True, match_result=mr, turtle=t)
        assert resp.is_identified is True

    def test_esik_uzeri_skor_tam_guven(self):
        mr = MatchResult(
            is_match=True,
            similarity_score=0.99,
            threshold_used=0.82,
        )
        assert mr.confidence == 1.0   # 0.99/0.82 > 1 → kırpılır
