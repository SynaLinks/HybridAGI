import unittest

from hybridagi import (
    FileSystemContext,
    FileSystem,
    BrowserUtility,
)

from langchain.embeddings import FakeEmbeddings

class TestBrowserUtility(unittest.TestCase):

    def setUp(self):
        self.embeddings = FakeEmbeddings(size=512)
        self.embeddings_dim = 512
        # Set up the RedisGraphHybridStore and the VirtualFileSystem
        self.context = FileSystemContext()
        self.filesystem = FileSystem(
            redis_url = 'redis://localhost:6379',
            index_name = 'test_index',
            embeddings = self.embeddings,
            embeddings_dim = self.embeddings_dim,
            context = self.context
        )
        self.filesystem.clear()

        self.browser = BrowserUtility(
            filesystem = self.filesystem,
            user_agent = "",
        )

    def test_browser(self):
        result = self.browser.browse_website("https://synalinks.com")
        self.assertTrue("SynaLinks" in result)