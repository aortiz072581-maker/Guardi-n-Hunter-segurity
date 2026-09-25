from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from guardian_hunter.assessment.safe import assess_headers


USER_AGENT = "Guardian-Hunter/1.0"


def assess_http(url, timeout=8):
    findings = []

    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
        },
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            headers = dict(response.headers.items())

            findings.extend(assess_headers(headers))

            return {
                "url": url,
                "status": response.status,
                "headers": headers,
                "findings": findings,
                "error": None,
            }

    except HTTPError as exc:
        headers = dict(exc.headers.items()) if exc.headers else {}
        findings.extend(assess_headers(headers))

        return {
            "url": url,
            "status": exc.code,
            "headers": headers,
            "findings": findings,
            "error": str(exc),
        }

    except (URLError, OSError, TimeoutError) as exc:
        return {
            "url": url,
            "status": None,
            "headers": {},
            "findings": [],
            "error": str(exc),
        }

    except Exception as exc:
        return {
            "url": url,
            "status": None,
            "headers": {},
            "findings": [],
            "error": str(exc),
        }
