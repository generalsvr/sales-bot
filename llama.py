from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
n_gpu_layers = 63  # Change this value based on your model and your GPU VRAM pool.
n_batch = 1024  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.

def load_llama():
    llama_llm = LlamaCpp(
        model_path="./guanaco-33B.ggmlv3.q4_1.bin",
        n_gpu_layers=n_gpu_layers,
        n_batch=n_batch,
        callback_manager=callback_manager,
        verbose=True,
    )
    return llama_llm