import contextlib
from streamsync.core_ui import ComponentTree, UIError, use_component_tree
from streamsync.ui import StreamsyncUIManager
import streamsync as ss

import json

from tests.backend import test_app_dir

sc = None
with open(test_app_dir / "ui.json", "r") as f:
    sc = json.load(f).get("components")


@contextlib.contextmanager
def use_new_ss_session():
    session = ss.session_manager.get_new_session()
    session.session_component_tree.ingest(sc)
    yield session


@contextlib.contextmanager
def use_ui_manager():
    with use_new_ss_session() as session:
        with use_component_tree(session.session_component_tree):
            yield StreamsyncUIManager()


class TestComponentTree:

    ct = ComponentTree()

    def test_ingest(self) -> None:
        with use_new_ss_session() as session:
            d = session.session_component_tree.to_dict()
            assert d.get(
                "84378aea-b64c-49a3-9539-f854532279ee").get("type") == "header"

    def test_descendents(self) -> None:
        with use_new_ss_session() as session:
            desc = session.session_component_tree.get_descendents("root")
            desc_ids = list(map(lambda x: x.id, desc))
            assert "84378aea-b64c-49a3-9539-f854532279ee" in desc_ids
            assert "bb4d0e86-619e-4367-a180-be28ab6059f4" in desc_ids
            assert "85120b55-69c6-4b50-853a-bbbf73ff8121" in desc_ids


class TestUIManager:

    def test_find_component(self):
        with use_ui_manager() as ui:
            # Verify that the find method correctly retrieves a component by its ID
            expected_id = "84378aea-b64c-49a3-9539-f854532279ee"
            with ui.find(expected_id) as found_component:
                assert found_component is not None
                assert found_component.id == expected_id

    def test_find_component_no_context(self):
        with use_ui_manager() as ui:
            # Verify that the find method correctly retrieves a component by its ID
            expected_id = "84378aea-b64c-49a3-9539-f854532279ee"
            found_component = ui.find(expected_id)
            assert found_component is not None
            assert found_component.id == expected_id

    def test_assert_in_container_context(self):
        # Verify the context assertion for creating components within a container
        # First, successfully create a component within a container context
        with use_ui_manager() as ui:
            with ui.root:
                passed = False
                try:
                    ui.create_component('text', text='Inside container')
                    passed = True
                except Exception:
                    passed = False
                assert passed, "Component should be created within container context without errors"

            # Now, attempt to create a component outside of any container context, which should raise an error
            raised = False
            try:
                ui.create_component('text', text='Outside container')
            except UIError:
                raised = True
            assert raised, "Creating a component outside of a container context should raise an UIError"

    def test_column_container_creation(self):
        with use_ui_manager() as ui:
            with ui.ColumnContainer(id="test_container") as container:
                assert container.type == 'columns'
                assert container.id == "test_container"
                assert container in ui.component_tree.components.values()

    def test_column_container_creation_no_context(self):
        with use_ui_manager() as ui:
            container = ui.ColumnContainer(id="test_container")
            assert container.type == 'columns'
            assert container.id == "test_container"
            assert container in ui.component_tree.components.values()

    def test_column_container_creation_no_id(self):
        with use_ui_manager() as ui:
            with ui.ColumnContainer() as container:
                assert container.type == 'columns'
                assert container.id is not None
                assert container in ui.component_tree.components.values()
                assert container.id in ui.component_tree.components.keys()

    def test_column_creation(self):
        with use_ui_manager() as ui:
            with ui.Column(id="test_column") as column:
                assert column.type == 'column'
                assert column.id == "test_column"
                assert column in ui.component_tree.components.values()

    def test_text_creation(self):
        with use_ui_manager() as ui:
            with ui.Column(id="test_column") as column:
                text_content = "Hello World"
                text_component = ui.Text({"text": text_content}, id="test_text")
            assert text_component.type == 'text'
            assert text_component.content.get("text") == text_content
            assert text_component.id == "test_text"
            assert text_component.parentId == column.id
            assert text_component in ui.component_tree.components.values()
