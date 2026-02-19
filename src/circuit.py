class Circuit:

    def __init__(self, life):
        self.life = life

    def place(self, pattern, x, y):
        for px, py in pattern:
            self.life.alive.add((x + px, y + py))

    def bounding_box(pattern):
        xs = [x for x, _ in pattern]
        ys = [y for _, y in pattern]
        return min(xs), max(xs), min(ys), max(ys)

    def inject(self, pattern, x, y, t_delay=0):
        for _ in range(t_delay):
            self.life.step()

        self.place(pattern, x, y)


class CircuitBuilder:
    """
    Grid-oriented builder on top of Circuit + Components.

    This manages component placement, records placed instances, and supports a
    simple port-to-port connection API that drops repeater components along a
    Manhattan path for quick circuit prototyping.
    """

    def __init__(self, life, components, cell_w=220, cell_h=220):
        self.life = life
        self.circuit = Circuit(life)
        self.components = components
        self.cell_w = cell_w
        self.cell_h = cell_h
        self.nodes = {}
        self.connections = []

    def _direction_to_unit(self, direction):
        d = direction % 360
        mapping = {
            0: (1, 0),
            45: (1, 1),
            90: (0, 1),
            135: (-1, 1),
            180: (-1, 0),
            225: (-1, -1),
            270: (0, -1),
            315: (1, -1),
        }
        if d not in mapping:
            raise ValueError(f"direction must be one of 0,45,...,315; got {direction}")
        return mapping[d]

    def add_component(
        self,
        component_id,
        config_name,
        grid_x,
        grid_y,
        orientation=0,
        phase_override=None,
        inputs=None,
    ):
        placed = self.components.place_on_grid(
            self.circuit,
            config_name=config_name,
            grid_x=grid_x,
            grid_y=grid_y,
            cell_w=self.cell_w,
            cell_h=self.cell_h,
            orientation=orientation,
            phase_override=phase_override,
            inputs=inputs,
        )
        self.nodes[component_id] = placed
        return placed

    def add_component_aligned(
        self,
        component_id,
        config_name,
        source_id,
        source_port,
        target_port,
        distance=0,
        orientation=None,
        phase_override=None,
        inputs=None,
    ):
        if source_id not in self.nodes:
            raise ValueError(f"unknown source component: {source_id}")

        src = self.nodes[source_id].ports[source_port]
        if src.kind != "output":
            raise ValueError(f"source port '{source_port}' is not an output port")

        desired_direction = src.direction % 360
        if orientation is None:
            matches = self.components.find_orientations_for_port_direction(
                config_name, target_port, desired_direction
            )
            if not matches:
                raise ValueError(
                    f"no orientation for {config_name}.{target_port} matches direction {desired_direction}"
                )
            orientation = matches[0]
        else:
            matches = self.components.find_orientations_for_port_direction(
                config_name, target_port, desired_direction
            )
            if orientation not in matches:
                raise ValueError(
                    f"orientation {orientation} does not align {config_name}.{target_port} with {desired_direction}"
                )

        ux, uy = self._direction_to_unit(desired_direction)
        target_x = src.x + ux * distance
        target_y = src.y + uy * distance
        origin_x, origin_y = self.components.compute_origin_for_port(
            config_name=config_name,
            port_name=target_port,
            world_x=target_x,
            world_y=target_y,
            orientation=orientation,
        )
        placed = self.components.place_configured(
            self.circuit,
            config_name=config_name,
            origin_x=origin_x,
            origin_y=origin_y,
            orientation=orientation,
            phase_override=phase_override,
            inputs=inputs,
        )
        self.nodes[component_id] = placed
        self.connections.append(
            {
                "from": (src.x, src.y),
                "to": (target_x, target_y),
                "type": "aligned_attach",
                "source": f"{source_id}.{source_port}",
                "target": f"{component_id}.{target_port}",
            }
        )
        return placed

    def _segment_points(self, x1, y1, x2, y2, spacing):
        points = []
        if x1 == x2 and y1 == y2:
            return points
        if x1 != x2 and y1 != y2:
            raise ValueError("segment must be axis-aligned")

        if x1 == x2:
            step = spacing if y2 > y1 else -spacing
            y = y1 + step
            while (y < y2) if step > 0 else (y > y2):
                points.append((x1, y))
                y += step
            return points

        step = spacing if x2 > x1 else -spacing
        x = x1 + step
        while (x < x2) if step > 0 else (x > x2):
            points.append((x, y1))
            x += step
        return points

    def connect(
        self,
        source_id,
        source_port,
        target_id,
        target_port,
        repeater_spacing=120,
        route_style="hv",
    ):
        if source_id not in self.nodes:
            raise ValueError(f"unknown source component: {source_id}")
        if target_id not in self.nodes:
            raise ValueError(f"unknown target component: {target_id}")

        src = self.nodes[source_id].ports[source_port]
        dst = self.nodes[target_id].ports[target_port]

        if route_style not in {"hv", "vh"}:
            raise ValueError("route_style must be 'hv' or 'vh'")

        if route_style == "hv":
            waypoints = [(src.x, src.y), (dst.x, src.y), (dst.x, dst.y)]
        else:
            waypoints = [(src.x, src.y), (src.x, dst.y), (dst.x, dst.y)]

        repeater_points = []
        for i in range(len(waypoints) - 1):
            x1, y1 = waypoints[i]
            x2, y2 = waypoints[i + 1]
            repeater_points.extend(self._segment_points(x1, y1, x2, y2, repeater_spacing))

        placed_repeaters = []
        for rx, ry in repeater_points:
            placed_repeaters.append(
                self.components.place_repeater(self.circuit, rx, ry, orientation=0)
            )

        connection = {
            "from": (src.x, src.y),
            "to": (dst.x, dst.y),
            "waypoints": waypoints,
            "repeaters": placed_repeaters,
        }
        self.connections.append(connection)
        return connection

    def drive_input(
        self,
        source_id,
        source_port,
        target_id,
        target_port,
        repeater_spacing=120,
        route_style="hv",
    ):
        
        # Route a produced signal from source output port into target input port.
        
        if source_id not in self.nodes:
            raise ValueError(f"unknown source component: {source_id}")
        if target_id not in self.nodes:
            raise ValueError(f"unknown target component: {target_id}")
        src = self.nodes[source_id].ports[source_port]
        dst = self.nodes[target_id].ports[target_port]
        if src.kind != "output":
            raise ValueError(f"{source_id}.{source_port} is not an output port")
        if dst.kind != "input":
            raise ValueError(f"{target_id}.{target_port} is not an input port")
        return self.connect(
            source_id=source_id,
            source_port=source_port,
            target_id=target_id,
            target_port=target_port,
            repeater_spacing=repeater_spacing,
            route_style=route_style,
        )

    def add_input_source(
        self,
        component_id,
        target_id,
        target_port,
        source_config="glider_gun_component",
        source_port="out",
        distance=240,
        orientation=None,
        phase_override=None,
        inputs=None,
    ):
        """
        Place an explicit upstream input source aligned to a target input port.

        The source output direction is matched to target input direction, and
        the source is positioned `distance` cells upstream along that lane.
        """
        if target_id not in self.nodes:
            raise ValueError(f"unknown target component: {target_id}")

        dst = self.nodes[target_id].ports[target_port]
        if dst.kind != "input":
            raise ValueError(f"{target_id}.{target_port} is not an input port")

        desired_direction = dst.direction % 360
        if orientation is None:
            matches = self.components.find_orientations_for_port_direction(
                source_config, source_port, desired_direction
            )
            if not matches:
                raise ValueError(
                    f"no orientation for {source_config}.{source_port} matches direction {desired_direction}"
                )
            orientation = matches[0]
        else:
            matches = self.components.find_orientations_for_port_direction(
                source_config, source_port, desired_direction
            )
            if orientation not in matches:
                raise ValueError(
                    f"orientation {orientation} does not align {source_config}.{source_port} with {desired_direction}"
                )

        ux, uy = self._direction_to_unit(desired_direction)
        source_out_x = dst.x - ux * distance
        source_out_y = dst.y - uy * distance
        origin_x, origin_y = self.components.compute_origin_for_port(
            config_name=source_config,
            port_name=source_port,
            world_x=source_out_x,
            world_y=source_out_y,
            orientation=orientation,
        )
        placed = self.components.place_configured(
            self.circuit,
            config_name=source_config,
            origin_x=origin_x,
            origin_y=origin_y,
            orientation=orientation,
            phase_override=phase_override,
            inputs=inputs,
        )
        self.nodes[component_id] = placed
        self.connections.append(
            {
                "type": "input_source",
                "from": (placed.ports[source_port].x, placed.ports[source_port].y),
                "to": (dst.x, dst.y),
                "source": f"{component_id}.{source_port}",
                "target": f"{target_id}.{target_port}",
            }
        )
        return placed

    def set_component_inputs(self, component_id, inputs):
        # Enable referenced input guns on an already placed component.
        if component_id not in self.nodes:
            raise ValueError(f"unknown component: {component_id}")
        placed = self.nodes[component_id]
        self.components.apply_component_inputs(self.circuit, placed, inputs)
        self.connections.append(
            {
                "type": "local_inputs",
                "component": component_id,
                "inputs": dict(inputs),
            }
        )
        return placed
