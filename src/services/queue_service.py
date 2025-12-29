import queue
import threading
from src.services.caching_service.set_cache import set_cached_results

# Single global queue
rerank_queue = queue.Queue(maxsize=1000)

# 🔒 Tracks (query, _type) currently being reranked
rerank_in_progress: set[tuple[str, str]] = set()
rerank_lock = threading.Lock()


def rerank_worker():
    """
    Background worker that performs LLM reranking
    """

    while True:

        query, results, _type, es = rerank_queue.get()

        try:

            # This is where LLM runs (blocking, but NOT user-facing)
            set_cached_results(query, results, _type, es)

        except Exception as e:
            print("Rerank worker crashed: ", e)

        finally:
            # 🔑 Always clean up
            with rerank_lock:
                rerank_in_progress.discard((query, _type))

            rerank_queue.task_done()

def start_rerank_worker():
    """
    Start exactly ONE background worker
    """
    worker = threading.Thread(
        target=rerank_worker,
        daemon=True
    )
    worker.start()
