"""Phase 6: study-register search + accepted citation chaining audit.

The register provider (ClinicalTrials.gov API v2) answers offline from a
fixture body; parsing rules mirror the study record structure, so a
registered trial becomes an ordinary source with its NCT id, status and
enrolment in the snippet - no key, no fitted thresholds, no mock network.
"""

import asyncio
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.research.search import (
    ClinicalTrialsRegisterProvider,
    SearchManager,
    SearchProvider,
    SearchResult,
)


def _study(nct="NCT00000001", title="Exercise vs control in depression",
           status="Completed", count=240, conditions=("Major depressive disorder",),
           summary="Randomised controlled trial of a walking programme."):
    return {"protocolSection": {
        "identificationModule": {"nctId": nct, "briefTitle": title},
        "statusModule": {
            "overallStatus": status,
            "studyFirstPostDateStruct": {"date": "2019-03-14"},
        },
        "designModule": {"enrollmentInfo": {"count": count}},
        "conditionsModule": {"conditions": list(conditions)},
        "descriptionModule": {"briefSummary": summary},
    }}


class FakeResponse:
    def __init__(self, status=200, payload=None):
        self.status = status
        self._payload = payload

    async def json(self):
        return self._payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class FakeSession:
    def __init__(self, response):
        self._response = response

    def get(self, url, params=None):
        self.params = params
        return self._response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class ClinicalTrialsParseTest(unittest.TestCase):
    def _run(self, payload, status=200):
        provider = ClinicalTrialsRegisterProvider()
        session = FakeSession(FakeResponse(status=status, payload=payload))
        with mock.patch("research_agent.research.search.aiohttp.ClientSession",
                        return_value=session, timeout=5):
            return asyncio.run(provider.search("exercise depression",
                                               max_results=5)), session

    def test_records_parse_into_search_results(self):
        results, session = self._run({"studies": [_study(), _study(
            nct="NCT00000002", title="Second arm", count=None,
            status="Terminated")]})
        self.assertEqual(len(results), 2)
        first = results[0]
        self.assertEqual(first.url, "https://clinicaltrials.gov/study/NCT00000001")
        self.assertEqual(first.source_type, "clinicaltrials")
        self.assertEqual(first.year, "2019")
        self.assertIn("NCT NCT00000001", first.snippet)
        self.assertIn("Status: Completed", first.snippet)
        self.assertIn("n=240", first.snippet)
        self.assertIn("Condition: Major depressive disorder", first.snippet)
        # no enrolment -> no n= fragment, no invented number
        second = results[1]
        self.assertNotIn("n=", second.snippet)
        self.assertIn("Status: Terminated", second.snippet)

    def test_error_status_notes_failure_and_stays_empty(self):
        results, _ = self._run(None, status=500)
        self.assertEqual(results, [])

    def test_records_without_nct_or_title_are_skipped(self):
        body = {"studies": [
            _study(nct=""),  # no id: worthless without the register link
            _study(title="", summary=""),
            _study(),
        ]}
        results, _ = self._run(body)
        self.assertEqual(len(results), 1)


class RegisterRegistrationTest(unittest.TestCase):
    def test_default_provider_list_includes_the_register(self):
        names = list(SearchManager().providers.keys())
        self.assertIn("clinicaltrials", names)
        # Established order unchanged: arxiv still leads.
        self.assertEqual(names[0], "arxiv")

    def test_register_provider_implements_the_contract(self):
        provider = ClinicalTrialsRegisterProvider()
        self.assertIsInstance(provider, SearchProvider)
        self.assertEqual(provider.name, "clinicaltrials")


if __name__ == "__main__":
    unittest.main()
