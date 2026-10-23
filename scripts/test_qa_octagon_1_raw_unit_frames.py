"""Source-frame observability tests; never infer that a road is playable."""
import unittest
from PIL import Image
from qa_octagon_1_raw_unit_frames import source_coverage, render_contact_sheet


def sampler(points):
    return [(i, x, y, 0, 1) for i, (x, y) in enumerate(points)]


class SourceFrameCoverageTests(unittest.TestCase):
    def test_fully_visible_crop(self):
        self.assertEqual(source_coverage((100, 100, 284, 284)), 1)

    def test_edge_and_corner_are_partial(self):
        self.assertAlmostEqual(source_coverage((1008, 612, 1192, 796)), 0.5)
        self.assertAlmostEqual(source_coverage((-92, -92, 92, 92)), 0.25)

    def test_completely_outside_crop_has_no_evidence(self):
        self.assertEqual(source_coverage((1200, 900, 1384, 1084)), 0)

    def test_invalid_crop_rejected(self):
        for box in ((1, 1, 1, 4), (2, 4, 3, 2), (1, 2, 3, "4")):
            with self.subTest(box=box), self.assertRaises(ValueError):
                source_coverage(box)

    def test_contact_sheet_marks_partial_frames_without_approving(self):
        source = Image.new("RGB", (1100, 842), (72, 101, 45))
        routes = {"east_candidate": [[600, 500], [1100, 704]],
                  "south_candidate": [[500, 500], [315, 842]]}
        sheet, frames = render_contact_sheet(source, routes, sampler,
                                            fractions=(0, 1), radius=92)
        self.assertEqual(sheet.size, (368, 424))
        self.assertEqual(len(frames), 4)
        self.assertTrue(frames[0]["crop_fully_in_source"])
        self.assertEqual(frames[0]["source_pixel_coverage_fraction"], 1)
        self.assertFalse(frames[1]["candidate_center_in_source"])
        self.assertTrue(frames[1]["source_padding_present"])
        self.assertFalse(frames[3]["candidate_center_in_source"])
        self.assertTrue(frames[3]["source_padding_present"])
        self.assertEqual(sheet.getpixel((184, 0)), (255, 85, 85))
        self.assertEqual(source.getpixel((600, 500)), (72, 101, 45))

    def test_invalid_radius_and_fraction_rejected(self):
        im = Image.new("RGB", (1100, 842))
        for bad in (0, 20.5, True):
            with self.subTest(radius=bad), self.assertRaises(ValueError):
                render_contact_sheet(im, {"r": [[0, 0], [1, 1]]}, sampler, radius=bad)
        with self.assertRaises(ValueError):
            render_contact_sheet(im, {"r": [[0, 0], [1, 1]]}, sampler,
                                 fractions=(float("nan"),))


if __name__ == "__main__":
    unittest.main()
