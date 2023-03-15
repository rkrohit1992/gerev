import logging
import threading

from docs_queue import IndexingQueue
from indexing.index_documents import Indexer


class BackgroundIndexer:
    _thread = None
    _stop_event = threading.Event()
    _left_to_index = 0

    @classmethod
    def get_left_to_index(cls):
        return cls._left_to_index

    @classmethod
    def start(cls):
        cls._thread = threading.Thread(target=cls.run)
        cls._thread.start()

    @classmethod
    def stop(cls):
        cls._stop_event.set()
        logging.info('Stop event set, waiting for background indexer to stop...')

        cls._thread.join()
        logging.info('Background indexer stopped')

        cls._thread = None

    @staticmethod
    def run():
        logger = logging.getLogger()
        docs_queue_instance = IndexingQueue.get()
        logger.info(f'Background indexer started...')

        while not BackgroundIndexer._stop_event.is_set():
            docs_chunk = docs_queue_instance.consume_all()
            if not docs_chunk:
                continue

            BackgroundIndexer._left_to_index = len(docs_chunk)
            logger.info(f'Got chunk of {len(docs_chunk)} documents')
            Indexer.index_documents(docs_chunk)
            logger.info(f'Finished indexing chunk of {len(docs_chunk)} documents')
            BackgroundIndexer._left_to_index = 0