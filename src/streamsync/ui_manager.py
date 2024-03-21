from json import dumps as json_dumps
from typing import Dict, List, Optional

from streamsync.core_ui import (Component, UIError,
                                current_parent_container, current_component_tree, ComponentTree)


class StreamsyncUI:
    """Provides mechanisms to manage and manipulate UI components within a
    Streamsync session.

    This class offers context managers and methods to dynamically create, find,
    and organize UI components based on a structured component tree.
    """
    parent_types_map: Dict[str, List[str]]
    children_types_map: Dict[str, List[str]]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        ...

    @staticmethod
    def assert_in_container():
        container = current_parent_container.get(None)
        if container is None:
            raise UIError("A component can only be created inside a container")

    @property
    def component_tree(self) -> ComponentTree:
        """
        Returns the component tree representation

        :return:
        """
        return current_component_tree()

    @property
    def root(self) -> Component:
        tree = current_component_tree()
        root_component = tree.get_component('root')
        if not root_component:
            raise RuntimeError("Failed to acquire root component")
        return root_component

    @staticmethod
    def find(component_id: str) \
            -> Component:
        """
        Retrieves a component by its ID from the current session's component tree.

        This method searches for a component with the given ID within the
        application's UI structure. If the component is found, it is returned
        for further manipulation or inspection.

        :param component_id: The unique identifier of the component to find.
        :type component_id: str
        :return: The found component with the specified ID.
        :rtype: Component
        :raises RuntimeError: If no component with the specified ID is found
        in the current session's component tree.

        **Example**::

        >>> my_component = ui.find("my-component-id")
        >>> print(my_component.properties)
        """
        # Example context manager for finding components
        component = current_component_tree().get_component(component_id)
        if component is None:
            raise RuntimeError(f"Component {component_id} not found")
        return component

    @staticmethod
    def create_container_component(component_type: str, **kwargs) -> Component:
        component_tree = current_component_tree()
        container = _create_component(component_tree, component_type, **kwargs)
        component_tree.attach(container)
        return container

    @staticmethod
    def create_component(component_type: str, **kwargs) -> Component:
        component_tree = current_component_tree()
        component = _create_component(component_tree, component_type, **kwargs)
        component_tree.attach(component)

        return component


def _prepare_handlers(raw_handlers: Optional[dict]):
    handlers = {}
    if raw_handlers is not None:
        for event, handler in raw_handlers.items():
            if callable(handler):
                handlers[event] = handler.__name__
            else:
                handlers[event] = handler
    return handlers


def _prepare_binding(raw_binding):
    if raw_binding is not None:
        if len(raw_binding) == 1:
            binding = {
                "eventType": list(raw_binding.keys())[0],
                "stateRef": list(raw_binding.values())[0]
            }
            return binding
        elif len(raw_binding) != 0:
            raise RuntimeError('Improper binding configuration')


def _prepare_value(value):
    if isinstance(value, dict):
        return json_dumps(value)
    return str(value)


def _check_parent_child_relations(
        component_tree: ComponentTree,
        parent_id: str,
        component_type: str
):
    # Import required inside a function:
    # StreamsyncUIManager class stores actual type maps,
    # but importing it directly causes a circular import
    from streamsync.ui import StreamsyncUIManager

    if component_type == "root":
        raise UIError("Root component cannot be a child component.")

    parent = component_tree.get_component(parent_id)
    if not parent:
        raise RuntimeError(
            f"Improper parent_id provided: {parent_id} is missing in tree"
            )

    valid_children_types_for_parent = \
        StreamsyncUIManager.children_types_map.get(parent.type)

    while "inherit" in valid_children_types_for_parent:
        # Switch to grandparent allowed types in case of "inherit" instruction
        grandparent = component_tree.get_component(parent.parentId)
        valid_children_types_for_parent = \
            StreamsyncUIManager.children_types_map.get(grandparent.type)

    valid_parent_types_for_component = \
        StreamsyncUIManager.parent_types_map.get(component_type)

    if not valid_children_types_for_parent \
       or not valid_parent_types_for_component:
        type_to_blame = (f"Parent type '{parent.type}'"
                         if not valid_children_types_for_parent
                         else f"Child type '{component_type}'")
        raise RuntimeError(
            f"Misconfigured types: {type_to_blame} is not present " +
            "in allowed types map."
            )

    is_component_eligible = \
        (component_type in valid_children_types_for_parent
         or '*' in valid_children_types_for_parent)

    is_parent_eligible = \
        (parent.type in valid_parent_types_for_component
         or '*' in valid_parent_types_for_component)

    return is_component_eligible and is_parent_eligible


def _create_component(
        component_tree: ComponentTree,
        component_type: str,
        **kwargs
        ) -> Component:

    if kwargs.get("id", False) is None:
        kwargs.pop("id")

    if kwargs.get("position", False) is None:
        kwargs.pop("position")

    if kwargs.get("parentId", False) is None:
        kwargs.pop("parentId")

    if "parentId" in kwargs:
        parent_id: str = kwargs.pop("parentId")
    else:
        parent_container = current_parent_container.get(None)
        parent_id = "root" if not parent_container else parent_container.id

    is_component_a_valid_child = \
        _check_parent_child_relations(component_tree, parent_id, component_type)

    if not is_component_a_valid_child:
        raise UIError(f"Component type '{component_type}'" +
                      f"cannot be a child for component '{parent_id}'")

    # Converting all passed content values to strings
    raw_content: dict = kwargs.pop("content", {})
    content = {key: _prepare_value(value) for key, value in raw_content.items()}

    # A pre-defined ID is required for page components
    # to prevent page focus loss on app reload
    if component_type == "page" and "id" not in kwargs:
        identifier = f"cmc-page-{component_tree.page_counter + 1}"
        if "key" not in content:
            content["key"] = identifier
        if "id" not in kwargs:
            kwargs["id"] = identifier

    position: Optional[int] = kwargs.pop("position", None)
    is_positionless: bool = kwargs.pop("positionless", False)
    raw_handlers: dict = kwargs.pop("handlers", {})
    raw_binding: dict = kwargs.pop("binding", {})

    handlers = _prepare_handlers(raw_handlers) or None
    binding = _prepare_binding(raw_binding) or None

    component = Component(
        type=component_type,
        parentId=parent_id,
        isCodeManaged=True,
        content=content,
        handlers=handlers,
        binding=binding,
        **kwargs
        )

    # We're determining the position separately
    # due to that we need to know whether parent of the component
    # is present within base component tree
    # or a session-specific one
    component.position = \
        position if position is not None else \
        component_tree.determine_position(
            parent_id,
            is_positionless=is_positionless
            )

    return component
