import contextlib
from typing import Optional

import streamsync.core
from streamsync.core import StreamsyncState, State

@contextlib.contextmanager
def use_dedicated_streamsync_initial_state():
    """

    Returns
    -------

    """
    previous_state = streamsync.core.initial_state
    yield
    streamsync.core.initial_state = previous_state

def test_init_state_should_build_simple_streamsync_state_without_schema():
    """
    Tests that `streamsync.init_state` without schema returns a StreamsyncState object.
    """
    with use_dedicated_streamsync_initial_state():
        # When
        state = streamsync.init_state({})

        # Then
        assert isinstance(state, StreamsyncState)


def test_init_state_with_schema_should_inherits_streamsync_state():
    """
    Tests that `streamsync.init_state` with schema returns a StreamsyncState object.
    """
    class SimpleSchema(StreamsyncState):
        value: int
        message: Optional[str]

    with use_dedicated_streamsync_initial_state():
        # When
        state = streamsync.init_state({'value': 1, 'message': None, 'hello': 2}, schema=SimpleSchema)

        # Then
        assert isinstance(state, SimpleSchema)
        assert state.value == 1
        assert state.message is None
        assert state['hello'] == 2


def test_init_state_should_build_a_state_with_a_schema_that_contains_a_substate():
    """
    Tests that `streamsync.init_state` constructs an instance with schema that contains a substate.
    """
    class AppState(State):
        title: str

    class ComplexSchema(StreamsyncState):
        app: AppState
        value: int
        message: Optional[str]

    with use_dedicated_streamsync_initial_state():
        # When
        state = streamsync.init_state({'app': {'title': 'hello'}, 'value': 1, 'message': None, 'hello': 2}, schema=ComplexSchema)

        # Then
        assert isinstance(state, ComplexSchema)
        assert isinstance(state.app, AppState)
        assert state.app.title == 'hello'
        assert state['hello'] == 2

        # A State Proxy instance is directly linked to the State Proxy instance of a child state
        assert state._state_proxy.state['app'] is state.app._state_proxy





def test_init_state_with_state_accept_raw_values_that_deviates_from_the_expected_type():
    """
    Tests that `streamsync.init_state` with schema accepts in raw state values that deviate from the expected type.
    """
    class AppState(State):
        year: int

    class ComplexSchema(StreamsyncState):
        app: AppState
        value: int
        message: Optional[str]

    with use_dedicated_streamsync_initial_state():
        # When
        state = streamsync.init_state({'app': {'year': 'hello'}, 'value': 1, 'message': None, 'hello': 2}, schema=ComplexSchema)

        # Then
        assert isinstance(state, ComplexSchema)
        assert state.value == 1
        assert state.app.year == 'hello'
        assert state.message is None
        assert state['hello'] == 2