from pathlib import Path

from aicoding.relevant_user_flows import load_relevant_user_flow_inventory


REPO_ROOT = Path(__file__).resolve().parents[2]
INVENTORY_PATH = (
    REPO_ROOT / "notes" / "catalogs" / "traceability" / "relevant_user_flow_inventory.yaml"
)


def test_relevant_user_flow_inventory_loads_and_has_expected_identity() -> None:
    inventory = load_relevant_user_flow_inventory(INVENTORY_PATH)

    assert inventory.schema_version == 1
    assert inventory.inventory_id == "relevant_user_flow_inventory"
    assert len(inventory.flows) == 13


def test_relevant_user_flow_inventory_tracks_all_canonical_flow_docs() -> None:
    inventory = load_relevant_user_flow_inventory(INVENTORY_PATH)
    flow_docs = sorted(path.name for path in (REPO_ROOT / "flows").glob("*.md") if path.name != "README.md")

    assert sorted(Path(flow.canonical_md).name for flow in inventory.flows) == flow_docs


def test_relevant_user_flow_inventory_entries_link_to_real_paths_and_commands() -> None:
    inventory = load_relevant_user_flow_inventory(INVENTORY_PATH)

    for flow in inventory.flows:
        assert (REPO_ROOT / flow.canonical_md).is_file()
        assert (REPO_ROOT / flow.proof.primary_e2e_target).is_file()
        assert flow.scope.user_documentation in {"affected", "not_applicable"}
        assert isinstance(flow.documentation.required, bool)
        for surface in flow.documentation.surfaces:
            assert (REPO_ROOT / surface).is_file()
        for note_path in flow.relevance.discovered_from + flow.related_notes:
            assert (REPO_ROOT / note_path).is_file()
        for command_group in (
            flow.canonical_commands.bounded,
            flow.canonical_commands.e2e,
            flow.canonical_commands.docs,
        ):
            assert all("pytest" in command for command in command_group)


def test_relevant_user_flow_inventory_declares_interpretation_boundary() -> None:
    inventory = load_relevant_user_flow_inventory(INVENTORY_PATH)

    assert any(
        "flows/*.md remain the canonical narrative runtime flow contracts" in rule
        for rule in inventory.interpretation_rules
    )
    assert any(
        "bounded proof status and real E2E completion must remain distinct" in rule
        for rule in inventory.interpretation_rules
    )


def test_relevant_user_flow_inventory_records_documentation_linkage() -> None:
    inventory = load_relevant_user_flow_inventory(INVENTORY_PATH)

    for flow in inventory.flows:
        assert flow.scope.user_documentation == "affected"
        assert flow.documentation.required is True
        assert "docs/README.md" in flow.documentation.surfaces
