import json
import math
import unittest
import urllib
from typing import Dict

import altair
import numpy as np
import pandas as pd
import plotly.express as px
import polars as pl
import pyarrow as pa
import pytest
import writer as wf
from writer.core import (
    BytesWrapper,
    Evaluator,
    EventDeserialiser,
    FileWrapper,
    SessionManager,
    State,
    StateSerialiser,
    StateSerialiserException,
    WriterState,
)
from writer.core_ui import Component
from writer.ss_types import WriterEvent

from backend.fixtures import core_ui_fixtures
from tests.backend import test_app_dir

raw_state_dict = {
    "name": "Robert",
    "age": 1,
    "interests": ["lamps", "cars"],
    "state.with.dots": {
        "photo.jpeg": "Not available",
    },
    "features": {
        "eyes": "green",
        "height": "very short"
    },
    "best_feature": "eyes",
    "utfࠀ": 23,
    "counter": 4,
    "_private": 3,
    # Used as an example of something unserialisable yet pickable
    "_private_unserialisable": np.array([[1+2j, 2, 3+3j]])
}

simple_dict = {"items": {
        "Apple": {"name": "Apple", "type": "fruit"},
        "Cucumber": {"name": "Cucumber", "type": "vegetable"},
        "Lettuce": {"name": "Lettuce", "type": "vegetable"}
    }}

wf.Config.is_mail_enabled_for_log = True
wf.init_state(raw_state_dict)

sc = None
with open(test_app_dir / "ui.json", "r") as f:
    sc = json.load(f).get("components")
session = wf.session_manager.get_new_session()
session.session_component_tree.ingest(sc)


class TestStateProxy(unittest.TestCase):

    def setUp(self):
        self.sp = State(raw_state_dict)._state_proxy
        self.sp_simple_dict = State(simple_dict)._state_proxy

    @classmethod
    def count_initial_mutations(cls, d, count=0):
        """
        Counts the number of mutations that will be performed for a given dictionary
        when it is converted into a StateProxy.
        """
        for key, value in d.items():
            if not key.startswith('_'):
                count += 1  # Increment for each key-value pair
                if isinstance(value, dict):
                    count = TestStateProxy.count_initial_mutations(value, count)
                    # Recurse for nested dictionaries
        return count

    def test_read(self) -> None:
        d = self.sp.to_dict()
        assert d.get("name") == "Robert"
        assert d.get("age") == 1
        assert d.get("state.with.dots").get("photo.jpeg") == "Not available"
        assert d.get("utfࠀ") == 23

    def test_mutations(self) -> None:
        m = self.sp.get_mutations_as_dict()
        assert len(m) == TestStateProxy.count_initial_mutations(self.sp.to_dict())
        # Mutated after initialization from raw_state_dict

        self.sp["age"] = 2
        m = self.sp.get_mutations_as_dict()
        assert m.get("+age") == 2
        assert len(m) == 1

        self.sp["interests"] += ["dogs"]
        self.sp["features"]["height"] = "short"
        m = self.sp.get_mutations_as_dict()
        assert m.get("+interests") == ["lamps", "cars", "dogs"]
        assert m.get("+features.height") == "short"
        assert len(m) == 2

        self.sp["state.with.dots"]["photo.jpeg"] = "Corrupted"
        m = self.sp.get_mutations_as_dict()
        assert m.get("+state\\.with\\.dots.photo\\.jpeg") == "Corrupted"
        assert len(m) == 1

        d = self.sp.to_dict()
        assert d.get("age") == 2
        assert d.get("interests") == ["lamps", "cars", "dogs"]
        assert d.get("features").get("height") == "short"
        assert d.get("state.with.dots").get("photo.jpeg") == "Corrupted"


        del self.sp["best_feature"]
        m = self.sp.get_mutations_as_dict()
        assert "-best_feature" in m

    def test_apply_mutation_marker(self) -> None:
        self.sp.get_mutations_as_dict()
        self.sp_simple_dict.get_mutations_as_dict()

        # Apply the mutation to a specific key
        self.sp.apply_mutation_marker("age")
        m = self.sp.get_mutations_as_dict()
        assert m == {
            '+age': 1
        }

        # Apply the mutation to the state as a whole
        self.sp.apply_mutation_marker()
        m = self.sp.get_mutations_as_dict()
        assert m == {
            '+age': 1,
            '+best_feature': 'eyes',
            '+counter': 4,
            '+features': None,
            '+interests': ['lamps', 'cars'],
            '+name': 'Robert',
            '+state\\.with\\.dots': None,
            '+utfࠀ': 23
        }

        self.sp_simple_dict.apply_mutation_marker()
        m = self.sp_simple_dict.get_mutations_as_dict()
        assert m == {
            '+items': None
        }

        # Apply the mutation to the state as a whole and on all its children
        self.sp_simple_dict.apply_mutation_marker(recursive=True)
        m = self.sp_simple_dict.get_mutations_as_dict()
        assert m == {
            '+items': None,
            '+items.Apple': None,
            '+items.Apple.name': 'Apple',
            '+items.Apple.type': 'fruit',
            '+items.Cucumber': None,
            '+items.Cucumber.name': 'Cucumber',
            '+items.Cucumber.type': 'vegetable',
            '+items.Lettuce': None,
            '+items.Lettuce.name': 'Lettuce',
            '+items.Lettuce.type': 'vegetable'
        }


    def test_dictionary_removal(self) -> None:
        # Explicit removal test
        del self.sp_simple_dict["items"]["Lettuce"]
        m = self.sp_simple_dict.get_mutations_as_dict()
        assert "+items" in m
        assert "-items.Lettuce" in m


    def test_private_members(self) -> None:
        d = self.sp.to_dict()
        assert d.get("_private") is None
        assert d.get("_private_unserialisable") is None

    def test_to_raw_state(self) -> None:
        """
        Test that `to_raw_state` returns the state in its original format
        """
        assert self.sp.to_raw_state() == raw_state_dict
        assert self.sp_simple_dict.to_raw_state() == simple_dict



class TestState:

    def test_set_dictionary_in_a_state_should_transform_it_in_state_proxy_and_trigger_mutation(self):
        """
        Tests that writing a dictionary in a State without schema is transformed into a StateProxy and
        triggers mutations to update the interface

        #>>> _state = writer.init_state({'app': {}})
        #>>> _state["app"] = {"hello": "world"}
        """
        _state = State()

        # When
        _state["new.state.with.dots"] = {"test": "test"}

        m = _state._state_proxy.get_mutations_as_dict()
        assert m == {
            r"+new\.state\.with\.dots": None,
            r"+new\.state\.with\.dots.test": "test"
        }

    def test_set_dictionary_in_a_state_with_schema_should_transform_it_in_state_proxy_and_trigger_mutation(self):
        class SimpleSchema(State):
            app: dict

        _state = SimpleSchema()

        # When
        _state["app"] = {"hello": "world"}

        m = _state._state_proxy.get_mutations_as_dict()
        assert m == {
            r"+app": {"hello": "world"},
        }

    def test_replace_dictionary_content_in_a_state_with_schema_should_transform_it_in_state_proxy_and_trigger_mutation(self):
        """
        Tests that replacing a dictionary content in a State without schema trigger mutations on all the children.

        This processing must work after initialization and after recovering the mutations the first time.

        #>>> _state = State({'items': {}})
        #>>> _state["items"] = {k: v for k, v in _state["items"].items() if k != "Apple"}
        """
        _state = State({"items": {
            "Apple": {"name": "Apple", "type": "fruit"},
            "Cucumber": {"name": "Cucumber", "type": "vegetable"},
            "Lettuce": {"name": "Lettuce", "type": "vegetable"}
        }})

        m = _state._state_proxy.get_mutations_as_dict()
        assert m == {
            '+items': None,
            '+items.Apple': None,
            '+items.Apple.name': "Apple",
            '+items.Apple.type': "fruit",
            '+items.Cucumber': None,
            '+items.Cucumber.name': 'Cucumber',
            '+items.Cucumber.type': 'vegetable',
            '+items.Lettuce': None,
            '+items.Lettuce.name': 'Lettuce',
            '+items.Lettuce.type': 'vegetable'
        }

        # When
        items = _state['items']
        items = {k: v for k, v in items.items() if k != "Apple"}
        _state["items"] = items

        # Then
        m = _state._state_proxy.get_mutations_as_dict()
        assert m == {
            '+items': None,
            '+items.Cucumber': None,
            '+items.Cucumber.name': 'Cucumber',
            '+items.Cucumber.type': 'vegetable',
            '+items.Lettuce': None,
            '+items.Lettuce.name': 'Lettuce',
            '+items.Lettuce.type': 'vegetable'
        }

    def test_changing_a_value_in_substate_is_accessible_and_mutations_are_present(self):
        """
        Tests that the change of values in a child state is readable whatever the access mode and
        that mutations are triggered

        #>>> _state = ComplexSchema({'app': {'title': ''}})
        #>>> _state.app.title = 'world'
        """
        class AppState(State):
            title: str

        class ComplexSchema(State):
            app: AppState

        _state = ComplexSchema({'app': {'title': ''}})

        # When
        _state.app.title = 'world'

        # Then
        assert _state.app.title == 'world'
        assert _state['app']['title'] == 'world'
        assert _state.app['title'] == 'world'
        assert _state['app'].title == 'world'
        assert _state._state_proxy.get_mutations_as_dict() == {
            '+app': None,
            '+app.title': 'world',
        }

    def test_remove_then_replace_nested_dictionary_should_trigger_mutation(self):
        """
        Tests that deleting a key from a substate, then replacing it, triggers the expected mutations
        """
        # Assign
        _state = State({"nested": {"a": 1, "b": 2, "c": {"d": 3, "e": 4}}})
        m = _state._state_proxy.get_mutations_as_dict()

        # Acts
        del _state["nested"]["c"]["e"]
        _state['nested']['c'] = _state['nested']['c']

        # Assert
        m = _state._state_proxy.get_mutations_as_dict()
        assert m == {
            '+nested.c': None,
            '+nested.c.d': 3,
            '-nested.c.e': None
        }
        assert _state.to_dict() == {"nested": {"a": 1, "b": 2, "c": {"d": 3}}}


class TestWriterState:

    # Initialised manually

    base_s = WriterState(raw_state_dict)

    def test_dict_json_serialisable(self) -> None:
        json.dumps(self.base_s.user_state.to_dict())
        json.dumps(self.base_s.mail)

    def test_read(self) -> None:
        assert self.base_s["age"] == 1
        assert self.base_s["features"]["eyes"] == "green"
        assert "cars" in self.base_s["interests"]
        assert self.base_s["utfࠀ"] == 23

    def test_get_clone(self) -> None:
        cloned_s = self.base_s.get_clone()
        assert self.base_s.user_state.to_dict() == cloned_s.user_state.to_dict()
        assert self.base_s.mail == cloned_s.mail
        json.dumps(cloned_s.user_state.to_dict())
        json.dumps(cloned_s.mail)

    def test_get_new(self) -> None:

        # Initialised via clone of initial_state

        cloned_s = WriterState.get_new()
        cloned_s["age"] = 2
        cloned_s["features"]["height"] = "short"

        assert self.base_s["age"] == 1
        assert self.base_s["features"]["height"] == "very short"

        assert cloned_s["age"] == 2
        assert cloned_s["features"]["eyes"] == "green"
        assert cloned_s["features"]["height"] == "short"
        json.dumps(cloned_s.user_state.to_dict())
        json.dumps(cloned_s.mail)

    def test_mail(self) -> None:
        self.base_s.set_page("my_page_key")
        self.base_s.add_mail("my_own_mail", 2)

        assert self.base_s.mail[0] == {
            "type": "my_own_mail", "payload": 2}
        assert self.base_s.mail[1] == {
            "type": "pageChange", "payload": "my_page_key"}

        self.base_s.clear_mail()
        assert len(self.base_s.mail) == 0
        json.dumps(self.base_s.user_state.to_dict())
        json.dumps(self.base_s.mail)

    def test_non_str_keys(self) -> None:
        d = {
            ("tuple", "key"): "Invalid"
        }
        with pytest.raises(ValueError):
            WriterState(d)

    def test_unpickable_members(self) -> None:
        bad_base_s = WriterState({
            "unpickable_thing": json,
        })
        assert bad_base_s.mail == []

        # A substitute state with an error message should be provided

        cloned = bad_base_s.get_clone()
        assert cloned.user_state.to_dict() == {}
        assert cloned.mail[0].get("type") == "logEntry"
        assert cloned.mail[0].get("payload").get("type") == "error"
        json.dumps(cloned.user_state.to_dict())
        json.dumps(cloned.mail)


class TestEventDeserialiser:

    root_instance_path = [{"componentId": "root", "instanceNumber": 0}]
    session_state = WriterState(raw_state_dict)
    component_tree = session.session_component_tree
    ed = EventDeserialiser(session_state, component_tree)

    def test_unknown_no_payload(self) -> None:
        ev = WriterEvent(
            type="not-a-known-event",
            instancePath=self.root_instance_path,
            payload=None
        )
        self.ed.transform(ev)
        assert ev.type == "not-a-known-event"

    def test_unknown_with_payload(self) -> None:
        ev = WriterEvent(
            type="not-a-known-event",
            instancePath=self.root_instance_path,
            payload={"has_payload": "yes"}
        )
        assert ev.type == "not-a-known-event"

    def test_unknown_native_with_payload(self) -> None:
        ev = WriterEvent(
            type="wf-not-a-known-event",
            instancePath=self.root_instance_path,
            payload={"has_payload": "yes"}
        )
        assert ev.type == "wf-not-a-known-event"
        with pytest.raises(ValueError):
            self.ed.transform(ev)

    def test_number_change(self) -> None:
        ev = WriterEvent(
            type="wf-number-change",
            instancePath=self.root_instance_path,
            payload="44"
        )
        self.ed.transform(ev)
        assert ev.payload == 44

    def test_change(self) -> None:
        ev = WriterEvent(
            type="wf-change",
            instancePath=self.root_instance_path,
            payload="44 !@"
        )
        self.ed.transform(ev)
        assert ev.payload == "44 !@"

    def test_option_change_default(self) -> None:
        instance_path = [
            {"componentId": "root", "instanceNumber": 0},
            {"componentId": "7730df5b-8731-4123-bacc-898e7347b124", "instanceNumber": 0},
            {"componentId": "6010765e-9ac3-4570-84bf-913ae404e03a", "instanceNumber": 0},
            {"componentId": "d2269aeb-c84e-4075-8679-c6f168fecfac", "instanceNumber": 0}
        ]

        ev_valid = WriterEvent(
            type="wf-option-change",
            instancePath=instance_path,
            payload="a"
        )

        self.ed.transform(ev_valid)
        assert ev_valid.payload == "a"

        ev_invalid = WriterEvent(
            type="wf-option-change",
            instancePath=instance_path,
            payload="d"
        )

        with pytest.raises(RuntimeError):
            self.ed.transform(ev_invalid)

    def test_option_change(self) -> None:
        instance_path = [
            {"componentId": "root", "instanceNumber": 0},
            {"componentId": "7730df5b-8731-4123-bacc-898e7347b124", "instanceNumber": 0},
            {"componentId": "6010765e-9ac3-4570-84bf-913ae404e03a", "instanceNumber": 0},
            {"componentId": "9b09d964-da68-4d47-851a-31f070ae1f2f", "instanceNumber": 0}
        ]

        ev_valid = WriterEvent(
            type="wf-option-change",
            instancePath=instance_path,
            payload="sp"
        )

        self.ed.transform(ev_valid)
        assert ev_valid.payload == "sp"

        ev_invalid = WriterEvent(
            type="wf-option-change",
            instancePath=instance_path,
            payload="dk"
        )

        with pytest.raises(RuntimeError):
            self.ed.transform(ev_invalid)

    def test_options_change_default(self) -> None:
        instance_path = [
            {"componentId": "root", "instanceNumber": 0},
            {"componentId": "7730df5b-8731-4123-bacc-898e7347b124", "instanceNumber": 0},
            {"componentId": "6010765e-9ac3-4570-84bf-913ae404e03a", "instanceNumber": 0},
            {"componentId": "784288ff-80ec-4170-a3de-53e461ca1640", "instanceNumber": 0}
        ]

        ev_valid = WriterEvent(
            type="wf-options-change",
            instancePath=instance_path,
            payload=["a", "b"]
        )

        self.ed.transform(ev_valid)
        assert ev_valid.payload == ["a", "b"]

        ev_invalid = WriterEvent(
            type="wf-options-change",
            instancePath=instance_path,
            payload=["a", "d"]
        )

        with pytest.raises(RuntimeError):
            self.ed.transform(ev_invalid)

    def test_hashchange(self) -> None:
        ev = WriterEvent(
            type="wf-hashchange",
            instancePath=self.root_instance_path,
            payload={
                "pageKey": "myPage",
                "routeVars": {
                    "param": "1"
                },
                "virus": "yes"
            }
        )
        self.ed.transform(ev)
        assert ev.payload == {
            "page_key": "myPage",
            "route_vars": {
                "param": "1"
            },
        }

    def test_webcam(self) -> None:
        ev = WriterEvent(
            type="wf-webcam",
            instancePath=self.root_instance_path,
            payload="data:text/plain;base64,aGVsbG8gd29ybGQ="
        )
        self.ed.transform(ev)
        assert bytes(ev.payload).decode("utf-8") == "hello world"

    def test_file_change(self) -> None:
        ev = WriterEvent(
            type="wf-file-change",
            instancePath=self.root_instance_path,
            payload=[{
                "name": "myfile.txt",
                "type": "text/plain",
                "data": "data:text/plain;base64,aGVsbG8gd29ybGQ="
            }]
        )
        self.ed.transform(ev)
        assert ev.payload[0].get("name") == "myfile.txt"
        assert ev.payload[0].get("type") == "text/plain"
        assert bytes(ev.payload[0].get("data")).decode(
            "utf-8") == "hello world"

    def test_date_change(self) -> None:
        ev_invalid = WriterEvent(
            type="wf-date-change",
            instancePath=self.root_instance_path,
            payload="virus"
        )
        with pytest.raises(RuntimeError):
            self.ed.transform(ev_invalid)

        ev_valid = WriterEvent(
            type="wf-date-change",
            instancePath=self.root_instance_path,
            payload="2019-11-23"
        )
        self.ed.transform(ev_valid)
        assert ev_valid.payload == "2019-11-23"

    def test_time_change(self) -> None:
        ev_invalid = WriterEvent(
            type="wf-time-change",
            instancePath=self.root_instance_path,
            payload="virus"
        )
        with pytest.raises(RuntimeError):
            self.ed.transform(ev_invalid)

        ev_valid = WriterEvent(
            type="wf-time-change",
            instancePath=self.root_instance_path,
            payload="23:59"
        )
        self.ed.transform(ev_valid)
        assert ev_valid.payload == "23:59"


class TestFileWrapper():

    file_path = str(test_app_dir / "assets/myfile.csv")

    def test_get_as_dataurl(self) -> None:
        fw = FileWrapper(self.file_path, "text/plain")
        assert fw.get_as_dataurl() == "data:text/plain;base64,aGVsbG8gd29ybGQ="


class TestBytesWrapper():

    def test_get_as_dataurl(self) -> None:
        bw = BytesWrapper("hello world".encode("utf-8"), "text/plain")
        assert bw.get_as_dataurl() == "data:text/plain;base64,aGVsbG8gd29ybGQ="


class TestStateSerialiser():

    sts = StateSerialiser()
    file_path = str(test_app_dir / "assets/myfile.csv")
    df_path = str(test_app_dir / "assets/main_df.csv")

    def test_nested_dict(self) -> None:
        d = {
            "features": {
                "eyes": "green"
            }
        }
        s = self.sts.serialise(d)
        assert s.get("features").get("eyes") == "green"

    def test_non_str_keys_in_dict(self) -> None:
        d = {
            ("tuple", "key"): "Invalid"
        }
        s = self.sts.serialise(d)
        assert s.get("('tuple', 'key')") is not None

    def test_bytes(self) -> None:
        d = {
            "name": "Normal name",
            "data": "hello world".encode("utf-8")
        }
        s = self.sts.serialise(d)

        # Note absence of MIME type

        assert s.get("data") == "data:;base64,aGVsbG8gd29ybGQ="

    def test_wrappers(self) -> None:
        fw = FileWrapper(self.file_path, "text/plain")
        bw = BytesWrapper("hello world".encode("utf-8"), "text/plain")
        d = {
            "datafw": fw,
            "databw": bw
        }
        s = self.sts.serialise(d)
        assert s.get("datafw") == s.get("databw")
        assert s.get("databw") == "data:text/plain;base64,aGVsbG8gd29ybGQ="

    def test_numbers(self) -> None:
        d = {
            "name": "Normal name",
            "pet_count": 2,
            "fav_number": math.nan,
            "likes_coffee": True,
            "likes_black_tea": False
        }
        s = self.sts.serialise(d)
        assert s.get("name") == "Normal name"
        assert s.get("pet_count") == 2
        assert s.get("fav_number") is None  # NaN is serialised as None
        assert s.get("likes_coffee") == True
        assert s.get("likes_black_tea") == False

    def test_invalid(self) -> None:

        # A Python module is used as an example of a non-serialisable object

        d = {
            "fav_module": wf
        }

        with pytest.raises(StateSerialiserException):
            self.sts.serialise(d)

    def test_numpy_array_and_int(self) -> None:
        d = {
            "counter": 0,
            "np_a": np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
        }
        s = self.sts.serialise(d)
        assert s.get("np_a")[0][1] == 2
        json.dumps(s)

    def test_numpy_array_with_complex(self) -> None:
        d = {
            "counter": 0,
            "np_a": np.array([[1, 2, 3+3j], [4, 5, 6], [7, 8, 9]]),
        }
        with pytest.raises(StateSerialiserException):
            self.sts.serialise(d)

    def test_nans_in_dataframe(self) -> None:
        data = {
            "column_a": [1, 2, np.nan, 4],
            "column_b": [5, np.nan, 7, 8],
        }
        d = {
            "name": "Normal name",
            "df": pd.DataFrame(data)
        }
        self.sts.serialise(d)

    def test_unserialisable_altair(self) -> None:
        chart = altair.Chart([3, 3, 3]).mark_line().encode(
            x='x',
            y='y'
        )
        d = {
            "chart": chart
        }
        with pytest.warns(UserWarning):
            with pytest.raises(ValueError):
                self.sts.serialise(d)
                
    def test_plotly_should_be_serialize_to_json(self) -> None:
        """
        Test that plotly figure should be serialised to json string directly. Serializing the json directly allows you 
        to display datasets that exceed 10,000 records. 
        
        With the default json serializer, a dataset like this blows up memory. Plotly is using internaly orjson as serializer.
        """
        # Arrange
        df = px.data.iris()
        fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species", symbol="species")
        
        # Acts
        json_code = self.sts.serialise(fig)

        # Assert
        assert isinstance(json_code, str)
        o = json.loads(json_code)
        assert 'data' in o
        assert 'layout' in o

    def test_pandas_df(self) -> None:
        d = {
            "name": "Normal name",
            "df": pd.read_csv(self.df_path)
        }
        s = self.sts.serialise(d)
        assert s.get("name") == "Normal name"
        df_durl = s.get("df")
        df_buffer = urllib.request.urlopen(df_durl)
        reader = pa.ipc.open_file(df_buffer)
        table = reader.read_all()
        assert table.column("name")[0].as_py() == "Byte"
        assert table.column("length_cm")[2].as_py() == 32

    def test_polars_df(self) -> None:
        d = {
            "name": "Normal name",
            "df": pl.read_csv(self.df_path)
        }
        s = self.sts.serialise(d)
        assert s.get("name") == "Normal name"
        df_durl = s.get("df")
        df_buffer = urllib.request.urlopen(df_durl)
        reader = pa.ipc.open_file(df_buffer)
        table = reader.read_all()
        assert table.column("name")[0].as_py() == "Byte"
        assert table.column("length_cm")[2].as_py() == 32

class TestEvaluator:

    def test_evaluate_field_simple(self) -> None:

        instance_path = [
            {"componentId": "root", "instanceNumber": 0},
            {"componentId": "4b6f14b0-b2d9-43e7-8aba-8d3e939c1f83", "instanceNumber": 0},
            {"componentId": "0cd59329-29c8-4887-beee-39794065221e", "instanceNumber": 0}

        ]
        st = WriterState({
            "counter": 8
        })
        ct = session.session_component_tree
        e = Evaluator(st, ct)
        evaluated = e.evaluate_field(instance_path, "text")
        assert evaluated == "The counter is 8"

    def test_evaluate_field_repeater(self) -> None:
        instance_path_base = [
            {"componentId": "root", "instanceNumber": 0},
            {"componentId": "4b6f14b0-b2d9-43e7-8aba-8d3e939c1f83", "instanceNumber": 0},
            {"componentId": "f811ca14-8915-443d-8dd3-77ae69fb80f4", "instanceNumber": 0}
        ]
        instance_path_0 = instance_path_base + [
            {"componentId": "2e688107-f865-419b-a07b-95103197e3fd", "instanceNumber": 0}
        ]
        instance_path_2 = instance_path_base + [
            {"componentId": "2e688107-f865-419b-a07b-95103197e3fd", "instanceNumber": 2}
        ]
        st = WriterState({
            "prog_languages": {
                "c": "C",
                "py": "Python",
                "js": "JavaScript",
                "ts": "TypeScript"
            }
        })
        ct = session.session_component_tree
        e = Evaluator(st, ct)
        assert e.evaluate_field(
            instance_path_0, "text") == "The id is c and the name is C"
        assert e.evaluate_field(
            instance_path_2, "text") == "The id is js and the name is JavaScript"

    def test_set_state(self) -> None:
        instance_path = [
            {"componentId": "root", "instanceNumber": 0}
        ]
        st = WriterState(raw_state_dict)
        ct = session.session_component_tree
        e = Evaluator(st, ct)
        e.set_state("name", instance_path, "Roger")
        e.set_state("dynamic_prop", instance_path, "height")
        e.set_state("features[dynamic_prop]", instance_path, "toddler height")
        e.set_state("features.new_feature", instance_path, "blue")
        assert st["name"] == "Roger"
        assert st["features"]["height"] == "toddler height"
        assert st["features"]["new_feature"] == "blue"

    def test_evaluate_expression(self) -> None:
        instance_path = [
            {"componentId": "root", "instanceNumber": 0}
        ]
        st = WriterState(raw_state_dict)
        ct = session.session_component_tree
        e = Evaluator(st, ct)
        assert e.evaluate_expression("features.eyes", instance_path) == "green"
        assert e.evaluate_expression("best_feature", instance_path) == "eyes"
        assert e.evaluate_expression("features[best_feature]", instance_path) == "green"

    def test_get_context_data_should_return_the_target_of_event(self) -> None:
        """
        Test that the target of the event is correctly returned by the get_context_data method

        Here we reproduce a click on a button
        """
        # Given
        st = WriterState({})
        ct = core_ui_fixtures.build_fake_component_tree([
            Component(id="button1", parentId="root", type="button")
        ], init_root=True)

        e = Evaluator(st, ct)

        # When
        context = e.get_context_data([
            {"componentId": "root", "instanceNumber": 0},
            {"componentId": "button1", "instanceNumber": 0}
        ])

        # Then
        assert context.get("target") == "button1"

    def test_get_context_data_should_return_the_repeater_position_and_the_target_inside_the_repeater(self) -> None:
        """
        Test that the repeater position and target of the event is correctly returned by the get_context_data method

        Here we reproduce a click on a button
        """
        # Given
        st = WriterState({})
        ct = core_ui_fixtures.build_fake_component_tree([
            Component(id="repeater1", parentId="root", type="repeater", content={'keyVariable': 'item', 'valueVariable': 'value', 'repeaterObject': json.dumps({'a': 'A', 'b': 'B'})}),
            Component(id="button1", parentId="repeater1", type="button")
        ], init_root=True)

        e = Evaluator(st, ct)

        # When
        context = e.get_context_data([
            {"componentId": "root", "instanceNumber": 0},
            {"componentId": "repeater1", "instanceNumber": 0},
            {"componentId": "button1", "instanceNumber": 1}
        ])

        # Then
        assert context.get("target") == "button1"
        assert context.get("item") == "b"
        assert context.get("value") == "B"


class TestSessionManager:

    sm = SessionManager()
    proposed_session_id = "c13a280fe17ec663047ec14de15cd93ad686fecf5f9a4dbf262d3a86de8cb577"

    def test_get_new_session_proposed(self) -> None:
        self.sm.get_new_session(
            {"testCookie": "yes"},
            {"origin": "example.com"},
            self.proposed_session_id
        )
        self.sm.get_session(self.proposed_session_id)
        s = self.sm.get_session(self.proposed_session_id)
        assert s.cookies == {"testCookie": "yes"}
        assert s.headers == {"origin": "example.com"}
        assert s.session_id == self.proposed_session_id
        assert self.sm.get_session(self.proposed_session_id) == s

    def test_get_new_session_generate_id(self) -> None:
        s = self.sm.get_new_session(
            {"testCookie": "yes"},
            {"origin": "example.com"},
            None
        )
        assert s.cookies == {"testCookie": "yes"}
        assert s.headers == {"origin": "example.com"}
        assert s.session_id is not None
        assert self.sm.get_session(s.session_id) == s

    def test_close_session(self) -> None:
        s = self.sm.get_new_session(
            {"testCookie": "yes"},
            {"origin": "example.com"},
            None
        )
        self.sm.close_session(s.session_id)
        assert self.sm.get_session(s.session_id) is None

    def test_session_timeout(self) -> None:
        s = self.sm.get_new_session(
            {"testCookie": "yes"},
            {"origin": "example.com"},
            None
        )
        self.sm.prune_sessions()
        assert self.sm.get_session(s.session_id) is not None
        EXCESS_IDLE_SECONDS = 600
        s.last_active_timestamp -= (
            SessionManager.IDLE_SESSION_MAX_SECONDS + EXCESS_IDLE_SECONDS)
        self.sm.prune_sessions()
        assert self.sm.get_session(s.session_id) is None

    def test_session_verifiers(self) -> None:
        def session_verifier_1(cookies: Dict[str, str]):
            if cookies != {"testCookie": "yes"}:
                return False
            return True

        def session_verifier_2(headers: Dict[str, str]) -> None:
            if headers != {"origin": "example.com"}:
                return False
            return True

        self.sm.add_verifier(session_verifier_1)
        self.sm.add_verifier(session_verifier_2)
        s_valid = self.sm.get_new_session(
            {"testCookie": "yes"},
            {"origin": "example.com"},
            None
        )
        assert s_valid is not None
        s_invalid = self.sm.get_new_session(
            {"testCookie": "no"},
            {"origin": "example.com"},
            None
        )
        s_invalid = self.sm.get_new_session(
            {"testCookie": "yes"},
            {"origin": "example"},
            None
        )
        assert s_invalid is None
