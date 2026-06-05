import ollama
from typing import Iterator
from core.config import settings
from core.security.network_guard import network_guard

class OllamaClient:
    """Interacts with the local Ollama daemon."""
    
    def __init__(self):
        # We explicitly ensure we only connect locally
        self.host = "http://127.0.0.1:11434"
        self.client = ollama.Client(host=self.host)
        
    def list_models(self) -> list[str]:
        """Returns a list of locally installed models."""
        try:
            models_info = self.client.list()
            models = []
            # Support both object list and dictionary response styles
            for m in models_info.get('models', []):
                if hasattr(m, 'model') and m.model:
                    models.append(m.model)
                elif isinstance(m, dict) and 'model' in m:
                    models.append(m['model'])
                elif isinstance(m, dict) and 'name' in m:
                    models.append(m['name'])
            return models
        except Exception as e:
            print(f"Error connecting to local Ollama: {e}")
            return []

    def _get_target_model(self, model: str | None = None) -> str:
        from core.config import settings
        target_model = model or settings.ollama_model
        available_models = self.list_models()
        if target_model not in available_models and available_models:
            print(f"Model {target_model} not found locally. Falling back to {available_models[0]}")
            return available_models[0]
        return target_model
    def chat_stream(self, messages: list[dict], model: str | None = None) -> Iterator[str]:
        """Streams a chat response from local Ollama."""
        target_model = self._get_target_model(model)
        
        # Security sanity check, ensure we aren't calling remote somehow
        network_guard.check("127.0.0.1")
        
        response_stream = self.client.chat(
            model=target_model,
            messages=messages,
            stream=True
        )
        
        for chunk in response_stream:
            yield chunk['message']['content']
            
    def generate(self, prompt: str, model: str | None = None, context: str | None = None, history: list | None = None) -> str:
        """Generates a single string response, optionally with history and context."""
        target_model = self._get_target_model(model)
        
        # Security sanity check
        network_guard.check("127.0.0.1")
        
        messages = []
        if history:
            # Clone history to avoid modifying it
            messages.extend(list(history))
            
        user_content = prompt
        if context:
            user_content = (
                f"Use the following context to answer the user's question. "
                f"If the context doesn't contain the answer, say so.\n\n"
                f"Context:\n{context}\n\n"
                f"Question: {prompt}"
            )
            
        messages.append({"role": "user", "content": user_content})
        
        try:
            response = self.client.chat(
                model=target_model,
                messages=messages
            )
            return response['message']['content']
        except Exception as e:
            print(f"Ollama chat error: {e}. Falling back to simple generate.")
            resp = self.client.generate(
                model=target_model,
                prompt=prompt
            )
            return resp['response']

    def check_connection(self) -> bool:
        """Checks if the local Ollama service is running and accessible."""
        try:
            self.client.list()
            return True
        except Exception:
            return False

