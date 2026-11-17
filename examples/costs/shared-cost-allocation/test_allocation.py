import unittest

from allocation import HERE, allocate, read_rows, split_cents


class AllocationTests(unittest.TestCase):
    def rows(self, driver_file="drivers.csv"):
        return (read_rows(HERE / "line-items.csv", {"id", "kind", "owner", "pool", "cents"}),
                read_rows(HERE / driver_file, {"pool", "owner", "units"}))

    def test_fixture_reconciles_and_keeps_unknown_visible(self):
        owners, bill = allocate(*self.rows())
        self.assertEqual(bill, 16000)
        self.assertEqual(owners, {"Repair": 9450, "Sales": 5550, "Unallocated": 1000})

    def test_dispute_changes_ownership_without_changing_bill(self):
        original, bill = allocate(*self.rows())
        revised, revised_bill = allocate(*self.rows("drivers-dispute.csv"))
        self.assertEqual((revised_bill, revised["Platform"], revised["Repair"]), (bill, 750, 8700))
        self.assertEqual(sum(revised.values()), sum(original.values()))

    def test_odd_cent_tie_break_is_deterministic(self):
        self.assertEqual(split_cents(1, {"Sales": 1, "Repair": 1}), {"Sales": 0, "Repair": 1})

    def test_missing_driver_or_duplicate_line_is_rejected(self):
        lines, drivers = self.rows()
        with self.assertRaises(ValueError):
            allocate(lines, [row for row in drivers if row["pool"] != "AI"])
        with self.assertRaises(ValueError):
            allocate(lines + [dict(lines[0])], drivers)

    def test_bad_units_or_unallocated_as_receiver_is_rejected(self):
        lines, drivers = self.rows()
        with self.assertRaises(ValueError):
            allocate(lines, drivers + [{"pool": "Network", "owner": "Unallocated", "units": "1"}])
        with self.assertRaises(ValueError):
            allocate(lines, [{**drivers[0], "units": "0"}] + drivers[1:])


if __name__ == "__main__":
    unittest.main()
