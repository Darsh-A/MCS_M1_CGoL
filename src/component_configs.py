
COMPONENT_CONFIGS = {
    "single_glider": {
        "size": {"width": 3, "height": 3},
        "parts": [
            {"component": "glider", "offset": (0, 0), "rotation": 0},
        ],
        "ports": [
            {"name": "out", "kind": "output", "offset": (0, 0), "direction": 315},
        ],
    },
    "glider_gun_component": {
        "size": {"width": 36, "height": 9},
        "parts": [
            {"component": "gun", "offset": (0, 0), "rotation": 0},
        ],
        "ports": [
            {"name": "out", "kind": "output", "offset": (36, 5), "direction": 315},
        ],
        "regions": [
            {
                "name": "output_lane",
                "kind": "output",
                "xmin": 40,
                "xmax": 85,
                "ymin": -60,
                "ymax": -15,
            },
        ],
    },
    "eater_component": {
        "size": {"width": 4, "height": 4},
        "parts": [
            {"component": "eater", "offset": (0, 0), "rotation": 0},
        ],
        "ports": [
            {"name": "in", "kind": "input", "offset": (0, 0), "direction": 315},
        ],
        "regions": [
            {
                "name": "input_lane",
                "kind": "input",
                "xmin": -10,
                "xmax": 20,
                "ymin": -20,
                "ymax": 10,
            }
        ],
    },
    "annihilation_pair": {
        "size": {"width": 36, "height": 209},
        "parts": [
            {"component": "gun", "offset": (0, -100), "rotation": 90},
            {
                "component": "gun",
                "offset": (0, 100),
                "rotation": 180,
                "phase_before": 1,
                "phase_override": True,
            },
        ],
        "ports": [
            {"name": "input_nw", "kind": "input", "offset": (0, -100), "direction": 90},
            {"name": "input_sw", "kind": "input", "offset": (0, 100), "direction": 180},
            {"name": "output", "kind": "output", "offset": (0, 0), "direction": 180},
        ],
    },
    "and_gate": {
        "size": {"width": 200, "height": 220},
        "parts": [
            {"component": "gun", "offset": (120, -60), "rotation": 270},
        ],
        "input_guns": {
            "A": {"component": "gun", "offset": (0, 0), "rotation": 0},
            "B": {"component": "gun", "offset": (-60, 0), "rotation": 0},
        },
        "ports": [
            {"name": "A", "kind": "input", "offset": (-60, 60), "direction": 315},
            {"name": "B", "kind": "input", "offset": (-120, 60), "direction": 315},
            {"name": "Y", "kind": "output", "offset": (36, 45), "direction": 315},
        ],
    },
    "or_gate": {
        "size": {"width": 220, "height": 240},
        "parts": [
            {"component": "gun", "offset": (120, -60), "rotation": 270},
            {"component": "gun", "offset": (-60, -60), "rotation": 0},
            {"component": "eater", "offset": (82, -123), "rotation": 0},
        ],
        "input_guns": {
            "A": {"component": "gun", "offset": (0, 0), "rotation": 0},
            "B": {"component": "gun", "offset": (-60, 0), "rotation": 0},
        },
        "ports": [
            {"name": "A", "kind": "input", "offset": (0, 0), "direction": 315},
            {"name": "B", "kind": "input", "offset": (-60, 0), "direction": 315},
            {"name": "Y", "kind": "output", "offset": (36, 45), "direction": 315},
        ],
    },
    "not_gate": {
        "size": {"width": 220, "height": 220},
        "parts": [
            {"component": "gun", "offset": (120, -60), "rotation": 270},
        ],
        "input_guns": {
            "A": {"component": "gun", "offset": (0, 0), "rotation": 0},
        },
        "ports": [
            {"name": "A", "kind": "input", "offset": (0, 0), "direction": 315},
            {"name": "Y", "kind": "output", "offset": (160, -160), "direction": 315},
        ],
    },
    "reflector": {
        "size": {"width": 9, "height": 23},
        "parts": [
            {"component": "reflector", "offset": (0, 0), "rotation": 0},
        ],
        "ports": [
            {"name": "in", "kind": "input", "offset": (0, 0), "direction": 315},
            {"name": "out", "kind": "output", "offset": (0, 0), "direction": 225},
        ],
        "regions": [
            {
                "name": "input_lane",
                "kind": "input",
                "xmin": -10,
                "xmax": 15,
                "ymin": -20,
                "ymax": 10,
            },
            {
                "name": "output_lane",
                "kind": "output",
                "xmin": -50,
                "xmax": -10,
                "ymin": -70,
                "ymax": -5,
            },
        ],
    },
    "repeater": {
        "size": {"width": 9, "height": 23},
        "parts": [
            {"component": "reflector", "offset": (0, 0), "rotation": 0},
        ],
        "ports": [
            {"name": "in", "kind": "input", "offset": (0, 0), "direction": 315},
            {"name": "out", "kind": "output", "offset": (0, 0), "direction": 225},
        ],
        "regions": [
            {
                "name": "input_lane",
                "kind": "input",
                "xmin": -10,
                "xmax": 15,
                "ymin": -20,
                "ymax": 10,
            },
            {
                "name": "output_lane",
                "kind": "output",
                "xmin": -50,
                "xmax": -10,
                "ymin": -70,
                "ymax": -5,
            },
        ],
    },
    "reflector_gun": {
        "size": {"width": 39, "height": 37},
        "parts": [
            {"component": "gun", "offset": (0, 28), "rotation": 0},
            {"component": "reflector", "offset": (30, 0), "rotation": 0},
        ],
        "ports": [
            {"name": "out", "kind": "output", "offset": (-5, -5), "direction": 225},
        ],
    },
}
