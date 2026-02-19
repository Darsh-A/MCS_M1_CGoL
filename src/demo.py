from dataclasses import dataclass
from pathlib import Path
import importlib
import time

import matplotlib.animation as mpl_animation
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image as PILImage, ImageSequence

from IPython.display import Image, Video, display

from circuit import Circuit, CircuitBuilder
from components import Components
from component_configs import COMPONENT_CONFIGS
from life_engine import Life
import animator


def find_project_root(start=None):
    base = Path(start).resolve() if start is not None else Path.cwd().resolve()
    for candidate in [base, *base.parents]:
        if (candidate / "src" / "life_engine.py").exists() and (
            candidate / "patterns" / "glider.rle"
        ).exists():
            return candidate
    return base


@dataclass
class DemoContext:
    root: Path
    out_dir: Path
    comp: Components


def create_context(root=None):
    project_root = find_project_root(root)
    out_dir = project_root / "tests" / "output" / "notebook"
    out_dir.mkdir(parents=True, exist_ok=True)
    comp = Components(str(project_root / "patterns"))
    return DemoContext(root=project_root, out_dir=out_dir, comp=comp)


def print_context(ctx):
    print(f"Project root: {ctx.root}")
    print(f"Output dir:   {ctx.out_dir}")


def _safe_name(name):
    return "".join(ch if ch.isalnum() else "_" for ch in name.lower()).strip("_")


def _unique_out_path(ctx, title, suffix):
    stamp = int(time.time() * 1000)
    return ctx.out_dir / f"{_safe_name(title)}_{stamp}{suffix}"


def _animate_with_reload(*args, **kwargs):
    # Keep notebook behavior stable after edits to src/animator.py.
    importlib.reload(animator)
    return animator.animate_life(*args, **kwargs)


def render_snapshot(
    ctx,
    life,
    title,
    width=220,
    height=220,
    show_stream=False,
    show_grid=True,
    display_media=True,
    announce=True,
):
    out_path = _unique_out_path(ctx, title, ".png")
    _animate_with_reload(
        life,
        steps=1,
        width=width,
        height=height,
        save=str(out_path),
        show_stream=show_stream,
        show_grid=show_grid,
        grid_spacing=20,
        grid_alpha=0.2,
    )
    if (not out_path.exists()) or out_path.stat().st_size == 0:
        raise RuntimeError(f"Snapshot was not created: {out_path}")
    if announce:
        print(f"Snapshot: {out_path} ({out_path.stat().st_size} bytes)")
    if display_media:
        try:
            display(Image(filename=str(out_path)))
        except Exception:
            display(Image(data=out_path.read_bytes(), format="png"))
    return out_path


def render_animation(
    ctx,
    life,
    title,
    steps=240,
    width=260,
    height=260,
    show_stream=True,
    show_grid=True,
    speed=1.0,
    media_format="mp4",
    display_media=True,
    announce=True,
):
    ext = media_format.lower().lstrip(".")
    out_path = _unique_out_path(ctx, title, f".{ext}")
    _animate_with_reload(
        life,
        steps=steps,
        width=width,
        height=height,
        save=str(out_path),
        show_stream=show_stream,
        show_grid=show_grid,
        speed=speed,
        grid_spacing=20,
        grid_alpha=0.2,
    )
    if (not out_path.exists()) or out_path.stat().st_size == 0:
        raise RuntimeError(f"Animation was not created: {out_path}")
    if announce:
        print(f"Animation: {out_path} ({out_path.stat().st_size} bytes)")
    if display_media:
        if ext == "gif":
            try:
                display(Image(filename=str(out_path)))
            except Exception:
                display(Image(data=out_path.read_bytes(), format="gif"))
        else:
            try:
                display(Video(filename=str(out_path), embed=True))
            except Exception:
                display(Video(data=out_path.read_bytes(), embed=True, mimetype="video/mp4"))
    return out_path


def run_basic_rules_demo(ctx):
    life = Life()
    circuit = Circuit(life)
    ctx.comp.place_component(circuit, "glider", x=0, y=0, rotation=0)
    render_snapshot(ctx, life, title="glider_t0", width=40, height=40)
    render_animation(ctx, life, title="glider_motion", steps=90, width=40, height=40)


def print_component_catalog():
    print("Configured components available:")
    for name in sorted(COMPONENT_CONFIGS.keys()):
        ports = [f"{p['name']}({p['kind']})" for p in COMPONENT_CONFIGS[name].get("ports", [])]
        print(f"- {name:20s} ports={ports}")


def run_atomic_component_snapshots(ctx):
    for pattern_name, width, height in [
        ("glider", 120, 120),
        ("gun", 260, 200),
        ("eater", 120, 120),
        ("reflector", 180, 180),
    ]:
        life = Life()
        circuit = Circuit(life)
        ctx.comp.place_component(circuit, pattern_name, x=0, y=0, rotation=0)
        render_snapshot(
            ctx,
            life,
            title=f"atomic_{pattern_name}",
            width=width,
            height=height,
        )


def _load_gif_frames(path):
    with PILImage.open(path) as img:
        return [np.asarray(frame.convert("RGB")) for frame in ImageSequence.Iterator(img)]


def run_atomic_component_grid(ctx):
    """
    Render component snapshot + animation in a 2-column matplotlib grid.
    Animations are loaded from GIFs so they can play inside subplot axes.
    """
    specs = [
        ("glider", 40, 40, 90),
        ("gun", 120, 120, 180),
        ("eater", 20, 20, 140),
        ("reflector", 120, 120, 200),
    ]

    rows = []
    for pattern_name, width, height, steps in specs:
        life = Life()
        circuit = Circuit(life)
        ctx.comp.place_component(circuit, pattern_name, x=0, y=0, rotation=0)

        snapshot_path = render_snapshot(
            ctx,
            life,
            title=f"atomic_{pattern_name}_grid_snapshot",
            width=width,
            height=height,
            display_media=False,
            announce=False,
        )
        # Build animation from a fresh initial state so each media starts at t=0.
        life_anim = Life()
        circuit_anim = Circuit(life_anim)
        ctx.comp.place_component(circuit_anim, pattern_name, x=0, y=0, rotation=0)
        animation_path = render_animation(
            ctx,
            life_anim,
            title=f"atomic_{pattern_name}_grid_motion",
            steps=steps,
            width=width,
            height=height,
            media_format="gif",
            display_media=False,
            announce=False,
        )
        rows.append(
            {
                "name": pattern_name,
                "snapshot": plt.imread(snapshot_path),
                "frames": _load_gif_frames(animation_path),
            }
        )

    fig, axes = plt.subplots(len(rows), 2, figsize=(8, 2.8 * len(rows)))
    if len(rows) == 1:
        axes = np.array([axes])

    anim_artists = []
    for row_idx, row in enumerate(rows):
        ax_snapshot = axes[row_idx, 0]
        ax_anim = axes[row_idx, 1]

        ax_snapshot.imshow(row["snapshot"])
        ax_snapshot.set_title(f"{row['name']} snapshot")
        ax_snapshot.axis("off")

        frame0 = row["frames"][0]
        artist = ax_anim.imshow(frame0)
        ax_anim.set_title(f"{row['name']} animation")
        ax_anim.axis("off")
        anim_artists.append((artist, row["frames"]))

    plt.tight_layout()

    max_frames = max(len(frames) for _, frames in anim_artists)

    def _update(frame_idx):
        updated = []
        for artist, frames in anim_artists:
            artist.set_data(frames[frame_idx % len(frames)])
            updated.append(artist)
        return updated

    animation = mpl_animation.FuncAnimation(
        fig,
        _update,
        frames=max_frames,
        interval=50,
        blit=False,
        repeat=True,
    )
    plt.rcParams["animation.html"] = "jshtml"
    display(animation)
    plt.close(fig)
    return animation


def run_reflector_gun_demo(ctx):
    life = Life()
    circuit = Circuit(life)
    ctx.comp.place_component(circuit, "gun", x=-10, y=28, rotation=0)
    ctx.comp.place_reflector(circuit, x=20, y=0, orientation=0)
    render_snapshot(ctx, life, title="reflector_gun_setup", width=100, height=100)
    render_animation(
        ctx,
        life,
        title="reflector_gun_motion",
        steps=320,
        width=100,
        height=100,
    )


def demo_gate(ctx, config_name, title, inputs=None, steps=2000, width=420, height=420):
    life = Life()
    builder = CircuitBuilder(life, ctx.comp, cell_w=260, cell_h=260)
    gate = builder.add_component(
        component_id="g1",
        config_name=config_name,
        grid_x=0,
        grid_y=0,
        phase_override=1,
    )
    if inputs:
        builder.set_component_inputs("g1", inputs)

    print(f"{title} orientation={gate.orientation}")
    for name, port in gate.ports.items():
        print(f"  {name}: kind={port.kind}, pos=({port.x},{port.y}), dir={port.direction}")

    render_snapshot(ctx, life, title=f"{title}_setup", width=width, height=height)
    render_animation(
        ctx,
        life,
        title=f"{title}_motion",
        steps=steps,
        width=width,
        height=height,
        speed=3.0,
    )


def run_all_gate_demos(ctx):
    demo_gate(
        ctx,
        "not_gate",
        "not_gate_demo",
        inputs={"A": True},
        steps=420,
    )
    demo_gate(
        ctx,
        "and_gate",
        "and_gate_demo",
        inputs={"A": True, "B": True},
        steps=420,
    )
    demo_gate(
        ctx,
        "or_gate",
        "or_gate_demo",
        inputs={"A": True, "B": True},
        steps=420,
    )


def run_and_to_not_demo(ctx):
    life = Life()
    builder = CircuitBuilder(life, ctx.comp, cell_w=260, cell_h=260)

    and1 = builder.add_component(
        component_id="and1",
        config_name="and_gate",
        grid_x=0,
        grid_y=0,
        phase_override=1,
    )
    not1 = builder.add_component_aligned(
        component_id="not1",
        config_name="not_gate",
        source_id="and1",
        source_port="Y",
        target_port="A",
        distance=120,
        phase_override=1,
    )
    builder.set_component_inputs("and1", {"A": True, "B": True})

    print("and1 orientation:", and1.orientation)
    print("not1 orientation:", not1.orientation)
    print("Connections:", builder.connections)

    render_snapshot(ctx, life, title="and_to_not_setup", width=920, height=680)
    render_animation(
        ctx,
        life,
        title="and_to_not_motion",
        steps=420,
        width=920,
        height=680,
    )


def run_double_reflector_eater_demo(ctx):
    life = Life()
    builder = CircuitBuilder(life, ctx.comp, cell_w=260, cell_h=260)

    builder.add_component(
        component_id="gun1",
        config_name="glider_gun_component",
        grid_x=0,
        grid_y=0,
        orientation=0,
        phase_override=1,
    )
    builder.add_component_aligned(
        component_id="refl1",
        config_name="reflector",
        source_id="gun1",
        source_port="out",
        target_port="in",
        distance=140,
        phase_override=1,
    )
    builder.add_component_aligned(
        component_id="refl2",
        config_name="reflector",
        source_id="refl1",
        source_port="out",
        target_port="in",
        distance=140,
        phase_override=1,
    )
    builder.add_component_aligned(
        component_id="eat1",
        config_name="eater_component",
        source_id="refl2",
        source_port="out",
        target_port="in",
        distance=120,
        phase_override=1,
    )

    for component_id in ["gun1", "refl1", "refl2", "eat1"]:
        node = builder.nodes[component_id]
        print(f"{component_id}: config={node.config_name}, orientation={node.orientation}")
        for port_name, port in node.ports.items():
            print(f"  {port_name}: kind={port.kind}, pos=({port.x},{port.y}), dir={port.direction}")

    print("Connection records:")
    for connection in builder.connections:
        print(connection)

    render_snapshot(
        ctx,
        life,
        title="gun_refl_refl_eater_setup",
        width=980,
        height=760,
    )
    render_animation(
        ctx,
        life,
        title="gun_refl_refl_eater_motion",
        steps=480,
        width=980,
        height=760,
    )
