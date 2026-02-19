import os
from dataclasses import dataclass

from component_configs import COMPONENT_CONFIGS
from pattern_transform import normalize, rotate_90, rotate_180, rotate_270
from rle_loader import load_rle


@dataclass
class Port:
    name: str
    kind: str
    x: int
    y: int
    direction: int


@dataclass
class PlacedComponent:
    config_name: str
    origin_x: int
    origin_y: int
    orientation: int
    ports: dict
    size: dict
    regions: dict
    options: dict


class Components:
    _VALID_ROTATIONS = {0, 90, 180, 270}

    def __init__(self, patterns_dir):
        self.patterns_dir = patterns_dir
        self.instances = []
        self._load_base_patterns()

    def _rotations(self, pattern):
        base = normalize(pattern)
        return {
            0: base,
            90: normalize(rotate_90(base)),
            180: normalize(rotate_180(base)),
            270: normalize(rotate_270(base)),
        }

    def _load_base_patterns(self):
        glider = load_rle(os.path.join(self.patterns_dir, "glider.rle"))
        gun = load_rle(os.path.join(self.patterns_dir, "glider_gun.rle"))
        eater = load_rle(os.path.join(self.patterns_dir, "eater.rle"))
        reflector = load_rle(os.path.join(self.patterns_dir, "reflector.rle"))

        self._patterns = {
            "glider": self._rotations(glider),
            "gun": self._rotations(gun),
            "eater": self._rotations(eater),
            "reflector": self._rotations(reflector),
        }

        for name, rots in self._patterns.items():
            setattr(self, name, rots[0])
            setattr(self, f"{name}_90", rots[90])
            setattr(self, f"{name}_180", rots[180])
            setattr(self, f"{name}_270", rots[270])

    def _resolve_rotation(self, rotation):
        if rotation not in self._VALID_ROTATIONS:
            raise ValueError("rotation must be one of: 0, 90, 180, 270")
        return rotation

    def _rotate_point(self, x, y, rotation):
        rotation = self._resolve_rotation(rotation)
        if rotation == 0:
            return x, y
        if rotation == 90:
            return -y, x
        if rotation == 180:
            return -x, -y
        return y, -x

    def _compose_rotation(self, a, b):
        self._resolve_rotation(b)
        return (int(a) + b) % 360

    def _rotate_box(self, xmin, xmax, ymin, ymax, rotation):
        corners = [
            (xmin, ymin),
            (xmin, ymax),
            (xmax, ymin),
            (xmax, ymax),
        ]
        rotated = [self._rotate_point(x, y, rotation) for x, y in corners]
        xs = [x for x, _ in rotated]
        ys = [y for _, y in rotated]
        return min(xs), max(xs), min(ys), max(ys)

    def _place_atomic(self, circuit, name, x, y, rotation=0):
        rotation = self._resolve_rotation(rotation)
        if name not in self._patterns:
            raise ValueError(f"unknown component: {name}")
        circuit.place(self._patterns[name][rotation], x, y)

    def _input_enabled(self, inputs, name):
        if inputs.get(name, False):
            return True
        if inputs.get(name.lower(), False):
            return True
        prefixed = f"input_{name}"
        if inputs.get(prefixed, False):
            return True
        if inputs.get(prefixed.lower(), False):
            return True
        return False

    def _place_input_guns(self, circuit, config_name, origin_x, origin_y, orientation, inputs):
        config = COMPONENT_CONFIGS[config_name]
        input_guns = config.get("input_guns", {})
        for name, gun in input_guns.items():
            if not self._input_enabled(inputs, name):
                continue
            phase_before = gun.get("phase_before", 0)
            for _ in range(phase_before):
                circuit.life.step()
            local_x, local_y = gun["offset"]
            dx, dy = self._rotate_point(local_x, local_y, orientation)
            part_rotation = self._compose_rotation(gun["rotation"], orientation)
            self._place_atomic(
                circuit,
                gun["component"],
                origin_x + dx,
                origin_y + dy,
                rotation=part_rotation,
            )

    def _port_spec(self, config_name, port_name):
        if config_name not in COMPONENT_CONFIGS:
            raise ValueError(f"unknown configuration: {config_name}")
        for port in COMPONENT_CONFIGS[config_name].get("ports", []):
            if port["name"] == port_name:
                return port
        raise ValueError(f"unknown port '{port_name}' for configuration '{config_name}'")

    def place_component(self, circuit, name, x, y, rotation=0):
        self._place_atomic(circuit, name, x, y, rotation=rotation)

    def compute_origin_for_port(self, config_name, port_name, world_x, world_y, orientation):
        orientation = self._resolve_rotation(orientation)
        port = self._port_spec(config_name, port_name)
        px, py = port["offset"]
        dx, dy = self._rotate_point(px, py, orientation)
        return world_x - dx, world_y - dy

    def find_orientations_for_port_direction(self, config_name, port_name, desired_direction):
        port = self._port_spec(config_name, port_name)
        matches = []
        for orientation in sorted(self._VALID_ROTATIONS):
            direction = self._compose_rotation(port.get("direction", 0), orientation)
            if direction == desired_direction % 360:
                matches.append(orientation)
        return matches

    def place_single_glider(self, circuit, x, y, orientation=0):
        return self.place_configured(
            circuit,
            "single_glider",
            x,
            y,
            orientation=orientation,
        )

    def place_glider_gun(self, circuit, x, y, orientation=0):
        return self.place_configured(
            circuit,
            "glider_gun_component",
            x,
            y,
            orientation=orientation,
        )

    def place_repeater(self, circuit, x, y, orientation=0):
        return self.place_configured(
            circuit,
            "repeater",
            x,
            y,
            orientation=orientation,
        )

    def place_on_grid(
        self,
        circuit,
        config_name,
        grid_x,
        grid_y,
        cell_w=200,
        cell_h=200,
        orientation=0,
        phase_override=None,
        inputs=None,
    ):
        origin_x = grid_x * cell_w
        origin_y = grid_y * cell_h
        return self.place_configured(
            circuit=circuit,
            config_name=config_name,
            origin_x=origin_x,
            origin_y=origin_y,
            orientation=orientation,
            phase_override=phase_override,
            inputs=inputs,
        )

    def place_configured(
        self,
        circuit,
        config_name,
        origin_x,
        origin_y,
        orientation=0,
        phase_override=None,
        inputs=None,
    ):
        orientation = self._resolve_rotation(orientation)
        inputs = inputs or {}

        if config_name not in COMPONENT_CONFIGS:
            raise ValueError(f"unknown configuration: {config_name}")

        config = COMPONENT_CONFIGS[config_name]
        for part in config["parts"]:
            enabled_by = part.get("enabled_by")
            if enabled_by is not None and not inputs.get(enabled_by, False):
                continue

            phase_before = part.get("phase_before", 0)
            if part.get("phase_override", False) and phase_override is not None:
                phase_before = phase_override

            for _ in range(phase_before):
                circuit.life.step()

            local_x, local_y = part["offset"]
            dx, dy = self._rotate_point(local_x, local_y, orientation)
            part_rotation = self._compose_rotation(part["rotation"], orientation)
            self._place_atomic(
                circuit,
                part["component"],
                origin_x + dx,
                origin_y + dy,
                rotation=part_rotation,
            )

        # Apply referenced input guns (A/B/...) only when explicitly enabled.
        self._place_input_guns(
            circuit=circuit,
            config_name=config_name,
            origin_x=origin_x,
            origin_y=origin_y,
            orientation=orientation,
            inputs=inputs,
        )

        ports = {}
        for port in config.get("ports", []):
            px, py = port["offset"]
            dx, dy = self._rotate_point(px, py, orientation)
            direction = self._compose_rotation(port.get("direction", 0), orientation)
            ports[port["name"]] = Port(
                name=port["name"],
                kind=port["kind"],
                x=origin_x + dx,
                y=origin_y + dy,
                direction=direction,
            )

        regions = {}
        for region in config.get("regions", []):
            xmin, xmax, ymin, ymax = self._rotate_box(
                region["xmin"],
                region["xmax"],
                region["ymin"],
                region["ymax"],
                orientation,
            )
            regions[region["name"]] = {
                "name": region["name"],
                "kind": region.get("kind", "probe"),
                "xmin": origin_x + xmin,
                "xmax": origin_x + xmax,
                "ymin": origin_y + ymin,
                "ymax": origin_y + ymax,
            }

        size = config.get("size")
        if size is None:
            size = {"width": 0, "height": 0}
        width = size["width"]
        height = size["height"]
        if orientation in {90, 270}:
            width, height = height, width

        placed = PlacedComponent(
            config_name=config_name,
            origin_x=origin_x,
            origin_y=origin_y,
            orientation=orientation,
            ports=ports,
            size={"width": width, "height": height},
            regions=regions,
            options={"phase_override": phase_override, "inputs": dict(inputs)},
        )
        self.instances.append(placed)
        return placed

    def apply_component_inputs(self, circuit, placed_component, inputs):
        """
        Add referenced input guns for an already placed component.
        """
        self._place_input_guns(
            circuit=circuit,
            config_name=placed_component.config_name,
            origin_x=placed_component.origin_x,
            origin_y=placed_component.origin_y,
            orientation=placed_component.orientation,
            inputs=inputs,
        )
        placed_component.options.setdefault("applied_inputs", []).append(dict(inputs))
        return placed_component

    def route_ports(self, source_component, source_port, target_component, target_port):
        if source_port not in source_component.ports:
            raise ValueError(f"unknown source port: {source_port}")
        if target_port not in target_component.ports:
            raise ValueError(f"unknown target port: {target_port}")

        src = source_component.ports[source_port]
        dst = target_component.ports[target_port]
        return {
            "from": (src.x, src.y),
            "to": (dst.x, dst.y),
            "delta": (dst.x - src.x, dst.y - src.y),
        }

    def place_annihilation_pair(self, circuit, origin_x, origin_y, orientation=0, phase=1):
        return self.place_configured(
            circuit,
            "annihilation_pair",
            origin_x,
            origin_y,
            orientation=orientation,
            phase_override=phase,
        )

    def place_and_gate(
        self,
        circuit,
        origin_x,
        origin_y,
        input_A=False,
        input_B=False,
        orientation=0,
        phase=1,
    ):
        return self.place_configured(
            circuit,
            "and_gate",
            origin_x,
            origin_y,
            orientation=orientation,
            phase_override=phase,
            inputs={"input_A": input_A, "input_B": input_B},
        )

    def place_or_gate(
        self,
        circuit,
        origin_x,
        origin_y,
        input_A=False,
        input_B=False,
        orientation=0,
        phase=1,
    ):
        return self.place_configured(
            circuit,
            "or_gate",
            origin_x,
            origin_y,
            orientation=orientation,
            phase_override=phase,
            inputs={"input_A": input_A, "input_B": input_B},
        )

    def place_not_gate(self, circuit, origin_x, origin_y, input_A=False, orientation=0, phase=1):
        return self.place_configured(
            circuit,
            "not_gate",
            origin_x,
            origin_y,
            orientation=orientation,
            phase_override=phase,
            inputs={"input_A": input_A},
        )

    def place_eater(self, circuit, x, y, rotation=0):
        return self.place_configured(
            circuit,
            "eater_component",
            x,
            y,
            orientation=rotation,
        )

    def place_reflector(self, circuit, x, y, orientation=0):
        return self.place_configured(
            circuit,
            "reflector",
            x,
            y,
            orientation=orientation,
        )
