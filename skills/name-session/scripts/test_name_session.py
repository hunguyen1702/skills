import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("namer", Path(__file__).with_name("name_session.py"))
namer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(namer)


class NamerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "session.jsonl"

    def write(self, entries):
        self.path.write_text("".join(json.dumps(e) + "\n" for e in entries))

    def test_filters_tools_and_injected_text(self):
        self.write([
            {"type": "user", "message": {"role": "user", "content": "<system-reminder>secret</system-reminder>Build a namer"}},
            {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "content": "noise"}]}},
            {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "thinking", "thinking": "hidden"}, {"type": "text", "text": "Done"}]}},
        ])
        self.assertEqual(namer.digest("claude", self.path), "user: Build a namer\nassistant: Done")

    def test_slash_commands_in_either_tag_order(self):
        self.write([
            {"type": "user", "message": {"role": "user", "content": "<command-name>/clear</command-name>\n<command-message>clear</command-message>\n<command-args></command-args>"}},
            {"type": "user", "message": {"role": "user", "content": "<command-name>/scout</command-name>\n<command-message>scout</command-message>\n<command-args>Ollama context limits</command-args>"}},
            {"type": "user", "message": {"role": "user", "content": "<command-message>pr</command-message>\n<command-name>/pr</command-name>"}},
        ])
        self.assertEqual(namer.digest("claude", self.path), "user: /scout Ollama context limits\nuser: /pr")

    def test_all_agent_formats(self):
        for agent, entry in [
            ("codex", {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "Fix login"}]}}),
            ("pi", {"type": "message", "message": {"role": "user", "content": "Fix login"}}),
        ]:
            self.write([entry])
            self.assertEqual(namer.digest(agent, self.path), "user: Fix login")

    def test_utf8_budget_keeps_first_and_recent_users(self):
        self.write([{"type": "message", "message": {"role": "user", "content": str(i) + "đ" * 500}} for i in range(500)])
        digest = namer.digest("pi", self.path)
        self.assertLessEqual(len(digest.encode()), namer.BUDGET)
        self.assertIn("user: 0", digest)
        self.assertIn("user: 499", digest)

    def test_refuses_missing_or_ambiguous_identity(self):
        for env in ({}, {"PI_SESSION_FILE": "x", "CODEX_THREAD_ID": "y"}):
            with self.assertRaises(RuntimeError):
                namer.current_session(env)

    def test_pi_append_preserves_records(self):
        self.write([{"type": "session", "id": "sid"}, {"type": "message", "id": "leaf"}])
        before = self.path.read_bytes()
        namer.save_title("pi", "sid", self.path, "Name this session")
        self.assertTrue(self.path.read_bytes().startswith(before))
        last = list(namer.records(self.path))[-1]
        self.assertEqual(last["parentId"], "leaf")
        self.assertEqual(last["name"], "Name this session")

    def test_claude_append_and_sidecar(self):
        self.write([{"type": "user"}])
        namer.save_title("claude", "sid", self.path, "A useful title")
        self.assertEqual(list(namer.records(self.path))[-1]["customTitle"], "A useful title")
        self.assertEqual(json.loads((self.path.parent / "sid/custom-title.json").read_text())["customTitle"], "A useful title")

    def test_model_request_and_title_limit(self):
        from io import BytesIO
        response = BytesIO(json.dumps({"message": {"content": json.dumps({"title": "one two three four five six seven eight nine ten eleven"})}}).encode())
        with patch("urllib.request.OpenerDirector.open", return_value=response) as opened:
            title = namer.request_title("user: Build it", "local only")
        self.assertEqual(len(title.split()), 10)
        payload = json.loads(opened.call_args.args[0].data)
        self.assertEqual(payload["model"], "qwen2.5:3b")
        self.assertEqual(payload["format"]["required"], ["title"])


if __name__ == "__main__":
    unittest.main()
