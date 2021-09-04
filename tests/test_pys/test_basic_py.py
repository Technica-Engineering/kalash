from typing import List
from kalash.config import Config, Trigger, Test, dataclass, field
from kalash.run import run


@dataclass
class CustomConfig(Config):
    run_only_with: List[str] = field(default_factory=list)


t = Trigger(
    tests=[
        Test(
            path='./tests/test_scripts/python_instead_of_yaml'
        )
    ],
    config=CustomConfig(run_only_with=['cancombo'])
)

if __name__ == "__main__":
    run(t)
