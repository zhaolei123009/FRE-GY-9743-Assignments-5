"""Run the assignment with this Python interpreter, from any working directory."""
from pathlib import Path
import tempfile

import nbformat
from nbclient import NotebookClient
from jupyter_client.kernelspec import KernelSpecManager

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'hw5_valuation_and_first_order_risk.ipynb'
notebook = nbformat.read(path, as_version=4)
# An ephemeral kernel spec avoids changing the user's Jupyter configuration.
with tempfile.TemporaryDirectory() as temporary:
    from ipykernel.kernelspec import install
    install(prefix=temporary, kernel_name='assignment5',
            display_name='Assignment 5')
    manager = KernelSpecManager(kernel_dirs=[str(Path(temporary)/'share/jupyter/kernels')])
    notebook.metadata.kernelspec = {
        'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}
    client = NotebookClient(notebook, timeout=180, kernel_name='assignment5',
        resources={'metadata': {'path': str(ROOT)}},
        kernel_manager_class='jupyter_client.manager.KernelManager')
    from jupyter_client import KernelManager
    client.km = KernelManager(kernel_name='assignment5', kernel_spec_manager=manager)
    client.execute()
nbformat.write(notebook, path)
print(f'Executed {sum(c.cell_type == "code" for c in notebook.cells)} code cells: {path.name}')
