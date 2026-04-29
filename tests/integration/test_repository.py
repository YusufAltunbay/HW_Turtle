"""
SQLiteTurtleRepository entegrasyon testleri.
In-memory SQLite veritabanı kullanır — disk yazmaz.
"""
import numpy as np
import pytest
from uuid import uuid4

from turtle_id.core.models.embedding import Embedding
from turtle_id.core.models.turtle import Turtle
from turtle_id.infrastructure.persistence.database import (
    build_engine,
    build_session_factory,
    init_db,
)
from turtle_id.infrastructure.persistence.sqlite_turtle_repo import SQLiteTurtleRepository


@pytest.fixture()
def repo():
    """Her test için temiz in-memory veritabanı."""
    engine = build_engine(":memory:")
    session_factory = build_session_factory(engine)
    init_db(engine)
    return SQLiteTurtleRepository(session_factory)


def _turtle(name="Ninja") -> Turtle:
    return Turtle(name=name, species="Chelonia mydas", primary_photo_path="test.jpg")


def _embedding(turtle_id) -> Embedding:
    v = np.random.randn(1280).astype(np.float32)
    v = v / np.linalg.norm(v)
    return Embedding(turtle_id=turtle_id, vector=v, photo_path="test.jpg")


class TestSave:
    def test_kaydet_ve_bul(self, repo):
        t = _turtle()
        saved = repo.save(t)
        found = repo.find_by_id(saved.id)
        assert found is not None
        assert found.name == "Ninja"

    def test_embedding_ile_kaydet(self, repo):
        t = _turtle()
        emb = _embedding(t.id)
        t.add_embedding(emb)
        repo.save(t)
        found = repo.find_by_id(t.id)
        assert len(found.embeddings) == 1
        assert found.embeddings[0].dimension == 1280

    def test_embedding_vektoru_bozulmadan_geri_gelir(self, repo):
        t = _turtle()
        emb = _embedding(t.id)
        original_vector = emb.vector.copy()
        t.add_embedding(emb)
        repo.save(t)
        found = repo.find_by_id(t.id)
        np.testing.assert_array_almost_equal(
            found.embeddings[0].vector, original_vector, decimal=5
        )


class TestFindAll:
    def test_aktif_kayitlari_listele(self, repo):
        repo.save(_turtle("A"))
        repo.save(_turtle("B"))
        all_turtles = repo.find_all()
        assert len(all_turtles) == 2

    def test_silinen_kayitlar_listelenmez(self, repo):
        t = _turtle()
        repo.save(t)
        repo.delete(t.id)
        all_turtles = repo.find_all()
        assert len(all_turtles) == 0

    def test_olmayan_id_none_doner(self, repo):
        result = repo.find_by_id(uuid4())
        assert result is None


class TestUpdate:
    def test_guncelleme(self, repo):
        t = _turtle()
        repo.save(t)
        t.name = "Turbo"
        t.species = "Caretta caretta"
        repo.update(t)
        found = repo.find_by_id(t.id)
        assert found.name == "Turbo"
        assert found.species == "Caretta caretta"


class TestAddEmbedding:
    def test_sonradan_embedding_ekle(self, repo):
        t = _turtle()
        repo.save(t)
        emb = _embedding(t.id)
        repo.add_embedding(emb)
        found = repo.find_by_id(t.id)
        assert len(found.embeddings) == 1

    def test_get_all_embeddings(self, repo):
        t1, t2 = _turtle("A"), _turtle("B")
        e1, e2 = _embedding(t1.id), _embedding(t2.id)
        t1.add_embedding(e1)
        t2.add_embedding(e2)
        repo.save(t1)
        repo.save(t2)
        all_embs = repo.get_all_embeddings()
        assert len(all_embs) == 2

    def test_silinen_kaplumaganin_embeddingleri_gelmez(self, repo):
        t = _turtle()
        emb = _embedding(t.id)
        t.add_embedding(emb)
        repo.save(t)
        repo.delete(t.id)
        all_embs = repo.get_all_embeddings()
        assert len(all_embs) == 0
