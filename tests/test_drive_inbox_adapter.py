import unittest
from tools.drive_inbox_adapter import plan_drive_inbox_item

SONG = "https://suno.com/song/be108fa8-2efa-4aea-b32d-22f60b8e78fb"
SOURCE = {"id":"synthetic-source-id","title":"already-exported.mp3","mime_type":"audio/mpeg","parent_ids":["synthetic-inbox-folder-id"]}

class DriveInboxAdapterTests(unittest.TestCase):
    def plan(self, item=None, confirmed=True, existing=None):
        return plan_drive_inbox_item(item if item is not None else SOURCE, SONG,
            "Static Riot","Nobody Gets Close to You",
            official_export_confirmed=confirmed,target_existing_names=existing or [])

    def test_valid_preexisting_source_generates_readonly_plan(self):
        plan=self.plan()
        self.assertEqual(plan["destination_filename"], "Static Riot - Nobody Gets Close to You.mp3")
        self.assertEqual(plan["source_drive_id"],"synthetic-source-id")
        self.assertTrue(plan["preserve_source"])
        self.assertTrue(plan["requires_raw_file_sha256_before_and_after_upload"])
        self.assertFalse(plan["transferred"])

    def test_requires_official_export_confirmation(self):
        with self.assertRaises(ValueError):self.plan(confirmed=False)

    def test_rejects_destination_duplicate(self):
        with self.assertRaises(ValueError):self.plan(existing=["static riot - nobody gets close to you.mp3"])

    def test_rejects_wrong_mime(self):
        with self.assertRaises(ValueError):self.plan(item={**SOURCE,"mime_type":"text/plain"})

    def test_rejects_missing_parent(self):
        with self.assertRaises(ValueError):self.plan(item={**SOURCE,"parent_ids":[]})

    def test_rejects_source_already_in_destination(self):
        with self.assertRaises(ValueError):self.plan(item={**SOURCE,"parent_ids":["11xkA5Hc2tqQhYX8tu2HgGZu5rKR_Q62k"]})

if __name__ == "__main__":unittest.main()
