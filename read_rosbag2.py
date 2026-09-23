import numpy as np
import matplotlib.pyplot as plt
from mcap.reader import make_reader
from mcap_ros2.decoder import DecoderFactory

FIELD_TYPE_MAP = {
    1: (np.int8, "int8"),
    2: (np.uint8, "uint8"),
    3: (np.int16, "int16"),
    4: (np.uint16, "uint16"),
    5: (np.int32, "int32"),
    6: (np.uint32, "uint32"),
    7: (np.float32, "float32"),
    8: (np.float64, "float64"),
}

PLY_TYPE_MAP = {
    np.dtype("int8"): "char",
    np.dtype("uint8"): "uchar",
    np.dtype("int16"): "short",
    np.dtype("uint16"): "ushort",
    np.dtype("int32"): "int",
    np.dtype("uint32"): "uint",
    np.dtype("float32"): "float",
    np.dtype("float64"): "double",
}



def unpack_pointcloud2_full(msg):
    """
    Decodes XYZ and all scalar fields (intensity, ring, time, etc.)
    directly from raw bytes.
    """
    raw_buffer = bytes(msg.data)
    total_bytes = len(raw_buffer)

    if total_bytes == 0 or msg.point_step == 0:
        return None, None

    num_points = total_bytes // msg.point_step
    if num_points == 0:
        return None, None

    valid_len = num_points * msg.point_step
    records = np.frombuffer(raw_buffer[:valid_len], dtype=np.uint8).reshape(num_points, msg.point_step)

    # 1. Parse Fields Metadata
    fields = {}
    for f in msg.fields:
        np_type, _ = FIELD_TYPE_MAP.get(f.datatype, (np.float32, "float32"))
        itemsize = np.dtype(np_type).itemsize
        data_slice = records[:, f.offset: f.offset + itemsize].copy().view(np_type).flatten()
        fields[f.name] = data_slice

    if not all(k in fields for k in ("x", "y", "z")):
        return None, None

    # Filter out NaNs/Infs from coordinates
    pts = np.column_stack((fields["x"].astype(np.float32),
                           fields["y"].astype(np.float32),
                           fields["z"].astype(np.float32)))
    valid_mask = np.isfinite(pts).all(axis=1)

    pts = pts[valid_mask]
    # Filter all scalars with the same mask
    scalars = {k: v[valid_mask] for k, v in fields.items() if k not in ("x", "y", "z")}

    return pts, scalars


def save_to_cloudcompare_ply(filename, points, scalars):
    """
    Writes points and all scalar fields into an efficient binary PLY.
    """
    num_points = len(points)

    # Define structured dtype for binary writing
    dtype_fields = [("x", "<f4"), ("y", "<f4"), ("z", "<f4")]
    ply_header_props = [
        "property float x",
        "property float y",
        "property float z"
    ]

    for name, array in scalars.items():
        elem_dtype = array.dtype
        ply_t = PLY_TYPE_MAP.get(elem_dtype, "float")
        ply_header_props.append(f"property {ply_t} {name}")
        dtype_fields.append((name, elem_dtype))

    header = (
            "ply\n"
            "format binary_little_endian 1.0\n"
            f"element vertex {num_points}\n"
            + "\n".join(ply_header_props)
            + "\nend_header\n"
    )

    # Pack data
    structured_data = np.zeros(num_points, dtype=np.dtype(dtype_fields))
    structured_data["x"] = points[:, 0]
    structured_data["y"] = points[:, 1]
    structured_data["z"] = points[:, 2]

    for name, array in scalars.items():
        structured_data[name] = array

    with open(filename, "wb") as f:
        f.write(header.encode("ascii"))
        f.write(structured_data.tobytes())

    print(f"Successfully saved {num_points:,} points with fields {list(scalars.keys())} to '{filename}'.")


def main():

    name = "my_lidar_bag6"
    mcap_file ="rosbags/" + name + "/" + name + "_0.mcap"
    topic = "/unilidar/cloud"
    output_ply = "combined_unilidar" + name + ".ply"

    all_points = []
    all_scalars = {}

    frame_count = 0
    frames2combine = 15
    print(f"Reading {mcap_file}...")
    with open(mcap_file, "rb") as f:
        reader = make_reader(f, decoder_factories=[DecoderFactory()])
        for schema, channel, message, ros_msg in reader.iter_decoded_messages():
            if channel.topic == topic:
                frame_count += 1
                pts, scalars = unpack_pointcloud2_full(ros_msg)
                if pts is not None and len(pts) > 0:
                    all_points.append(pts)
                    for k, v in scalars.items():
                        all_scalars.setdefault(k, []).append(v)
                if frame_count == frames2combine:
                    break

    if not all_points:
        print("No valid points found.")
        return

    print(f"Total Frames used: {frame_count}")
    combined_pts = np.vstack(all_points)
    combined_scalars = {k: np.concatenate(v) for k, v in all_scalars.items()}

    # Save to PLY
    save_to_cloudcompare_ply(output_ply, combined_pts, combined_scalars)

    # Optional quick plot with intensity coloring if available
    color_by = combined_scalars.get("intensity", combined_pts[:, 2])
    plt.figure(figsize=(9, 6))
    plt.scatter(combined_pts[::10, 0], combined_pts[::10, 1], c=color_by[::10], cmap="turbo", s=0.5)
    plt.colorbar(label="Intensity" if "intensity" in combined_scalars else "Z")
    plt.title("LiDAR Top-Down View")
    plt.axis("equal")
    plt.show()


if __name__ == "__main__":
    main()