import numpy as np
import matplotlib.pyplot as plt

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def carve_disk(free, cx, cy, radius):
    W, H = free.shape
    x0 = max(0, int(cx - radius - 1)); x1 = min(W, int(cx + radius + 2))
    y0 = max(0, int(cy - radius - 1)); y1 = min(H, int(cy + radius + 2))
    rr = radius * radius
    for x in range(x0, x1):
        for y in range(y0, y1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= rr:
                free[x, y] = True

def carve_segment(free, p0, p1, half_width):
    x0, y0 = p0; x1, y1 = p1
    W, H = free.shape

    xmin = int(max(0, min(x0, x1) - half_width - 2))
    xmax = int(min(W - 1, max(x0, x1) + half_width + 2))
    ymin = int(max(0, min(y0, y1) - half_width - 2))
    ymax = int(min(H - 1, max(y0, y1) + half_width + 2))

    vx, vy = (x1 - x0), (y1 - y0)
    vv = vx * vx + vy * vy
    if vv == 0:
        carve_disk(free, x0, y0, half_width)
        return

    hw2 = half_width * half_width
    for x in range(xmin, xmax + 1):
        for y in range(ymin, ymax + 1):
            wx, wy = (x - x0), (y - y0)
            t = (wx * vx + wy * vy) / vv
            if t < 0:
                px, py = x0, y0
            elif t > 1:
                px, py = x1, y1
            else:
                px, py = x0 + t * vx, y0 + t * vy

            dx, dy = x - px, y - py
            if dx * dx + dy * dy <= hw2:
                free[x, y] = True

def carve_polyline(free, pts, half_width):
    for a, b in zip(pts[:-1], pts[1:]):
        carve_segment(free, a, b, half_width)
    for (x, y) in pts:
        carve_disk(free, x, y, half_width)

def build_double_diamond_mask(W, H, r=1.4):
    # Expect W:H approx 3:1
    cx, cy = W // 2, H // 2
    s = min(W, H)

    # --- thickness / sizes (proportional to H mostly, because it's "thin") ---
    corridor_half = clamp(int(0.05 * H), 2, max(2, H // 8))

    room_margin = max(2, int(0.04 * H))
    room_w = clamp(int(0.12 * W), 12, W // 4)        # room width scales with W
    room_h = clamp(int(0.70 * H), 12, H - 2*room_margin)

    # Vertical offsets: short is a "diamond-like" branch, long is detour
    short_h = clamp(int(0.22 * H), 5, H // 2 - corridor_half - 2)
    long_h = clamp(int(short_h * r), short_h, H // 2 - corridor_half - 2)

    # --- usable horizontal budget between rooms ---
    usable_x = W - 2 * (room_margin + room_w)
    if usable_x < 30:
        raise ValueError("Map too small for double diamond with given room sizes.")

    # Allocate widths: tunnel | module | bridge | module | tunnel
    # Choose ratios that behave well for 3:1
    tunnel_L = int(0.16 * usable_x)
    bridge_L = int(0.08 * usable_x)
    module_L = (usable_x - 2*tunnel_L - bridge_L) // 2

    # Safety clamps
    tunnel_L = clamp(tunnel_L, 6, usable_x // 3)
    bridge_L = clamp(bridge_L, 4, usable_x // 4)
    module_L = clamp(module_L, 12, usable_x)

    # Recompute if clamping changed things
    total = 2*tunnel_L + 2*module_L + bridge_L
    if total > usable_x:
        # shrink tunnels first
        overflow = total - usable_x
        shrink = min(overflow // 2 + 1, tunnel_L - 6)
        tunnel_L -= shrink
        total = 2*tunnel_L + 2*module_L + bridge_L

    # --- start with all walls ---
    free = np.zeros((W, H), dtype=bool)

    # --- rooms ---
    left_x0 = room_margin
    left_x1 = room_margin + room_w
    right_x1 = W - room_margin
    right_x0 = right_x1 - room_w

    room_y0 = clamp(cy - room_h // 2, 0, H - room_h)
    room_y1 = room_y0 + room_h

    free[left_x0:left_x1, room_y0:room_y1] = True
    free[right_x0:right_x1, room_y0:room_y1] = True

    # --- module x positions ---
    m1_left = left_x1 + tunnel_L
    m1_right = m1_left + module_L
    m2_left = m1_right + bridge_L
    m2_right = m2_left + module_L

    # carve straight connections (rooms <-> modules and module1 <-> module2)
    carve_segment(free, (left_x1, cy), (m1_left, cy), corridor_half)
    carve_segment(free, (m1_right, cy), (m2_left, cy), corridor_half)
    carve_segment(free, (m2_right, cy), (right_x0, cy), corridor_half)

    def module_paths(xL, xR, short_is_top: bool):
        xM = (xL + xR) // 2
        if short_is_top:
            top_h, bot_h = short_h, long_h
        else:
            top_h, bot_h = long_h, short_h

        left = (xL, cy)
        right = (xR, cy)
        top = (xM, cy + top_h)
        bot = (xM, cy - bot_h)
        return [left, top, right], [left, bot, right]

    # Module 1: short on TOP
    p1_top, p1_bot = module_paths(m1_left, m1_right, short_is_top=True)
    carve_polyline(free, p1_top, corridor_half)
    carve_polyline(free, p1_bot, corridor_half)

    # Module 2: mirror (short on BOTTOM)
    p2_top, p2_bot = module_paths(m2_left, m2_right, short_is_top=False)
    carve_polyline(free, p2_top, corridor_half)
    carve_polyline(free, p2_bot, corridor_half)

    wall_mask = ~free
    return wall_mask

if __name__ == "__main__":
    W, H = 300, 200   # 3:1
    r = 1
    wall_mask = build_double_diamond_mask(W, H, r=r)

    plt.figure(figsize=(12, 8))
    plt.imshow(wall_mask.T, cmap="gray", origin="lower")
    plt.title(f"Double-diamond (W={W}, H={H}, r={r})")
    plt.axis("off")
    plt.show()