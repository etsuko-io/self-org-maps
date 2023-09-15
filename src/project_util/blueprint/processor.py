from abc import ABC
from pathlib import Path

from src.project_util.blueprint.blueprint import Blueprint
from src.project_util.naming.naming import NamingUtil
from src.project_util.project.project import Project


class BlueprintProcessor(ABC):
    def __init__(
        self, name, module=None, parent_level=0, suffix_fn=NamingUtil.format_now
    ):
        # todo: explain what this does and why? what is module>
        parent_dir = Path(module).parents[parent_level] if module else Path()

        name = f"{name}-{suffix_fn()}" if suffix_fn else name

        self.project = Project(
            name=name,
            parent_dir=parent_dir,
        )

    def process(self, blueprint: Blueprint):
        raise NotImplementedError
