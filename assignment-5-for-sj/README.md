# Assignment 5 — Implicit Differentiation, Valuation and First-Order Risk

Complete solution for FRE-GT-9743 Assignment 5. Part I gives the written answers;
Part II completes all five library tasks and includes the executed notebook.

## Contents

| File / directory | Purpose |
|---|---|
| [Part I answers](docs/part_i_implicit_differentiation.md) | Q1–Q3: calibration, implicit derivatives, option smile and trader risk |
| [Executed notebook](hw5_valuation_and_first_order_risk.ipynb) | Original workflow with saved outputs |
| [Curve model](fixedincomelib/yield_curve/yield_curve_model.py) | Local and recursive discount-factor gradients (tasks 1–2) |
| [Valuation engine](fixedincomelib/yield_curve/valuation_engine.py) | Funding selection, PV/cash and first-order risk (tasks 3–5) |
| [Tests](tests/test_valuation.py) | Independent formulas, central differences and boundary cases |
| [Method and results](docs/implementation.md) | Formulas, conventions and verified numerical results |
| `static_files/` | Required registry configuration; keep this beside `fixedincomelib/` |
| `.github/workflows/checks.yml` | Tests and notebook execution on GitHub pushes/PRs |

## Run locally

Use **Python 3.11**. Open a terminal **in this repository's root folder**:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/execute_notebook.py
```

On Windows, use `py -3.11 -m venv .venv` and activate with
`.venv\Scripts\activate` instead. The numerical dependencies are pinned to
NumPy 1.26.4, pandas 2.3.1 and QuantLib 1.41.

For interactive use:

```bash
python -m ipykernel install --user --name assignment5 --display-name "Assignment 5 (Python 3.11)"
jupyter lab
```

Open `hw5_valuation_and_first_order_risk.ipynb`, choose the **Assignment 5
(Python 3.11)** kernel, and run all cells. The execution script automatically
uses its own Python interpreter without requiring a permanent kernel install.

## Verified example

The original notebook inputs give:

- Accrual fraction: `0.25277777777777777` (`91/360`).
- Signed cash amount: `252777.77777777778 USD`.
- Present value: `245870.91057967892 USD`.
- Cash payable on the value date: `0 USD`.
- SOFR raw risk: `[-60625.703979, -123272.264756, 0.000000]`.
- Funding-spread raw risk: `[-121925.026890, -61972.941845]`.

Raw risk is the PV derivative per **1.0 annual decimal** IFR change. The report
multiplies by `0.0001` for the signed PV change for a positive 1 bp node bump.
It does not reverse the sign into a positive-duration convention.

## 上传 GitHub（中文操作说明）

1. 解压交付的 ZIP，进入 `assignment-5` 文件夹。
2. 在 GitHub 创建一个空仓库。若课程限制公开答案，请选 Private。
3. 在该文件夹中打开终端，按下面命令上传；将最后的仓库地址替换成你自己的。

```bash
git init
git add .
git commit -m "Complete Assignment 5: implicit differentiation and valuation engine"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

`YOUR_USERNAME/YOUR_REPOSITORY` 是唯一需要替换的上传信息，不是代码占位符。
也可以在 GitHub 仓库网页用 **Add file → Upload files**，上传解压后的全部内容。
网页上传时确认隐藏目录 `.github` 和 `.gitignore` 也包含在内。
不要只上传 notebook：它依赖 `fixedincomelib` 和 `static_files`。

书面答案使用英文，便于按英文题目提交。建议先阅读答案和方法说明，确认理解
推导与符号，并按课程要求补充个人信息。项目没有填入虚构姓名或学号。

## Attribution and scope

Based on the [course starter repository](https://github.com/Jerry0108-SJ/FRE-GY-9743-Assignments-5),
commit `ad9e3fc17def3bdd5539d65e9a51470215d93727`.
The starter's MIT [LICENSE](LICENSE) is retained. Original source, configuration,
and screenshots are preserved. Changes complete the five assigned methods;
additional files supply answers, documentation, tests and CI.

The engine intentionally handles the assignment's fixed-accrual cashflow and
direct IFR state risk. The cash amount is `notional * accrued`; the product has
no separate coupon-rate field. This is not a general bond or option engine.
