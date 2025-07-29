"""
Model Selection System for xPyLLMent ASI-ARCH

Leverages Pixeltable's native model infrastructure to provide a unified
interface for discovering, configuring, and switching between AI models
from different providers.
"""

import pixeltable as pxt
from pixeltable.functions import anthropic, openai, ollama, huggingface, gemini
from pixeltable import env
from typing import Dict, List, Optional, Any, Callable
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.columns import Columns
from dataclasses import dataclass
import json
from pathlib import Path
import requests
import subprocess

console = Console()

@dataclass
class ModelInfo:
    """Information about an available model"""
    provider: str
    model_id: str
    display_name: str
    description: str
    context_length: Optional[int] = None
    capabilities: List[str] = None
    cost_per_token: Optional[float] = None
    local: bool = False
    available: bool = True

class ModelRegistry:
    """Registry of available models across providers"""
    
    def __init__(self):
        self.models: Dict[str, List[ModelInfo]] = {}
        self.console = Console()
        self._load_model_registry()
    
    def _load_model_registry(self):
        """Load model registry with known models from each provider"""
        
        # Anthropic Models
        self.models['anthropic'] = [
            ModelInfo(
                provider='anthropic',
                model_id='claude-3-5-sonnet-20241022',
                display_name='Claude 3.5 Sonnet',
                description='Most capable Claude model for complex reasoning',
                context_length=200000,
                capabilities=['text', 'analysis', 'coding', 'reasoning']
            ),
            ModelInfo(
                provider='anthropic', 
                model_id='claude-3-5-haiku-20241022',
                display_name='Claude 3.5 Haiku',
                description='Fast and efficient Claude model',
                context_length=200000,
                capabilities=['text', 'analysis', 'fast_response']
            ),
            ModelInfo(
                provider='anthropic',
                model_id='claude-3-opus-20240229',
                display_name='Claude 3 Opus',
                description='Most powerful Claude model for complex tasks',
                context_length=200000,
                capabilities=['text', 'analysis', 'coding', 'reasoning', 'complex_tasks']
            )
        ]
        
        # OpenAI Models
        self.models['openai'] = [
            ModelInfo(
                provider='openai',
                model_id='gpt-4o',
                display_name='GPT-4o',
                description='Latest multimodal GPT model',
                context_length=128000,
                capabilities=['text', 'vision', 'reasoning', 'coding']
            ),
            ModelInfo(
                provider='openai',
                model_id='gpt-4o-mini',
                display_name='GPT-4o Mini',
                description='Fast and cost-effective GPT model',
                context_length=128000,
                capabilities=['text', 'vision', 'fast_response']
            ),
            ModelInfo(
                provider='openai',
                model_id='gpt-4-turbo',
                display_name='GPT-4 Turbo',
                description='High-performance GPT-4 variant',
                context_length=128000,
                capabilities=['text', 'vision', 'reasoning', 'coding']
            )
        ]
        
        # Ollama Models (check what's available locally)
        self.models['ollama'] = self._discover_ollama_models()
        
        # HuggingFace Models (curated selection)
        self.models['huggingface'] = [
            ModelInfo(
                provider='huggingface',
                model_id='microsoft/DialoGPT-medium',
                display_name='DialoGPT Medium',
                description='Conversational AI model',
                capabilities=['text', 'conversation'],
                local=True
            ),
            ModelInfo(
                provider='huggingface',
                model_id='facebook/blenderbot-400M-distill',
                display_name='BlenderBot 400M',
                description='Lightweight conversational model',
                capabilities=['text', 'conversation'],
                local=True
            )
        ]
        
        # Gemini Models
        self.models['gemini'] = [
            ModelInfo(
                provider='gemini',
                model_id='gemini-1.5-pro',
                display_name='Gemini 1.5 Pro',
                description='Google\'s most capable model',
                context_length=2000000,
                capabilities=['text', 'vision', 'reasoning', 'long_context']
            ),
            ModelInfo(
                provider='gemini',
                model_id='gemini-1.5-flash',
                display_name='Gemini 1.5 Flash',
                description='Fast and efficient Gemini model',
                context_length=1000000,
                capabilities=['text', 'vision', 'fast_response']
            )
        ]
    
    def _discover_ollama_models(self) -> List[ModelInfo]:
        """Discover locally available Ollama models"""
        ollama_models = []
        
        try:
            # Check if Ollama is available
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if parts:
                            model_name = parts[0]
                            ollama_models.append(ModelInfo(
                                provider='ollama',
                                model_id=model_name,
                                display_name=f'Ollama {model_name}',
                                description=f'Local Ollama model: {model_name}',
                                capabilities=['text', 'local'],
                                local=True,
                                available=True
                            ))
            else:
                # Ollama not available, add common models as unavailable
                common_models = [
                    ('llama3.2:3b', 'Llama 3.2 3B'),
                    ('qwen2.5:0.5b', 'Qwen 2.5 0.5B'),
                    ('mistral:7b', 'Mistral 7B'),
                    ('codellama:7b', 'Code Llama 7B')
                ]
                
                for model_id, display_name in common_models:
                    ollama_models.append(ModelInfo(
                        provider='ollama',
                        model_id=model_id,
                        display_name=display_name,
                        description=f'Local model (requires Ollama): {display_name}',
                        capabilities=['text', 'local'],
                        local=True,
                        available=False
                    ))
                        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Ollama not installed, return empty list
            pass
            
        return ollama_models
    
    def get_provider_models(self, provider: str) -> List[ModelInfo]:
        """Get all models for a specific provider"""
        return self.models.get(provider, [])
    
    def get_all_providers(self) -> List[str]:
        """Get list of all available providers"""
        return list(self.models.keys())
    
    def get_model_info(self, provider: str, model_id: str) -> Optional[ModelInfo]:
        """Get detailed info for a specific model"""
        for model in self.models.get(provider, []):
            if model.model_id == model_id:
                return model
        return None
    
    def get_available_models(self, provider: str = None) -> List[ModelInfo]:
        """Get all available models, optionally filtered by provider"""
        if provider:
            return [m for m in self.models.get(provider, []) if m.available]
        
        all_models = []
        for provider_models in self.models.values():
            all_models.extend([m for m in provider_models if m.available])
        return all_models

class ModelManager:
    """Manages model selection and configuration for ASI-ARCH"""
    
    def __init__(self):
        self.registry = ModelRegistry()
        self.config_file = Path.home() / '.pixeltable' / 'xpyllment_models.json'
        self.current_config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load model configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'default_provider': 'anthropic',
            'default_model': 'claude-3-5-sonnet-20241022',
            'provider_preferences': {},
            'model_overrides': {}
        }
    
    def _save_config(self):
        """Save model configuration"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.current_config, f, indent=2)
    
    def interactive_setup(self) -> Dict[str, str]:
        """Interactive model selection setup"""
        
        console.print(Panel.fit(
            "[bold blue]🤖 Model Configuration Setup[/bold blue]\\n"
            "[dim]Configure AI models for xPyLLMent ASI-ARCH[/dim]",
            style="blue"
        ))
        
        # Check provider availability
        available_providers = self._check_provider_availability()
        
        if not available_providers:
            console.print("[red]❌ No model providers are configured![/red]")
            console.print("\\nPlease configure at least one provider:")
            console.print("• Set ANTHROPIC_API_KEY for Claude models")
            console.print("• Set OPENAI_API_KEY for GPT models") 
            console.print("• Install Ollama for local models")
            return {}
        
        # Show available providers
        console.print("\\n[bold]Available Providers:[/bold]")
        provider_table = Table()
        provider_table.add_column("Provider", style="cyan")
        provider_table.add_column("Status", style="green")
        provider_table.add_column("Models Available", style="dim")
        
        for provider, info in available_providers.items():
            model_count = len([m for m in self.registry.get_provider_models(provider) if m.available])
            provider_table.add_row(
                provider.title(),
                "✅ Ready" if info['available'] else "❌ Not configured",
                str(model_count)
            )
        
        console.print(provider_table)
        
        # Let user select provider
        provider_choices = list(available_providers.keys())
        console.print(f"\\nSelect primary provider [1-{len(provider_choices)}]:")
        for i, provider in enumerate(provider_choices, 1):
            console.print(f"  {i}. {provider.title()}")
        
        while True:
            choice = Prompt.ask("Provider choice", default="1")
            try:
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(provider_choices):
                        selected_provider = provider_choices[idx]
                        break
                elif choice.lower() in provider_choices:
                    selected_provider = choice.lower()
                    break
            except:
                pass
            console.print("❌ Invalid choice, please try again")
        
        # Show models for selected provider
        models = self.registry.get_available_models(selected_provider)
        if not models:
            console.print(f"[red]No models available for {selected_provider}[/red]")
            return {}
        
        # Let user select model
        console.print(f"\\n[bold]Available {selected_provider.title()} Models:[/bold]")
        model_table = Table()
        model_table.add_column("#", style="cyan", width=3)
        model_table.add_column("Model", style="green")
        model_table.add_column("Description", style="dim")
        model_table.add_column("Capabilities", style="yellow")
        
        for i, model in enumerate(models, 1):
            caps = ", ".join(model.capabilities[:3]) if model.capabilities else "N/A"
            model_table.add_row(
                str(i),
                model.display_name,
                model.description[:50] + "..." if len(model.description) > 50 else model.description,
                caps
            )
        
        console.print(model_table)
        
        while True:
            choice = Prompt.ask(f"Model choice [1-{len(models)}]", default="1")
            try:
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(models):
                        selected_model = models[idx]
                        break
            except:
                pass
            console.print("❌ Invalid choice, please try again")
        
        # Save configuration
        self.current_config.update({
            'default_provider': selected_provider,
            'default_model': selected_model.model_id
        })
        self._save_config()
        
        console.print(f"\\n✅ [green]Model configuration saved![/green]")
        console.print(f"🤖 Provider: {selected_provider.title()}")
        console.print(f"🧠 Model: {selected_model.display_name}")
        
        return {
            'provider': selected_provider,
            'model': selected_model.model_id,
            'display_name': selected_model.display_name
        }
    
    def _check_provider_availability(self) -> Dict[str, Dict[str, Any]]:
        """Check which providers are available/configured"""
        availability = {}
        
        # Check Anthropic
        try:
            client = env.Env.get().get_client('anthropic')
            availability['anthropic'] = {'available': True, 'client': client}
        except:
            availability['anthropic'] = {'available': False, 'error': 'API key not configured'}
        
        # Check OpenAI
        try:
            client = env.Env.get().get_client('openai')
            availability['openai'] = {'available': True, 'client': client}
        except:
            availability['openai'] = {'available': False, 'error': 'API key not configured'}
        
        # Check Ollama
        try:
            client = env.Env.get().get_client('ollama')
            availability['ollama'] = {'available': True, 'client': client}
        except:
            # Check if Ollama is running
            try:
                result = subprocess.run(['ollama', 'list'], 
                                      capture_output=True, timeout=2)
                if result.returncode == 0:
                    availability['ollama'] = {'available': True, 'client': None}
                else:
                    availability['ollama'] = {'available': False, 'error': 'Ollama not running'}
            except:
                availability['ollama'] = {'available': False, 'error': 'Ollama not installed'}
        
        # Check Gemini
        try:
            client = env.Env.get().get_client('gemini')
            availability['gemini'] = {'available': True, 'client': client}
        except:
            availability['gemini'] = {'available': False, 'error': 'API key not configured'}
        
        return {k: v for k, v in availability.items() if v['available']}
    
    def create_chat_function(self, provider: str = None, model: str = None) -> Callable:
        """Create a chat function using the specified or default model"""
        
        if not provider:
            provider = self.current_config['default_provider']
        if not model:
            model = self.current_config['default_model']
        
        # Return appropriate function based on provider
        if provider == 'anthropic':
            return lambda messages, **kwargs: anthropic.messages(
                messages=messages,
                model=model,
                max_tokens=kwargs.get('max_tokens', 3000),
                **{k: v for k, v in kwargs.items() if k != 'max_tokens'}
            )
        elif provider == 'openai':
            return lambda messages, **kwargs: openai.chat_completions(
                messages=messages,
                model=model,
                max_tokens=kwargs.get('max_tokens', 3000),
                **{k: v for k, v in kwargs.items() if k != 'max_tokens'}
            )
        elif provider == 'ollama':
            return lambda messages, **kwargs: ollama.chat(
                messages=messages,
                model=model,
                **kwargs
            )
        elif provider == 'gemini':
            return lambda messages, **kwargs: gemini.generate_content(
                messages=messages,
                model=model,
                **kwargs
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def get_current_config(self) -> Dict[str, str]:
        """Get current model configuration"""
        provider = self.current_config['default_provider']
        model_id = self.current_config['default_model']
        
        model_info = self.registry.get_model_info(provider, model_id)
        display_name = model_info.display_name if model_info else model_id
        
        return {
            'provider': provider,
            'model': model_id,
            'display_name': display_name
        }

# Global instance
model_manager = ModelManager()

def get_model_manager() -> ModelManager:
    """Get the global model manager instance"""
    return model_manager

def setup_models() -> Dict[str, str]:
    """Setup models interactively"""
    return model_manager.interactive_setup()

if __name__ == "__main__":
    # Demo the model system
    console.print("🤖 Testing xPyLLMent Model System")
    
    manager = ModelManager()
    config = manager.interactive_setup()
    
    if config:
        console.print("\\n🎉 Model system ready!")
        
        # Test creating a chat function
        chat_fn = manager.create_chat_function()
        console.print(f"✅ Chat function created for {config['display_name']}")