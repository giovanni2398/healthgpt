"""
Configuração do pytest para o projeto HealthGPT.
"""
import pytest

def pytest_addoption(parser):
    """Adiciona opções de linha de comando personalizadas."""
    parser.addoption(
        "--use-real-api",
        action="store_true",
        default=False,
        help="Habilita testes que usam APIs reais."
    )
    
@pytest.fixture(scope="session")
def use_real_api(request):
    """Fixture que indica se os testes devem usar APIs reais."""
    return request.config.getoption("--use-real-api") 