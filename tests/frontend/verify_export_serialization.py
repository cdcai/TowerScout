"""Round-trip actual browser-export payloads through independent stdlib parsers."""

import csv
import io
import html
import json
from pathlib import Path
import subprocess
import unittest
import xml.etree.ElementTree as ET


class ExportSerialization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        script = Path(__file__).with_name("test_task105_export_downloads.js")
        cls.payload = json.loads(
            subprocess.check_output(
                ["node", str(script), "--serialization-fixture"], encoding="utf-8"
            )
        )

    def test_csv_preserves_fields_and_all_detection_rows(self):
        rows = list(
            csv.reader(io.StringIO(self.payload["csv"], newline=""), strict=True)
        )
        self.assertEqual(len(rows), 7)
        self.assertTrue(all(len(row) == 10 for row in rows))
        self.assertEqual(rows[0][7:10], ["address", "confidence", "source"])
        self.assertEqual(rows[1][7], self.payload["special"])
        self.assertEqual(rows[2][7], 'Manual "tower", café')
        self.assertEqual(rows[3][7], "Unknown")
        self.assertEqual(
            [row[9] for row in rows[1:]], ["ML", "Manual", "ML", "ML", "ML", "ML"]
        )
        self.assertEqual(rows[4][1], "false")
        self.assertEqual(rows[5][3], "false")
        self.assertEqual(rows[6][2], "false")
        self.assertEqual(rows[1][4:7], ["40.00000000", "-75.00000000", "0.0"])

    def test_kml_preserves_text_geometry_and_selection(self):
        root = ET.fromstring(self.payload["kml"])
        ns = {"k": "http://www.opengis.net/kml/2.2"}
        placemarks = root.findall("k:Document/k:Placemark", ns)
        self.assertEqual(len(placemarks), 3)
        expected = [self.payload["special"], 'Manual "tower", café', "Unknown Location"]
        for index, placemark in enumerate(placemarks):
            self.assertEqual(
                placemark.findtext("k:name", namespaces=ns), expected[index]
            )
            address = expected[index] if index < 2 else "Unknown"
            self.assertEqual(
                html.unescape(placemark.findtext("k:description", namespaces=ns)),
                f'P(0.90) at {address} {self.payload["metadata"]}',
            )
            self.assertEqual(
                placemark.findtext("k:Point/k:coordinates", namespaces=ns), "-75,40,300"
            )
            self.assertEqual(len(placemark.find("k:name", ns)), 0)
            self.assertEqual(len(placemark.find("k:description", ns)), 0)
            self.assertNotIn("<", placemark.findtext("k:description", namespaces=ns))


if __name__ == "__main__":
    unittest.main()
