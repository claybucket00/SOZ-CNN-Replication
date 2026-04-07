# Localising the Seizure Onset Zone from SPES Responses — Replication & Ablation Study

Repository: **SOZ-CNN-Replication**

This repository contains code and documentation for a replication study of:

> Norris et al., “Localising the Seizure Onset Zone from Single-Pulse Electrical Stimulation Responses with a CNN Transformer” (2024).

Our goal is to reproduce the original results as closely as possible and to explore how stimulation paradigms and modeling choices affect performance.

---

## Original Paper and Resources

* Original paper (preprint): [https://arxiv.org/abs/2403.20324](https://arxiv.org/abs/2403.20324)
* Original code (authors’ repo): [https://github.com/norrisjamie23/Localising_SOZ_from_SPES](https://github.com/norrisjamie23/Localising_SOZ_from_SPES)
* Dataset (OpenNeuro SPES ECoG): [https://openneuro.org/datasets/ds004080/versions/1.2.4](https://openneuro.org/datasets/ds004080/versions/1.2.4)
* Our replication code: [https://github.com/claybucket00/SOZ-CNN-Replication](https://github.com/claybucket00/SOZ-CNN-Replication)
* PyHealth dataset PR: [https://github.com/sunlabuiuc/PyHealth/pull/685](https://github.com/sunlabuiuc/PyHealth/pull/685)

---

## Citation

If you use this code or the reproduced setup, please cite the original paper:

```bibtex
@article{norris2024localisingseizureonsetzone,
  title={Localising the Seizure Onset Zone from Single-Pulse Electrical Stimulation Responses with a CNN Transformer},
  author={Norris, Jamie and others},
  journal={arXiv preprint arXiv:2403.20324},
  year={2024}
}
```

---

## Motivation

Accurate localisation of the Seizure Onset Zone (SOZ) is critical for epilepsy surgery planning.
The original work investigates whether deep learning models trained on single-pulse electrical stimulation (SPES) responses can classify whether a stimulated contact lies inside or outside the SOZ.

Key aspects of the original study:

* Use of SPES-locked ECoG segments as input.
* Comparison of two paradigms:

  * **Convergent**: responses converging onto a contact.
  * **Divergent**: responses diverging from a stimulated contact.
* Evaluation of CNN baselines and a CNN–Transformer hybrid model.
* Generalisation to unseen patients.

Our replication project:

* Reproduces the preprocessing pipeline on an open-source dataset (ds004080).
* Re-runs the CNN and Transformer models using the authors’ released code.
* Compares performance to the original reported metrics.
* Adds an extension that changes the stimulation paradigm for the Transformer models.

---

## Repository Structure (high level)

Exact paths may differ slightly depending on how you organise the project, but the main components are:

* `benchmark/`
  Benchmarking to determine memory improvements when used the streaming approach to pre-processing the ECoG dataset.

* `data/`
  Raw and intermediate data. Assumes:

  * `data/mean/` – per-channel SPES response means.
  * `data/std/` – per-channel SPES response standard deviations.

* `dataset.py`
  Dataset creation utilities and the `create_dataset` function, which returns train/val/test `DataLoader`s and class imbalance weights.

* `models.py`
  Model definitions and helpers:

  * CNN (convergent)
  * CNN (divergent)
  * Transformer (base)
  * Transformer (all)
  * Model loading utilities for evaluation.

* `train.py`
  Training utilities:

  * `train_model(...)` – generic training loop with early stopping.
  * `train_and_evaluate(...)` – trains one model on one fold and evaluates it.

* `evaluate.py`
  Metric computation and threshold selection:

  * AUROC / AUPRC (averaged and all).
  * Youden’s J statistic, sensitivity, specificity.
  * Threshold selection by maximizing Youden’s J on validation data.

* `notebooks/`
  Jupyter/Colab notebooks for:

  * Running preprocessing.
  * Training models across 5 folds.
  * Summarising results.

---

## Environment

The experiments were run with:

* Python 3.11.8
* Key packages (versions used in the replication):

  * `torch==2.1.0`
  * `torcheeg==1.0.11`
  * `mne==1.4.2`
  * `mne_bids==0.13`
  * `numpy==1.25.1`
  * `pandas==2.0.3`
  * `scikit_learn==1.3.0`
  * `tqdm==4.65.0`

Training was done in Google Colab (T4-class GPU) using a Python 3.11 environment (older runtime to maintain compatibility with `torcheeg`).

---

## Data and Preprocessing

### Dataset

We use the OpenNeuro dataset:

* ds004080 v1.2.4
* ECoG recordings from 74 patients (ages 4–51) undergoing presurgical evaluation.
* SPES performed at 0.2 Hz, with current intensities of 4 or 8 mA.

The original paper restricts analysis to 35 patients with at least one SOZ electrode and uses both sampling rates (512 Hz and 2048 Hz).
In practice, the released preprocessing code assumes a uniform sampling rate, which does not hold for the full dataset.

In this replication, we:

* Restrict to patients with:

  * at least one SOZ electrode, and
  * a 512 Hz sampling rate.
* This yields 20 patients in the final training set.

### Preprocessing Steps (high level)

1. Download the dataset from OpenNeuro.
2. Use MNE/MNE-BIDS to:

   * Load ECoG recordings and BIDS metadata.
   * Identify stimulation events and corresponding responses.
3. Extract SPES-locked segments around stimulation events.
4. Z-score channels using per-channel `mean` and `std` computed from the training folds:

   * Stored as tensors under `data/mean/` and `data/std/`.
5. Encode labels indicating whether the stimulated electrode lies in the clinically defined SOZ.

Preprocessing is implemented in the preprocessing scripts and notebooks in this repository, following the logic of the original authors’ code with adjustments for sampling rates.

---

## Training

Training is organised around 5-fold cross-validation over patients. For each fold:

* Construct train/validation/test splits using `create_dataset(...)`.
* Initialise the model via `get_model_instance(model_name, **hyperparams)` in `models.py`.
* Use `train_model(...)` from `train.py` to:

  * Train up to a fixed number of epochs.
  * Compute validation AUROC each epoch.
  * Save the checkpoint achieving the best validation AUROC.

Key hyperparameters for the Transformer (all) reproduction:

* Learning rate: 0.003368045116199473
* Batch size: 8
* Epochs: 10
* Embedding dimension: 16
* Number of Transformer layers: 2
* Dropout: 0.439

Loss function:

* `BCEWithLogitsLoss` with `pos_weight` set from class imbalance in each fold.

Optimiser:

* `AdamW` over all model parameters.

Training can be run via the provided Colab notebook (`train models` section) or by calling `train_and_evaluate(...)` directly in Python for each fold.

---

## Evaluation

For each model and fold:

1. Load the best checkpoint according to validation AUROC.
2. Compute metrics on the held-out test set using `get_thresh_and_evaluate(...)`:

   * AUROC (averaged) and AUPRC (averaged):
     per-patient metrics averaged over patients.
   * AUROC (all) and AUPRC (all):
     computed over all SPES trials pooled together.
3. Choose a probability threshold by maximizing Youden’s J statistic on validation data:

   * J = sensitivity + specificity − 1.
4. Using the chosen threshold, compute:

   * Sensitivity (averaged)
   * Specificity (averaged)
   * Youden (averaged)
   * Baseline (averaged/all) – class prevalence.

The final performance numbers reported below are the mean across 5 folds.

---

## Main Reproduction Results

Base models reproduced in this project:

* CNN (convergent)
* CNN (divergent)
* Transformer (base)
* Transformer (all)

All values below are mean across folds for averaged metrics.

| Model              | AUROC | AUPRC | Youden | Specificity | Sensitivity |
|--------------------|:-----:|:-----:|:------:|:-----------:|:-----------:|
| CNN (convergent)   | 0.579 | 0.221 | 0.095  | 0.678       | 0.417       |
| **CNN (divergent)**| **0.645** | **0.233** | **0.236** | 0.648       | 0.588       |
| Transformer (all)  | 0.565 | 0.196 | 0.004  | **0.754**   | 0.249       |
| Transformer (base) | 0.623 | 0.189 | 0.138  | 0.533       | **0.605**   |

Key observations:

* In the original paper, Transformer (all, convergent) is reported as the best-performing configuration.
* In our replication, the best-performing model is **CNN (divergent)**, not a Transformer variant.
* Transformer (all) in our setting achieves high specificity but relatively low sensitivity.

This suggests that:

* Performance is sensitive to:

  * stimulation paradigm (convergent vs divergent),
  * preprocessing details (sampling rate restrictions, artifact treatment),
  * training budget and hyperparameter choices.
* The advantages of the Transformer architecture reported in the original work may depend on a combination of these factors.

---

## Reproduction Results Summary

We reproduced four baseline models from Norris et al. (2024):
- CNN-Convergent
- CNN-Divergent
- Transformer-All
- Transformer-Base

Our best-performing model was **CNN-Divergent**, which contrasts with the original paper where **Transformer-Convergent was reported best**. Differences likely arise from smaller dataset size, fewer training epochs, and preprocessing variance.

| Model | AUROC (avg) |
|---|---|
| Transformer-All (original) | **0.73** |
| CNN-Divergent (ours) | **0.645** |
| Transformer-All (ours) | **0.565** |
| Transformer-Divergent-Base (extension) | **0.629** |

## Extension: Divergent-Transformer

Since Divergent CNN outperformed all models in our runs, we trained a **divergent-Transformer** variant, not tested in the original study. It performed better than our reproduced transformer implementation, suggesting stimulus-paradigm choice is an important factor in SOZ localization research.


## Notes and Limitations

* We restricted to 20 patients (512 Hz only) due to sampling rate assumptions in the authors’ preprocessing code.
* We trained for 10 epochs per fold instead of training until early stopping over a longer horizon.
* Some details of the original preprocessing (artifact removal, exclusion rules) are inferred from code rather than fully specified in the paper.
* For reproducibility, anyone using this code should document:

  * exact patient lists,
  * sampling rate filters,
  * preprocessing parameter choices.

---

## References

* Norris et al., “Localising the Seizure Onset Zone from Single-Pulse Electrical Stimulation Responses with a CNN Transformer,” 2024.
* ds004080, “Single-pulse electrical stimulation for seizure mapping,” OpenNeuro.
