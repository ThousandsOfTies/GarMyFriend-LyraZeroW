from __future__ import annotations

import csv
import importlib.util
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sources/gar-tools/composition"))
from product import Product


def rows(directory, table):
    with (directory / (table + ".csv")).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class HardwareGeneration(unittest.TestCase):
    def test_only_one_binding_is_authored_and_simulation_has_only_declared_differences(self):
        product = Product(ROOT).validate()
        self.assertEqual(ROOT / "hardware", product.hardware_for("physical"))
        for table in ("gpio", "spi"):
            self.assertEqual([ROOT / "hardware" / (table + ".csv")], list((ROOT / "hardware").rglob(table + ".csv")))
        before = {table: (product.hardware / (table + ".csv")).read_bytes() for table in ("gpio", "spi")}
        generated = product.hardware_for("simulation")
        self.assertEqual(ROOT / ".gar/hardware/simulation", generated)
        allowed = {(table, row["name"], field) for table, field in (("gpio", "debounce_us"), ("spi", "max_speed_hz"), ("spi", "sim"))
                   for row in rows(generated, table) if table != "gpio" or row["name"].startswith("encoder_")}
        differences = set()
        for table in ("gpio", "spi"):
            physical, simulated = rows(product.hardware, table), rows(generated, table)
            self.assertEqual([row["name"] for row in physical], [row["name"] for row in simulated])
            for original, derived in zip(physical, simulated):
                differences.update((table, original["name"], key) for key in original if original[key] != derived[key])
            self.assertEqual(before[table], (product.hardware / (table + ".csv")).read_bytes())
        self.assertEqual(allowed, differences)
        self.assertEqual(["1000"] * 3, [row["debounce_us"] for row in rows(product.hardware, "gpio") if row["name"].startswith("encoder_")])
        self.assertEqual(["0"] * 3, [row["debounce_us"] for row in rows(generated, "gpio") if row["name"].startswith("encoder_")])
        self.assertEqual("8000000", rows(product.hardware, "spi")[0]["max_speed_hz"])
        self.assertEqual("1000000", rows(generated, "spi")[0]["max_speed_hz"])

    def test_simulator_archive_contains_generated_profile_and_no_machine_credentials(self):
        spec = importlib.util.spec_from_file_location("product_vm", ROOT / "tools/vm.py")
        vm = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(vm)
        with tempfile.TemporaryDirectory() as temporary, patch.object(vm, "STATE", Path(temporary)):
            with tarfile.open(vm.archive(), "r:gz") as archive:
                names = archive.getnames()
                for name in ("gpio.csv", "spi.csv"):
                    member = ".gar/hardware/simulation/" + name
                    self.assertIn(member, names)
                    self.assertEqual((ROOT / member).read_bytes(), archive.extractfile(member).read())
                self.assertIn("product.json", names, "The launcher reads the generated profile path from composition")
                self.assertFalse(any(name.startswith((".gar/vm/", ".gar/device")) for name in names))
                manifest = json.load(archive.extractfile("product.json"))
                self.assertEqual(".gar/hardware/simulation", manifest["hardware"]["simulation"])


if __name__ == "__main__":
    unittest.main()
