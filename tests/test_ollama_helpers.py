from modules import helpers


class DummyClient:
    def __init__(self, should_fail=False, models=None):
        self.should_fail = should_fail
        self._models = models or []

    def list(self):
        if self.should_fail:
            raise RuntimeError("connection failed")
        return {"models": self._models}

    def pull(self, model, stream=False):
        if self.should_fail:
            raise RuntimeError("pull failed")
        return {"status": "success", "model": model}


def test_is_ollama_available_handles_failure(monkeypatch):
    monkeypatch.setattr(
        helpers.ollama, "Client", lambda host=None: DummyClient(should_fail=True)
    )
    assert helpers.is_ollama_available() is False


def test_get_ollama_models_filters_embeddings(monkeypatch):
    sample_models = [
        {"model": "llama3", "details": {"family": "llama"}},
        {"model": "nomic-embed-text:latest", "details": {"family": "embed"}},
    ]
    monkeypatch.setattr(
        helpers.ollama, "Client", lambda host=None: DummyClient(models=sample_models)
    )
    assert helpers.get_ollama_models("gpts") == ["llama3"]
    assert helpers.get_ollama_models("embeddings") == ["nomic-embed-text:latest"]


def test_pull_ollama_model_returns_false_on_error(monkeypatch):
    monkeypatch.setattr(
        helpers.ollama, "Client", lambda host=None: DummyClient(should_fail=True)
    )
    assert helpers.pull_ollama_model("llama3") is False
