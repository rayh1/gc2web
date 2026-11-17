from adapter.gedq_adapter import (
    build_families,
    build_individuals,
    build_repositories,
    build_sources,
    load_dataset,
)
from model.Family import Family
from model.Individual import Individual
from model.Repository import Repository
from model.Source import Source
from tqdm import tqdm  # type: ignore
from util.singleton import singleton


@singleton
class GedcomModel:
    def __init__(self):
        self.__individual_map: dict[str, Individual] = {}
        self.__family_map: dict[str, Family] = {}
        self.__source_map: dict[str, Source] = {}
        self.__repository_map: dict[str, Repository] = {}

    def __exclude_privates(self):
        """Exclude private individuals from the GedcomModel"""
        for individual in tqdm(
            list(filter(lambda i: i.is_private(), self.individuals)),
            desc="Excluded private individuals",
            bar_format="{desc}: {total_fmt}",
        ):
            del self.__individual_map[individual.xref_id]

    def get_individual(self, id: str) -> Individual | None:
        return self.__individual_map.get(id, None)

    def get_family(self, id: str) -> Family | None:
        return self.__family_map.get(id, None)

    def get_source(self, xref_id: str) -> Source | None:
        return self.__source_map.get(xref_id, None)

    def get_repository(self, id: str) -> Repository | None:
        return self.__repository_map.get(id, None)

    @property
    def individuals(self) -> list[Individual]:
        return list(self.__individual_map.values())

    @property
    def families(self) -> list[Family]:
        return list(self.__family_map.values())

    @property
    def sources(self) -> list[Source]:
        return list(self.__source_map.values())

    @property
    def repositories(self) -> list[Repository]:
        return list(self.__repository_map.values())

    def clear(self):
        self.__individual_map = {}
        self.__family_map = {}
        self.__source_map = {}
        self.__repository_map = {}

    def parse_file(self, gedcom_file: str):
        try:
            dataset = load_dataset(gedcom_file)
        except RuntimeError as exc:
            raise SystemExit(str(exc)) from exc

        self.clear()
        self.__source_map = build_sources(dataset.sources)
        self.__repository_map = build_repositories(dataset.repositories)
        self.__individual_map = build_individuals(dataset.individuals, dataset.sources)
        self.__family_map = build_families(dataset.families)
        self.__exclude_privates()
