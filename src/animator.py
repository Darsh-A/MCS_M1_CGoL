def animate_life(
    life,
    steps=200,
    width=100,
    height=100,
    save="output.mp4",
    speed=1.0,
    show_stream=False,
    stream_decay=0.93,
    stream_intensity=0.35,
    show_grid=False,
    grid_spacing=5,
    grid_alpha=0.25,
    grid_color="#7a7a7a",
    highlight_regions=None,
    step_callback=None,
):
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from pathlib import Path

    target = Path(save)
    target.parent.mkdir(parents=True, exist_ok=True)

    x_offset = width // 2
    y_offset = height // 2

    fig, ax = plt.subplots()
    trail = np.zeros((height, width), dtype=float)
    highlight_regions = highlight_regions or []

    def _build_frame():
        live_grid = np.zeros((height, width), dtype=float)

        for x, y in life.alive:
            gx = x + x_offset
            gy = y + y_offset
            if 0 <= gx < width and 0 <= gy < height:
                live_grid[gy, gx] = 1.0

        if show_stream:
            trail[:] *= stream_decay
            trail[:] = np.maximum(trail, live_grid)
        else:
            trail.fill(0.0)

        frame = np.zeros((height, width, 3), dtype=float)
        if show_stream:
            stream_layer = np.clip(trail * stream_intensity, 0.0, 1.0)
            frame[:, :, 0] = stream_layer
            frame[:, :, 1] = stream_layer
            frame[:, :, 2] = stream_layer

        for region in highlight_regions:
            xmin = int(region["xmin"]) + x_offset
            xmax = int(region["xmax"]) + x_offset
            ymin = int(region["ymin"]) + y_offset
            ymax = int(region["ymax"]) + y_offset
            alpha = float(region.get("alpha", 0.18))
            color = region.get("color", (0.0, 0.8, 0.0))
            r, g, b = color

            x0 = max(0, min(width - 1, xmin))
            x1 = max(0, min(width - 1, xmax))
            y0 = max(0, min(height - 1, ymin))
            y1 = max(0, min(height - 1, ymax))
            if x0 > x1 or y0 > y1:
                continue

            frame[y0 : y1 + 1, x0 : x1 + 1, 0] = np.maximum(
                frame[y0 : y1 + 1, x0 : x1 + 1, 0], r * alpha
            )
            frame[y0 : y1 + 1, x0 : x1 + 1, 1] = np.maximum(
                frame[y0 : y1 + 1, x0 : x1 + 1, 1], g * alpha
            )
            frame[y0 : y1 + 1, x0 : x1 + 1, 2] = np.maximum(
                frame[y0 : y1 + 1, x0 : x1 + 1, 2], b * alpha
            )

        live_mask = live_grid > 0
        frame[live_mask] = (1.0, 1.0, 1.0)
        return frame

    def _draw_frame(frame):
        ax.clear()
        ax.imshow(frame, origin="lower", interpolation="nearest")
        ax.set_xlim(-0.5, width - 0.5)
        ax.set_ylim(-0.5, height - 0.5)

        if show_grid:
            xticks = np.arange(0, width, grid_spacing)
            yticks = np.arange(0, height, grid_spacing)
            ax.set_xticks(xticks)
            ax.set_yticks(yticks)
            ax.grid(True, color=grid_color, alpha=grid_alpha, linewidth=0.3)
        else:
            ax.set_xticks([])
            ax.set_yticks([])

        ax.set_facecolor("black")

    suffix = target.suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg"}:
        if step_callback is not None:
            step_callback(life, 0)
        frame = _build_frame()
        _draw_frame(frame)
        fig.savefig(target, dpi=200, bbox_inches="tight")
        plt.close(fig)
        return

    base_fps = 20
    fps = max(1, int(round(base_fps * float(speed))))
    if suffix == ".gif":
        writer = animation.PillowWriter(fps=fps)
    else:
        writer = animation.FFMpegWriter(fps=fps)

    with writer.saving(fig, str(target), dpi=200):
        for t in range(steps):
            if step_callback is not None:
                step_callback(life, t)
            frame = _build_frame()
            _draw_frame(frame)
            writer.grab_frame()
            life.step()

    plt.close(fig)
