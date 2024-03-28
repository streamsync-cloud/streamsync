import streamsync as ss
import pandas as pd
import numpy as np
import plotly.express as px
import statistics
import logging
import streamsync.core
import altair as alt
import asyncio


@ss.session_verifier
def check_headers(headers):
    if headers.get("x-fail") is not None:
        return False
    return True


@ss.session_verifier
def check_cookies(cookies):
    if cookies.get("fail_cookie") is not None:
        return False
    return True

def update_cities(state, payload):
    if payload == "ar":
        state["cities"] = {
            "ba": "Buenos Aires",
            "cb": "Cordoba"
        }
    elif payload == "uk":
        state["cities"] = {
            "ln": "London",
            "br": "Bristol"
        }

logging.info("VERIFIERS")
logging.info(streamsync.core.session_manager.verifiers)


my_var = 3

def increment(state):
    state["counter"] += 1*my_var

# EVENT HANDLERS

def file_change_handler(state, payload):
    uploaded_files = payload
    for i, uploaded_file in enumerate(uploaded_files):
        name = uploaded_file.get("name")
        file_data = uploaded_file.get("data")
        with open(f"{name}-{i}.jpeg", "wb") as file_handle:
            file_handle.write(file_data)

def handle_timer_tick(state):
    state["counter"] += 1


def handle_file_download(state):
    data = ss.pack_file("assets/story.txt", "text/plain")
    file_name = "thestory.txt"
    state.file_download(data, file_name)

def add_notification(state):
    state.add_notification("error", "An Error", "Something bad happened.")
    state.add_notification("warning", "A Warning", "Be aware that something happened.")
    state.add_notification("info", "Some Info", "Something happened.")
    state.add_notification("success", "A Success", "Something good happened.")

def bad_event_handler(state):
    state["prog_languages"][1/0] = "bad"

def payload_inspector(state, payload, context):
    state["inspected_payload"] = repr(payload)
    print("Payload: " + repr(payload))
    print("Context: " + repr(context))


def handle_webcam(state, payload):
    state["webcam_image"] = ss.pack_bytes(payload, "image/png")


def handle_form_submit(state):
    if state["b"]["pet_count"] <= 0:
        state["b"]["message"] = "-You must have pets"
        return
    state["b"] = {
        "pet_count": 0
    }
    state["b"]["message"] = "+You have pets"


def handle_add_to_list(state, context):
    state["order_list"] += [context["itemId"]]


async def test_async_handler(state):
    await asyncio.sleep(3)
    state["counter"] += 1*my_var

# Filters data and triggers updates.


def update(state, session):
    main_df = _get_main_df()
    main_df = main_df[main_df['length_cm'] >= state["filter"]["min_length"]]
    main_df = main_df[main_df['weight_g'] >= state["filter"]["min_weight"]]
    state["main_df"] = main_df
    state["session"] = session
    _update_metrics(state)
    _update_role_chart(state)
    _update_scatter_chart(state)


def test_context(state, session, context):
    state["highlighted_context"] = repr(context)

# LOAD / GENERATE DATA


def _generate_random_df():
    data = np.around(np.random.rand(10, 5), decimals=9)
    column_names = [f'pgcf_{i+1}' for i in range(5)]
    random_df = pd.DataFrame(data, columns=column_names)
    return random_df


def _get_main_df():
    main_df = pd.read_csv("assets/main_df.csv")
    return main_df


def _get_highlighted_members_dict():
    sample_df = _get_main_df().sample(3)
    sample_dict = sample_df.to_dict("records")
    return sample_dict


def _get_story_text():
    with open("assets/story.txt", "r") as f:
        return f.read()

# UPDATES


def _update_metrics(state):
    main_df = state["main_df"]
    bmi = statistics.mean(
        (main_df['weight_g'] / 1000) / ((main_df['length_cm'] / 100) ** 2))
    diversity_index = main_df['feather_color'].nunique()/len(main_df)
    metrics = {
        "average_weight": round(main_df['weight_g'].mean(), 0),
        "average_length": round(main_df['length_cm'].mean(), 0),
        "average_bmi": round(bmi, 2),
        "diversity": round(diversity_index, 2),
    }
    metrics.update({
        "average_weight_note": "+Acceptable",
        "average_length_note": "+Acceptable",
        "average_bmi_note": "-Overweight" if metrics["average_bmi"] >= 5.3 else "+Acceptable",
        "diversity_note": "-Not diverse" if metrics["diversity"] < 0.8 else "+Acceptable",
    })
    state["metrics"] = metrics


def _update_role_chart(state):
    main_df = state["main_df"]
    custom_color_scale = ["#dd43df", "#e057e7",
                          "#e36bef", "#e680f7", "#e994ff"]
    role_counts = main_df['role'].value_counts().reset_index()
    role_counts.columns = ['role', 'count']
    fig = px.bar(role_counts, x='role', y='count', color='role',
                 color_discrete_sequence=custom_color_scale)
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=50),
        showlegend=False
    )
    state["role_chart"] = fig


def _update_scatter_chart(state):
    main_df = state["main_df"]
    average_role_data = main_df.groupby("role").agg(
        {"length_cm": "mean", "weight_g": "mean"}).reset_index()
    fig = px.scatter(average_role_data, x="length_cm", y="weight_g",
                     color="role", height=400, size_max=10, size="weight_g")
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=50),
        showlegend=False
    )
    state["scatter_chart"] = fig

def _get_altair_chart():
    x, y = np.meshgrid(range(-5, 5), range(-5, 5))
    z = x ** 2 + y ** 2
    source = pd.DataFrame({'x': x.ravel(),'y': y.ravel(),'z': z.ravel()})
    chart = alt.Chart(source).mark_rect().encode(
        x='x:O',
        y='y:O',
        color='z:Q'
    )
    return chart

# STATE INIT


initial_state = ss.init_state({
    "main_df": _get_main_df(),
    "highlighted_members_dict": _get_highlighted_members_dict(),
    "random_df": _generate_random_df(),
    "hue_rotation": 26,
    "story": {
        "text": _get_story_text(),  # For display
        "file": ss.pack_file("assets/story.txt", "text/plain")  # For download
    },
    "filter": {
        "min_length": 25,
        "min_weight": 300,
    },
    "counter": 0,
    "metrics": {},
    "b": {
        "pet_count": 8
    },
    "utfࠀ": "ثعلب كلب",
    "prog_languages": {
        "c": {"name": "C"},
        "ts": {"name": "TypeScript"},
        "py": {"name": "Python"}
    },
    "cities": {},
    "articles": {
        "Banana": {
            "type": "fruit",
            "colour": "yellow"
        },
        "Lettuce": {
            "type": "vegetable",
            "colour": "green"
        },
        "Spinach": {
            "type": "vegetable",
            "colour": "green"
        }
    },
    "order_list": [],
    "altair_chart": _get_altair_chart()
})

update(initial_state, None)
