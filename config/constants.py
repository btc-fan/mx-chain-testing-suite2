import os

# Chain Simulator Environment variable or default path
chain_simulator_build_path = os.getenv("CHAIN_SIMULATOR_BUILD_PATH")
if chain_simulator_build_path:
    chain_simulator_build_path = os.path.expanduser(chain_simulator_build_path)

if (
    chain_simulator_build_path
    and os.path.exists(chain_simulator_build_path)
    and os.listdir(chain_simulator_build_path)
):
    CHAIN_SIMULATOR_FOLDER = chain_simulator_build_path
else:
    # Fallback to another specific path
    specific_path = os.path.expanduser(
        "~/multiversX/mx-chain-simulator-go/cmd/chainsimulator"
    )
    if os.path.exists(specific_path) and os.listdir(specific_path):
        CHAIN_SIMULATOR_FOLDER = specific_path
    else:
        raise ValueError(
            "Both CHAIN_SIMULATOR_BUILD_PATH and the fallback path are invalid or empty"
        )

# Project Paths
PROJECT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WALLETS_FOLDER = os.path.join(PROJECT_FOLDER, "data", "wallets")
VALIDATOR_KEYS_FOLDER = os.path.join(PROJECT_FOLDER, "data", "validator_keys")
# contracts
VALIDATOR_CONTRACT = "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
SYSTEM_DELEGATION_MANAGER_CONTRACT = (
    "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqylllslmq6y6"
)
STAKING_CONTRACT = "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqllls0lczs7"
ESDT_CONTRACT = "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
GAS_PRICE = 1000000000

# timing
WAIT_UNTIL_API_REQUEST_IN_SEC = 0.5

# chain
MAX_NUM_OF_BLOCKS_UNTIL_TX_SHOULD_BE_EXECUTED = 20

# staking_v4
EPOCH_WITH_STAKING_V3_5 = 3
EPOCH_STAKING_QUEUE_BECOMES_AUCTION_LIST = 4
EPOCH_SHUFFLING_FROM_ELIGIBLE_TO_AUCTION_LIST = 5
EPOCH_STAKING_V4_FULLY_FUNCTIONAL = 6
