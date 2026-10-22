import unittest
from PIL import Image
from scripts.audit_octagon_1_edge import boundary_status, crop_native


class EastEdgeAuditTests(unittest.TestCase):
    def test_exact_boundary_is_not_a_source_pixel(self):
        state = boundary_status((1100, 842), (1100, 704))
        self.assertTrue(state["endpoint_on_east_image_boundary"])
        self.assertFalse(state["endpoint_is_source_pixel"])
        self.assertFalse(state["production_ready"])
        self.assertFalse(state["neighbor_art_verified"])

    def test_last_real_pixel_is_not_a_neighbor(self):
        state = boundary_status((1100, 842), (1099, 704))
        self.assertTrue(state["endpoint_is_source_pixel"])
        self.assertFalse(state["endpoint_on_east_image_boundary"])
        self.assertFalse(state["neighbor_art_verified"])

    def test_native_crop_preserves_source_pixels_and_marks_missing_pixels(self):
        image = Image.new("RGB", (10, 8), (12, 34, 56))
        crop, bounds = crop_native(image, (10, 4), radius=3)
        self.assertEqual(crop.size, (6, 6))
        self.assertEqual(bounds, (7, 1, 10, 7))
        self.assertEqual(crop.getpixel((2, 3)), (12, 34, 56))
        self.assertEqual(crop.getpixel((3, 3)), (45, 45, 45))

    def test_invalid_crop_inputs_rejected(self):
        image = Image.new("RGB", (10, 8))
        with self.assertRaises(ValueError):
            crop_native(image, (10, 4), radius=0)
        with self.assertRaises(ValueError):
            crop_native(image, (10.5, 4))


if __name__ == "__main__":
    unittest.main()
