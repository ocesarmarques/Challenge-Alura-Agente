from app.config import settings


def test_default_region_is_sao_paulo():
    assert settings.oci_region == "sa-saopaulo-1"


def test_default_models_are_configured():
    assert settings.oci_embedding_model_id == "cohere.embed-v4.0"
    assert settings.oci_chat_model_id == "cohere.command-a-03-2025"


def test_embedding_dimension():
    assert settings.embedding_dimensions == 1024


def test_default_min_relevance_score():
    assert settings.min_relevance_score == 0.32
