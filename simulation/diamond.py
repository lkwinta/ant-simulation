import numpy as np
import matplotlib.pyplot as plt


def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def get_diamond_mask(W: int, H: int):
    cx, cy = W // 2, H // 2
    s = min(W, H)

    # -----------------------------
    # SIZE-DEPENDENT PARAMETERS
    # -----------------------------
    room_margin = max(2, int(0.05 * s))
    room_w      = clamp(int(0.20 * W), 10, W // 3)
    room_h      = clamp(int(0.55 * H), 12, H - 2*room_margin)

    diamond_a   = clamp(int(0.20 * s), 8, s // 2 - 2)  # diamond "radius"
    diamond_corridor_half = clamp(int(0.04 * s), 2, diamond_a // 3)

    # tunnel thickness: keep consistent with diamond corridor thickness
    tunnel_half = clamp(diamond_corridor_half, 2, max(2, s // 10))

    # make tunnels long enough to reach the diamond comfortably
    tunnel_len = int(0.60 * W)

    wall_mask = np.ones((W, H), dtype=bool)

    # -----------------------------
    # DIAMOND CORRIDOR (ring)
    # -----------------------------
    inner_a = diamond_a - (2 * diamond_corridor_half + 1)
    if inner_a < 0:
        raise ValueError("diamond_corridor_half is too large for diamond_a")

    for x in range(W):
        for y in range(H):
            d = abs(x - cx) + abs(y - cy)
            in_outer = d <= diamond_a
            in_inner = d <= inner_a
            if in_outer and not in_inner:
                wall_mask[x, y] = False  # free space (corridor)

    # -----------------------------
    # ROOMS (free rectangles)
    # -----------------------------
    left_x0  = room_margin
    left_x1  = room_margin + room_w
    right_x1 = W - room_margin
    right_x0 = right_x1 - room_w

    room_y0 = cy - room_h // 2
    room_y1 = room_y0 + room_h

    wall_mask[left_x0:left_x1, room_y0:room_y1] = False
    wall_mask[right_x0:right_x1, room_y0:room_y1] = False

    # -----------------------------
    # TUNNELS (free rectangles) - longer and parameterized
    # -----------------------------
    # where does the diamond touch the horizontal axis?

    # where does the diamond touch the horizontal axis?
    diamond_left_tip  = cx - diamond_a
    diamond_right_tip = cx + diamond_a

    # "ports" where the tunnel should meet the diamond for given tunnel thickness
    # shift inward by tunnel_half to avoid missing the diamond at y = cy +/- tunnel_half
    left_port_x  = diamond_left_tip  + tunnel_half
    right_port_x = diamond_right_tip - tunnel_half

    # left tunnel: from left room right edge towards diamond port
    left_tunnel_x0 = left_x1
    left_tunnel_x1 = min(left_port_x + 1, left_tunnel_x0 + tunnel_len)  # +1 because slice end is exclusive

    # right tunnel: from diamond port towards right room left edge
    right_tunnel_x1 = right_x0
    right_tunnel_x0 = max(right_port_x, right_tunnel_x1 - tunnel_len)

    tunnel_y0 = cy - tunnel_half
    tunnel_y1 = cy + tunnel_half + 1  # +1 because slicing end is exclusive

    wall_mask[left_tunnel_x0:left_tunnel_x1, tunnel_y0:tunnel_y1] = False
    wall_mask[right_tunnel_x0:right_tunnel_x1, tunnel_y0:tunnel_y1] = False

    return wall_mask


if __name__ == "__main__":
    W, H = 300, 200

    wall_mask = get_diamond_mask(W, H)

    plt.figure(figsize=(12, 8))
    plt.imshow(wall_mask.T, cmap="gray", origin="lower")  # transpose for nicer x/y orientation
    plt.title("Wall Mask")
    plt.axis("off")
    plt.show()