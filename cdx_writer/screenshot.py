from .handler import RecordHandler
from .dispatcher import DefaultDispatcher

class ScreenshotHandler(RecordHandler):
    @property
    def original_url(self):
        return 'http://web.archive.org/screenshot/' + self.safe_url()

    @property
    def massaged_url(self):
        return 'org,archive,web)/screenshot/' + self.urlkey(self.safe_url())

    @property
    def mime_type(self):
        return self._normalize_content_type(self.record.content_type)

class ScreenshotDispatcher(DefaultDispatcher):
    def dispatch_metadata(self, record, env):
        content_type = record.content_type
        if content_type and content_type.startswith(b'image/'):
            return ScreenshotHandler
        return None
