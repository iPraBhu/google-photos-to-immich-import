from app.utils.google_photos_extractor import GooglePhotosExtractor

def test_extract_album_html(monkeypatch):
    class DummyResp:
        text = '<html><title>Test Album</title></html>'
        def raise_for_status(self): pass
    monkeypatch.setattr("httpx.get", lambda url, timeout: DummyResp())
    result = GooglePhotosExtractor.extract_album("http://fake")
    assert result["title"] == "Sample Album"
