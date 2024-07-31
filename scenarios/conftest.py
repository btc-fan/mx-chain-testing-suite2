import pytest
from multiversx_sdk.core.transactions_factories.transactions_factory_config import (
    TransactionsFactoryConfig,
)

from config.config import CHAIN_ID
from config.constants import CHAIN_SIMULATOR_FOLDER
from models.chain_simulator import ChainSimulator

config = TransactionsFactoryConfig(CHAIN_ID)


@pytest.fixture(scope="function")
def blockchain():
    chain_simulator = ChainSimulator(CHAIN_SIMULATOR_FOLDER)
    chain_simulator.start()
    yield chain_simulator
    chain_simulator.stop()


@pytest.fixture
def epoch(request):
    return request.param
