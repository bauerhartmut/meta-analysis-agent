"""
Unit tests for the LLM engine (research_agent/llm/engine.py).

These tests exercise the retry/backoff, JSON-parsing and concurrency logic of the
engine WITHOUT a running Ollama server: the aiohttp session is replaced with a
scripted fake that returns responses (or raises connection errors) on demand.

Runs fully offline and touches code outside the in-flight package scopes
(store.py / database.py / orchestrator.py / search.py / agents/ are NOT touched).
"""

import json
import sys
import asyncio
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import aiohttp

from research_agent.llm.engine import LLMEngine, unwrap_json_list
from research_agent.research.extractor import ContentExtractor
from research_agent.dashboard.server import _AsyncRunner


# ---------------------------------------------------------------------------
# Fake HTTP plumbing
# ---------------------------------------------------------------------------

class _FakeLoop:
    def is_running(self):
        return True


class _FakeResponse:
    def __init__(self, status=200, json_payload=None, text=""):
        self.status = status
        self._json = json_payload
        self._text = text
        self.headers = {}

    async def json(self):
        return self._json

    async def text(self):
        return self._text


class _RespContext:
    """Async-context manager standing in for aiohttp's _RequestContextManager."""

    def __init__(self, result):
        self.result = result

    async def __aenter__(self):
        if isinstance(self.result, BaseException):
            raise self.result
        return self.result

    async def __aexit__(self, *exc):
        return False


class _FakeSession:
    def __init__(self, responder):
        self.responder = responder
        self.closed = False
        self._loop = _FakeLoop()

    def post(self, *args, **kwargs):
        return _RespContext(self.responder(_FakeResponse(status=500, text="unscripted")))

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    async def close(self):
        self.closed = True


class _RecordingSession(_FakeSession):
    """Fake session that also records the URL/headers/payload of each request."""

    def __init__(self, responder):
        super().__init__(responder)
        self.calls = []

    def post(self, url=None, **kwargs):
        self.calls.append({"url": url, "headers": kwargs.get("headers"), "json": kwargs.get("json")})
        return super().post(url, **kwargs)

    def get(self, url=None, **kwargs):
        self.calls.append({"url": url, "headers": kwargs.get("headers"), "json": None})
        return _RespContext(self.responder(_FakeResponse(status=500, text="unscripted")))


def _make_engine(responses, session_cls=_FakeSession):
    """Build an LLMEngine whose HTTP session is scripted to return `responses`.

    `responses` may contain _FakeResponse instances or Exception instances
    (which the fake session raises, simulating connection errors/timeouts).
    """
    queue = list(responses)

    def responder(fallback):
        if queue:
            return queue.pop(0)
        return fallback

    engine = LLMEngine()
    session = session_cls(responder)

    async def ensure():
        return session

    engine._ensure_session = ensure
    engine._min_interval = 0.0
    engine._compute_delay = lambda attempt, retry_after=None: 0.0
    # Pin the backend: the real .env may select TUDaGPT or a GPU server, but
    # these tests describe the Ollama path.
    engine._backend = "ollama"
    return engine, session


def _ok(content):
    return _FakeResponse(status=200, json_payload={"message": {"content": content}})


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestChatRetry(unittest.TestCase):
    """chat() retry/backoff and error handling."""

    def test_success(self):
        async def _run():
            llm, _ = _make_engine([_ok("hello world")])
            r = await llm.chat([{"role": "user", "content": "hi"}])
            await llm.close()
            return r
        self.assertEqual(asyncio.run(_run()), "hello world")

    def test_retries_on_429_then_success(self):
        async def _run():
            llm, _ = _make_engine([
                _FakeResponse(status=429, text="rate limited"),
                _ok("second attempt"),
            ])
            r = await llm.chat([{"role": "user", "content": "hi"}])
            await llm.close()
            return r
        self.assertEqual(asyncio.run(_run()), "second attempt")

    def test_retries_on_server_error_then_success(self):
        async def _run():
            llm, _ = _make_engine([
                _FakeResponse(status=500, text="boom"),
                _ok("recovered"),
            ])
            r = await llm.chat([{"role": "user", "content": "hi"}])
            await llm.close()
            return r
        self.assertEqual(asyncio.run(_run()), "recovered")

    def test_error_marker_after_retries_exhausted(self):
        async def _run():
            llm, _ = _make_engine([
                _FakeResponse(status=500, text="a"),
                _FakeResponse(status=500, text="b"),
                _FakeResponse(status=500, text="c"),
            ])
            r = await llm.chat([{"role": "user", "content": "hi"}])
            await llm.close()
            return r
        result = asyncio.run(_run())
        self.assertTrue(result.startswith("[ERROR:"), result)

    def test_connection_error_retries(self):
        async def _run():
            llm, _ = _make_engine([
                aiohttp.ClientConnectionError("broken pipe"),
                _ok("after reconnect"),
            ])
            r = await llm.chat([{"role": "user", "content": "hi"}])
            await llm.close()
            return r
        self.assertEqual(asyncio.run(_run()), "after reconnect")


class TestFailureTracking(unittest.TestCase):
    """The consecutive-failure counter the orchestrator watchdog reads."""

    def setUp(self):
        LLMEngine.reset_failure_counter()

    def tearDown(self):
        LLMEngine.reset_failure_counter()

    def _failing_engine(self):
        return _make_engine([
            _FakeResponse(status=500, text="a"),
            _FakeResponse(status=500, text="b"),
            _FakeResponse(status=500, text="c"),
        ])[0]

    def test_failed_calls_are_counted_in_a_row(self):
        async def _run():
            for _ in range(3):
                llm = self._failing_engine()
                await llm.chat([{"role": "user", "content": "hi"}])
                await llm.close()

        asyncio.run(_run())
        self.assertEqual(LLMEngine.consecutive_failures(), 3)
        self.assertIn("ERROR", LLMEngine.last_failure())

    def test_a_successful_call_resets_the_counter(self):
        async def _run():
            for _ in range(2):
                llm = self._failing_engine()
                await llm.chat([{"role": "user", "content": "hi"}])
                await llm.close()
            good, _ = _make_engine([_ok("fine")])
            await good.chat([{"role": "user", "content": "hi"}])
            await good.close()

        asyncio.run(_run())
        self.assertEqual(LLMEngine.consecutive_failures(), 0)
        self.assertEqual(LLMEngine.last_failure(), "")

    def test_chat_json_error_response_counts_once(self):
        async def _run():
            llm = self._failing_engine()
            result = await llm.chat_json([{"role": "user", "content": "hi"}])
            await llm.close()
            return result

        self.assertIsNone(asyncio.run(_run()))
        # chat_json stops on the error marker instead of retrying it.
        self.assertEqual(LLMEngine.consecutive_failures(), 1)

    def test_json_parse_failures_are_not_backend_failures(self):
        async def _run():
            llm, _ = _make_engine([_ok("not json"), _ok("still not json"), _ok("nope")])
            result = await llm.chat_json([{"role": "user", "content": "hi"}])
            await llm.close()
            return result

        self.assertIsNone(asyncio.run(_run()))
        self.assertEqual(LLMEngine.consecutive_failures(), 0)

    def test_reset_clears_counter_and_error(self):
        LLMEngine._track_result("[ERROR: backend gone]")
        self.assertEqual(LLMEngine.consecutive_failures(), 1)
        LLMEngine.reset_failure_counter()
        self.assertEqual(LLMEngine.consecutive_failures(), 0)
        self.assertEqual(LLMEngine.last_failure(), "")


class TestChatJson(unittest.TestCase):
    """chat_json() JSON extraction robustness."""

    def test_object(self):
        async def _run():
            llm, _ = _make_engine([_ok('{"a": 1, "b": "x"}')])
            r = await llm.chat_json([{"role": "user", "content": "q"}])
            await llm.close()
            return r
        self.assertEqual(asyncio.run(_run()), {"a": 1, "b": "x"})

    def test_array(self):
        async def _run():
            llm, _ = _make_engine([_ok('[{"id": 1}, {"id": 2}]')])
            r = await llm.chat_json([{"role": "user", "content": "q"}])
            await llm.close()
            return r
        self.assertEqual(asyncio.run(_run()), [{"id": 1}, {"id": 2}])

    def test_markdown_fenced_object(self):
        # qwen3 in thinking mode often wraps JSON in a ```json fence.
        raw = '```json\n{"evidence_type": "supports", "strength": 0.8}\n```'
        async def _run():
            llm, _ = _make_engine([_ok(raw)])
            r = await llm.chat_json([{"role": "user", "content": "q"}])
            await llm.close()
            return r
        self.assertEqual(asyncio.run(_run()),
                         {"evidence_type": "supports", "strength": 0.8})

    def test_json_in_prose(self):
        # JSON embedded in surrounding prose -> regex fallback extraction.
        raw = 'Here is the answer: {"done": true} — hope that helps.'
        async def _run():
            llm, _ = _make_engine([_ok(raw)])
            r = await llm.chat_json([{"role": "user", "content": "q"}])
            await llm.close()
            return r
        self.assertEqual(asyncio.run(_run()), {"done": True})

    def test_invalid_json_returns_none(self):
        async def _run():
            llm, _ = _make_engine([
                _ok("no json here at all"),
                _ok("still no json"),
                _ok("nope"),
            ])
            r = await llm.chat_json([{"role": "user", "content": "q"}])
            await llm.close()
            return r
        self.assertIsNone(asyncio.run(_run()))

    def test_truncated_json_is_repaired_instead_of_rerolled(self):
        """A response cut off by the token cap only misses its closers.

        This is the failure one run hit three times on evidence classification:
        the model wrote a long reasoning field, the 256-token cap landed inside it,
        the JSON never parsed - and the retry with a higher temperature produced
        the same long field and the same cut.
        """
        raw = ('{\n  "evidence_type": "contradicts",\n  "strength": 0.85,\n'
               '  "reasoning": "The hypothesis claims that the pathway from '
               'physical health to cognition operates via inflammation')

        async def _run():
            llm, _ = _make_engine([_ok(raw)])
            r = await llm.chat_json([{"role": "user", "content": "q"}], max_tokens=256)
            await llm.close()
            return r

        result = asyncio.run(_run())
        self.assertEqual(result["evidence_type"], "contradicts")
        self.assertEqual(result["strength"], 0.85)
        self.assertTrue(result["reasoning"].startswith("The hypothesis claims"))

    def test_repair_keeps_only_complete_members(self):
        """When the cut lands on a key, the incomplete member is dropped."""
        raw = '{"verdict": "weakened", "vulnerabilities": [{"point": "selection bias", "sev'

        async def _run():
            llm, _ = _make_engine([_ok(raw)])
            r = await llm.chat_json([{"role": "user", "content": "q"}])
            await llm.close()
            return r

        self.assertEqual(asyncio.run(_run()), {"verdict": "weakened"})

    def test_balanced_but_invalid_json_is_not_treated_as_truncation(self):
        raw = '{"a": ,}'

        async def _run():
            llm, _ = _make_engine([_ok(raw), _ok(raw), _ok(raw)])
            r = await llm.chat_json([{"role": "user", "content": "q"}])
            await llm.close()
            return r

        self.assertIsNone(asyncio.run(_run()))

    def test_closers_come_out_in_container_order(self):
        """A flat count produced "[}]"; the nesting has to close inside out."""
        repaired = LLMEngine._close_truncated_json('{"a": [{"b": "c')
        self.assertEqual(json.loads(repaired), {"a": [{"b": "c"}]})

    def test_nothing_to_repair_without_a_container(self):
        self.assertIsNone(LLMEngine._close_truncated_json("just prose"))
        self.assertIsNone(LLMEngine._close_truncated_json('{"a": 1}'))

    def test_error_marker_returns_none_without_retry(self):
        async def _run():
            # Only ONE response scripted: on [ERROR:...] chat_json must return
            # None immediately instead of retrying (which would exhaust the queue
            # and trigger the fallback 500 - still fine, but None either way).
            llm, _ = _make_engine([_FakeResponse(status=500, text="x")])
            r = await llm.chat_json([{"role": "user", "content": "q"}])
            await llm.close()
            return r
        self.assertIsNone(asyncio.run(_run()))


def _make_tudagpt_engine(responses):
    """Engine pinned to the TUDaGPT backend (Hochschulrechenzentrum TU Darmstadt)."""
    engine, session = _make_engine(responses, session_cls=_RecordingSession)
    engine._backend = "tudagpt"
    engine._tudagpt_url = "https://tudagpt.example/api"
    engine._tudagpt_key = "test-key"
    engine._tudagpt_model = "gwdg/qwen3.5-397b-a17b"
    return engine, session


def _openai_ok(content, prompt_tokens=7, completion_tokens=3):
    return _FakeResponse(status=200, json_payload={
        "choices": [{"message": {"role": "assistant", "content": content}}],
        "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens},
    })


class TestTudagptBackend(unittest.TestCase):
    """chat()/embed() against the TUDaGPT OpenAI-compatible endpoint."""

    def test_request_contract_and_json_parsing(self):
        async def _run():
            llm, session = _make_tudagpt_engine([_openai_ok('{"a": 1}')])
            result = await llm.chat_json([{"role": "user", "content": "q"}])
            await llm.close()
            return result, session

        result, session = asyncio.run(_run())
        self.assertEqual(result, {"a": 1})
        self.assertEqual(len(session.calls), 1)
        call = session.calls[0]
        # TUDaGPT lives at {base}/chat/completions - no /v1 prefix.
        self.assertEqual(call["url"], "https://tudagpt.example/api/chat/completions")
        self.assertEqual(call["headers"]["Authorization"], "Bearer test-key")
        self.assertEqual(call["json"]["model"], "gwdg/qwen3.5-397b-a17b")
        self.assertEqual(call["json"]["response_format"], {"type": "json_object"})
        self.assertEqual(call["json"]["reasoning_effort"], "none")
        self.assertFalse(call["json"]["stream"])

    def test_plain_chat_has_no_json_mode(self):
        async def _run():
            llm, session = _make_tudagpt_engine([_openai_ok("plain answer")])
            text = await llm.chat([{"role": "user", "content": "q"}])
            await llm.close()
            return text, session

        text, session = asyncio.run(_run())
        self.assertEqual(text, "plain answer")
        self.assertNotIn("response_format", session.calls[0]["json"])

    def test_retries_on_server_error_then_succeeds(self):
        async def _run():
            llm, _ = _make_tudagpt_engine([
                _FakeResponse(status=503, text="busy"),
                _openai_ok("recovered"),
            ])
            text = await llm.chat([{"role": "user", "content": "q"}])
            await llm.close()
            return text

        self.assertEqual(asyncio.run(_run()), "recovered")

    def test_rejected_key_is_not_retried(self):
        async def _run():
            llm, session = _make_tudagpt_engine([
                _FakeResponse(status=401, text="unauthorized"),
            ])
            text = await llm.chat([{"role": "user", "content": "q"}])
            await llm.close()
            return text, session

        text, session = asyncio.run(_run())
        self.assertTrue(text.startswith("[ERROR:"), text)
        self.assertIn("401", text)
        self.assertEqual(len(session.calls), 1)

    def test_missing_key_fails_without_request(self):
        async def _run():
            llm, session = _make_tudagpt_engine([])
            llm._tudagpt_key = ""
            text = await llm.chat([{"role": "user", "content": "q"}])
            healthy = await llm.health_check()
            await llm.close()
            return text, healthy, session

        text, healthy, session = asyncio.run(_run())
        self.assertTrue(text.startswith("[ERROR:"), text)
        self.assertIn("TUDAGPT_API_KEY", text)
        self.assertFalse(healthy)
        self.assertEqual(session.calls, [])

    def test_health_check_ok(self):
        async def _run():
            llm, _ = _make_tudagpt_engine([_openai_ok("pong")])
            healthy = await llm.health_check()
            await llm.close()
            return healthy

        self.assertTrue(asyncio.run(_run()))

    def test_embeddings_still_use_ollama(self):
        async def _run():
            llm, session = _make_tudagpt_engine([
                _FakeResponse(status=200, json_payload={"embeddings": [[0.1, 0.2]]}),
            ])
            emb = await llm.embed(["text"])
            await llm.close()
            return emb, session

        emb, session = asyncio.run(_run())
        self.assertEqual(emb, [[0.1, 0.2]])
        self.assertTrue(session.calls[0]["url"].endswith("/api/embed"), session.calls[0]["url"])


class TestStandalone(unittest.TestCase):
    """Direct unit checks."""

    def test_strip_markdown_fence(self):
        cleaner = LLMEngine._strip_markdown_fence
        self.assertEqual(cleaner('```json\n{"a": 1}\n```'), '{"a": 1}')
        self.assertEqual(cleaner("```\n[1,2,3]\n```"), "[1,2,3]")
        # No fence -> unchanged
        self.assertEqual(cleaner('{"a": 1}'), '{"a": 1}')
        self.assertEqual(cleaner("plain text"), "plain text")

    def test_compute_delay_backoff(self):
        engine = LLMEngine()
        self.assertEqual(engine._compute_delay(0), 2.0)
        self.assertEqual(engine._compute_delay(1), 4.0)
        self.assertEqual(engine._compute_delay(2), 8.0)
        # Capped at MAX_DELAY
        self.assertEqual(engine._compute_delay(99), engine.MAX_DELAY)
        # Retry-After header wins
        self.assertEqual(engine._compute_delay(0, "1.5"), 1.5)

    def test_embed_success(self):
        async def _run():
            llm, _ = _make_engine([
                _FakeResponse(status=200,
                              json_payload={"embeddings": [[0.1, 0.2, 0.3]]}),
            ])
            emb = await llm.embed(["text"])
            await llm.close()
            return emb
        self.assertEqual(asyncio.run(_run()), [[0.1, 0.2, 0.3]])

    def test_concurrent_usage_across_loops(self):
        # Each asyncio.run() creates a NEW event loop. The global semaphore must
        # be rebound/recreated each time, otherwise the second run raises
        # "Task got Future attached to a different loop".
        results = []
        for _ in range(2):
            async def _run():
                llm, _ = _make_engine([_ok("ok")])
                r = await llm.chat([{"role": "user", "content": "q"}])
                await llm.close()
                return r
            results.append(asyncio.run(_run()))
        self.assertEqual(results, ["ok", "ok"])


class TestExtractorSession(unittest.TestCase):
    """ContentExtractor keeps a session per event loop (multi-loop safe)."""

    def test_session_per_loop(self):
        # Each asyncio.run() spins up a NEW event loop. A session must be created
        # fresh and bound to THAT loop - never reused across loops. Sessions stay
        # alive inside extractor._sessions, so object ids are guaranteed distinct.
        ex = ContentExtractor()
        sessions = []
        for _ in range(3):
            async def _run(ex=ex, sessions=sessions):
                s = await ex._get_session()
                sessions.append(s)
                return not s.closed
            self.assertTrue(asyncio.run(_run()))
        # 3 distinct loops -> 3 distinct session objects (no cross-loop reuse).
        self.assertEqual(len({id(s) for s in sessions}), 3)
        self.assertEqual(len(ex._sessions), 3)

    def test_reuse_same_loop_single_session(self):
        # Within the SAME loop the session must be reused (not recreated).
        ex = ContentExtractor()
        async def _run():
            s1 = await ex._get_session()
            s2 = await ex._get_session()
            return s1 is s2
        self.assertTrue(asyncio.run(_run()))


class TestAbstractRecovery(unittest.TestCase):
    """Blocked landing pages: recover the abstract from Crossref/OpenAlex so the
    source has real document text instead of only a search snippet."""

    LONG_ABSTRACT = (
        "Genome-wide association analyses of educational attainment in 1.1 million "
        "individuals identified 1,271 independent genome-wide significant loci, "
        "explaining 11 to 13 percent of the variance in educational attainment. "
        "Polygenic scores built from these summary statistics predict about four "
        "percent of the variance within a single cohort and roughly eleven percent "
        "in within-family designs that control for population stratification."
    )

    class _Getter:
        """Session stub: first URL substring match wins, everything else 404s."""

        def __init__(self, routes):
            self.routes = routes
            self.calls = []
            self.closed = False

        def get(self, url=None, **kwargs):
            self.calls.append({"url": url, "params": kwargs.get("params")})
            for needle, response in self.routes:
                if needle in (url or ""):
                    return _RespContext(response)
            return _RespContext(_FakeResponse(status=404, json_payload={}))

    def _extractor(self, routes):
        ex = ContentExtractor()
        session = self._Getter(routes)

        async def _ensure():
            return session

        ex._get_session = _ensure
        return ex, session

    def test_doi_from_url(self):
        self.assertEqual(
            ContentExtractor.doi_from_url("https://doi.org/10.1038/s41586-018-0574-4"),
            "10.1038/s41586-018-0574-4",
        )
        self.assertEqual(ContentExtractor.doi_from_url("https://example.org/x"), "")

    def test_crossref_by_doi_recovers_abstract(self):
        payload = {"message": {
            "title": ["GWAS of educational attainment"],
            "abstract": f"<jats:p>{self.LONG_ABSTRACT}</jats:p>",
        }}
        ex, session = self._extractor([
            ("api.crossref.org/works/10.", _FakeResponse(status=200, json_payload=payload)),
        ])

        result = asyncio.run(ex.fetch_abstract(url="https://doi.org/10.1038/s41586-018-0574-4"))

        self.assertIsNotNone(result)
        self.assertTrue(result["success"])
        self.assertEqual(result["abstract_source"], "crossref-doi")
        self.assertIn("1,271 independent", result["content"])
        self.assertNotIn("<jats:p>", result["content"])
        self.assertTrue(result["content_hash"])
        self.assertIn("10.1038/s41586-018-0574-4", session.calls[0]["url"])

    def test_openalex_inverted_index_is_reconstructed_in_order(self):
        # Pad to pass the minimum length, keeping word order stable.
        words = ["Polygenic", "scores", "predict", "IQ", "weakly"] + [
            f"padding{i:03d}" for i in range(40)
        ]
        inverted = {w: [] for w in words}
        for i, w in enumerate(words):
            inverted[w].append(i)
        payload = {"results": [{
            "title": "Polygenic scores predict IQ weakly",
            "abstract_inverted_index": inverted,
        }]}
        ex, _ = self._extractor([
            ("api.openalex.org/works", _FakeResponse(status=200, json_payload=payload)),
        ])

        result = asyncio.run(ex.fetch_abstract(title="Polygenic scores predict IQ weakly"))

        self.assertIsNotNone(result)
        self.assertEqual(result["abstract_source"], "openalex")
        self.assertTrue(result["content"].startswith("Polygenic scores predict IQ weakly")
                        or "Polygenic scores predict IQ weakly" in result["content"])

    def test_titles_match_guard(self):
        self.assertTrue(ContentExtractor._titles_match(
            "Shared genetic architecture between ADHD and intelligence varies across subtypes",
            "Shared genetic architecture between ADHD and intelligence varies across ADHD subtypes",
        ))
        self.assertFalse(ContentExtractor._titles_match(
            "Shared genetic architecture between ADHD and intelligence",
            "Solution-processable 2D semiconductors for large-area electronics",
        ))

    def test_title_lookup_rejects_a_different_paper(self):
        payload = {"message": {"items": [{
            "title": ["Solution-processable 2D semiconductors for large-area electronics"],
            "abstract": self.LONG_ABSTRACT,
        }]}}
        ex, _ = self._extractor([
            ("api.crossref.org", _FakeResponse(status=200, json_payload=payload)),
            ("api.openalex.org", _FakeResponse(status=200, json_payload={"results": []})),
        ])

        self.assertIsNone(asyncio.run(ex.fetch_abstract(
            title="Shared genetic architecture between ADHD and intelligence"
        )))

    def test_short_abstract_is_rejected(self):
        payload = {"message": {"title": ["T"], "abstract": "Too short."}}
        ex, _ = self._extractor([
            ("api.crossref.org", _FakeResponse(status=200, json_payload=payload)),
            ("api.openalex.org", _FakeResponse(status=200, json_payload={"results": []})),
        ])

        self.assertIsNone(asyncio.run(ex.fetch_abstract(url="https://doi.org/10.1/x")))

    def test_all_lookups_failing_returns_none(self):
        ex, _ = self._extractor([])
        self.assertIsNone(asyncio.run(ex.fetch_abstract(
            url="https://europepmc.org/article/MED/42103730",
            title="Shared genetic architecture between ADHD and intelligence",
        )))


class TestOpenAccessRecovery(unittest.TestCase):
    """Sources with neither a readable page nor an abstract: use the free full
    text (Europe PMC XML, Unpaywall OA PDF/landing page)."""

    LONG_TEXT = ("Introduction: polygenic scores for educational attainment "
                 "explain a small share of variance in cognitive outcomes. " * 30)

    class _BodyResponse(_FakeResponse):
        """Fake response that can also serve PDF bytes / HTML text."""

        def __init__(self, status=200, json_payload=None, text="",
                     body=b"", content_type="text/html"):
            super().__init__(status=status, json_payload=json_payload, text=text)
            self._body = body
            self.headers = {"Content-Type": content_type}
            self._content_type = content_type

        async def read(self):
            return self._body

        async def text(self, *args, **kwargs):
            return self._text

    class _Getter:
        def __init__(self, routes):
            self.routes = routes
            self.calls = []
            self.closed = False

        def get(self, url=None, **kwargs):
            self.calls.append(url)
            for needle, response in self.routes:
                if needle in (url or ""):
                    return _RespContext(response)
            return _RespContext(_FakeResponse(status=404, json_payload={}))

    def _extractor(self, routes):
        ex = ContentExtractor()
        session = self._Getter(routes)

        async def _ensure():
            return session

        ex._get_session = _ensure
        return ex, session

    def test_europepmc_fulltext_xml_is_used(self):
        xml = f"<article><body><p>{self.LONG_TEXT}</p></body></article>"
        ex, _ = self._extractor([
            ("europepmc/webservices", self._BodyResponse(text=xml)),
        ])

        result = asyncio.run(ex.fetch_open_access_text(
            url="https://europepmc.org/article/PMC/PMC13669090",
            title="Some genetics paper",
        ))

        self.assertIsNotNone(result)
        self.assertTrue(result["fulltext_source"].startswith("europepmc-fulltext"))
        self.assertIn("polygenic scores", result["content"])
        self.assertNotIn("<p>", result["content"])

    def test_unpaywall_pdf_is_tried_then_landing_page(self):
        # The PDF candidate yields no text (garbage bytes); the landing page does.
        unpaywall = {"is_oa": True, "best_oa_location": {
            "url_for_pdf": "https://oa.example/paper.pdf",
            "url": "https://oa.example/paper",
        }, "oa_locations": []}
        html = f"<html><body><article><p>{self.LONG_TEXT}</p></article></body></html>"
        ex, session = self._extractor([
            ("api.unpaywall.org", self._BodyResponse(json_payload=unpaywall)),
            ("paper.pdf", self._BodyResponse(body=b"%PDF-1.4 broken",
                                             content_type="application/pdf")),
            ("oa.example/paper", self._BodyResponse(text=html)),
        ])

        result = asyncio.run(ex.fetch_open_access_text(
            url="https://doi.org/10.1234/paper", title="A paper"
        ))

        self.assertIsNotNone(result)
        self.assertEqual(result["fulltext_source"], "https://oa.example/paper")
        self.assertIn("polygenic scores", result["content"])
        self.assertIn("https://oa.example/paper.pdf", session.calls)

    def test_no_open_access_copy_returns_none(self):
        ex, _ = self._extractor([])
        self.assertIsNone(asyncio.run(ex.fetch_open_access_text(
            url="https://europepmc.org/article/MED/123", title="Nothing"
        )))

    def test_short_open_access_text_is_rejected(self):
        html = "<html><body><p>Too short.</p></body></html>"
        unpaywall = {"is_oa": True, "best_oa_location": {"url": "https://oa.example/short"}}
        ex, _ = self._extractor([
            ("api.unpaywall.org", self._BodyResponse(json_payload=unpaywall)),
            ("oa.example/short", self._BodyResponse(text=html)),
        ])

        self.assertIsNone(asyncio.run(ex.fetch_open_access_text(
            url="https://doi.org/10.1234/short", title="Short"
        )))

    def test_pdf_garbage_yields_no_text(self):
        self.assertEqual(ContentExtractor._pdf_text(b"%PDF-1.4 not really"), "")


class TestUnwrapJsonList(unittest.TestCase):
    """A "return only a JSON array" prompt answered in JSON-object mode comes
    back wrapped ({"claims": [...]}); callers must get the items, not the
    envelope."""

    def test_plain_list_passes_through(self):
        items = [{"content": "a"}, {"content": "b"}]
        self.assertEqual(unwrap_json_list(items), items)

    def test_single_key_envelope_is_unwrapped(self):
        self.assertEqual(unwrap_json_list({"claims": [{"content": "a"}]}),
                         [{"content": "a"}])

    def test_envelope_with_metadata_still_unwraps(self):
        result = {"claims": [{"content": "a"}], "note": "only two found"}
        self.assertEqual(unwrap_json_list(result), [{"content": "a"}])

    def test_known_list_key_wins_when_several_lists(self):
        result = {"queries": ["q1"], "warnings": ["w1"]}
        self.assertEqual(unwrap_json_list(result), ["q1"])

    def test_single_object_is_one_item(self):
        self.assertEqual(unwrap_json_list({"content": "a", "confidence": 0.9}),
                         [{"content": "a", "confidence": 0.9}])

    def test_none_and_scalars_yield_empty_list(self):
        for value in (None, "text", 3, 0.5, True):
            self.assertEqual(unwrap_json_list(value), [], value)

    def test_empty_envelope_yields_empty_list(self):
        self.assertEqual(unwrap_json_list({"facts": []}), [])


class TestDashboardRunner(unittest.TestCase):
    """The shared _AsyncRunner runs coroutines on ONE dedicated loop."""

    def test_all_submissions_share_one_loop(self):
        runner = _AsyncRunner()
        try:
            loop_ids = set()

            async def probe():
                return id(asyncio.get_running_loop())

            for _ in range(3):
                # Submit from different threads/contexts; all must land on the
                # same (runner) loop.
                fut = runner.submit(probe())
                loop_ids.add(fut.result(timeout=5))
            self.assertEqual(len(loop_ids), 1, loop_ids)
        finally:
            runner.stop()


if __name__ == "__main__":
    unittest.main(verbosity=2)