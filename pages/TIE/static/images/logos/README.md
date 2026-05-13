# Affiliation logos

Drop institution logo files into this folder. Each `<a class="aff-logo">`
element in `index.html` looks for one of the filenames below. If a file is
missing, a clean text fallback (the institution acronym in a bordered pill)
is shown automatically — so the page always looks finished.

## Expected files

| Filename       | Institution                                      | Source (suggested)                                                     |
| -------------- | ------------------------------------------------ | ---------------------------------------------------------------------- |
| `ustc.svg`     | University of Science and Technology of China    | https://en.ustc.edu.cn/ — official press kit                           |
| `sjtu.svg`     | Shanghai Jiao Tong University                    | https://en.sjtu.edu.cn/ — official identity assets                     |
| `ntu.svg`      | Nanyang Technological University                 | https://www.ntu.edu.sg/                                                |
| `waterloo.svg` | University of Waterloo                           | https://uwaterloo.ca/brand/                                            |
| `psu.svg`      | The Pennsylvania State University                | https://brand.psu.edu/                                                 |
| `zgc.svg`      | Zhongguancun Academy                             | (provide internally)                                                   |
| `hku.svg`      | The University of Hong Kong                      | https://www.hku.hk/                                                    |

Matrix Team's logo is loaded directly from
`https://matrixteam-ai.github.io/assets/img/white-logo.svg` and does not need
a local copy.

## Format guidance

* **SVG preferred** — sharp on retina displays, tiny file size.
* PNG also works (use 2x density, transparent background).
* Aim for a logo that reads well at **40 px tall**.
* If the official logo is dark, no extra work needed — the strip applies
  `grayscale(100%)` by default and turns full color on hover. Keep this
  style for visual consistency across logos.
