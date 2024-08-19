import quaternion

import rclpy
from rclpy.node import Node

from std_msgs.msg import Empty, Int8
from sensor_msgs.msg import Image, CameraInfo


class ImageRelayNode(Node):
    def __init__(self) -> None:
        super().__init__("image_relay_node")

        self.declare_parameter("num_cameras", 10)
        num_cameras = (
            self.get_parameter("num_cameras").get_parameter_value().integer_value
        )

        self._image_pubs = [
            self.create_publisher(Image, f"cam_{i}/image_color", 10)
            for i in range(num_cameras)
        ]

        self._camera_info_pubs = [
            self.create_publisher(CameraInfo, f"cam_{i}/camera_info", 10)
            for i in range(num_cameras)
        ]
        self._camera_data = {}

        self._last_image = None
        self._last_camera_info = None

        self._publish_latched_sub = self.create_subscription(
            Empty, "/publish_latched", self._publish_latched_cb, 10
        )

        self._clear_buffer_sub = self.create_subscription(
            Empty, "/clear_buffer", self._clear_buffer_cb, 10
        )

        self._save_img_sub = self.create_subscription(
            Int8, "/save_image", self._save_img_cb, 10
        )

        self._image_sub = self.create_subscription(
            Image, "/camera/color/image_raw", self._image_cb, 10
        )

        self._camera_info_sub = self.create_subscription(
            CameraInfo, "/camera/color/camera_info", self._camera_info_cb, 10
        )

        self.get_logger().info("Node initialized.")

    def _image_cb(self, msg: Image) -> None:
        self._last_image = msg

    def _camera_info_cb(self, msg: CameraInfo) -> None:
        self._last_camera_info = msg

    def _publish_latched_cb(self, _: Empty) -> None:
        if len(self._camera_data) == 0:
            self.get_logger().warn(f"Buffer was empty, nothing published!")
            return

        now = self.get_clock().now().to_msg()
        for cam_num, (image, camera_info) in self._camera_data.items():
            image.header.stamp = now
            self._image_pubs[cam_num].publish(image)

            camera_info.header.stamp = now
            self._camera_info_pubs[cam_num].publish(camera_info)

        self.get_logger().warn(f"{len(self._camera_data)} images were published!")

    def _save_img_cb(self, msg: Int8) -> None:
        if self._last_camera_info is None and self._last_image is None:
            self.get_logger().error("No image or camera info received failed to save!")
            return
        self._camera_data[msg.data] = (self._last_image, self._last_camera_info)
        self.get_logger().info(
            f"Current images saved for camera with topic `/cam_{msg.data}`"
        )

    def _clear_buffer_cb(self, _: Empty) -> None:
        self._camera_data = {}
        self.get_logger().info(f"Buffer was cleared")


def main(args=None):
    rclpy.init(args=args)
    image_relay_node = ImageRelayNode()
    rclpy.spin(image_relay_node)
    image_relay_node.destroy_node()
    rclpy.try_shutdown()


if __name__ == "__main__":
    main()
