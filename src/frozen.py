"""Self-contained wrapper for the frozen model artifact (US-11, issue #27).

``src.compare_models`` serialises a dict ``{"model", "frozen_params",
"trained_on", "rows"}`` where ``model`` is this wrapper. It exists for one
reason: the boosting Pipeline needs numeric labels (its training script encodes
the target), while the prediction app calls ``predict`` and expects ``A``/``B``/
``C``/``D``. Encoding here keeps the artifact self-contained: original labels in
and out, whatever the estimator needs internally.

It inherits ``ClassifierMixin`` and ``BaseEstimator`` so tools that inspect
scikit-learn estimators (``permutation_importance``, ``is_classifier``, the
``score`` convenience method) accept it as a classifier.

The class lives in its own module, not in the script that writes the artifact,
because a class defined in a module executed with ``python -m`` is pickled as
``__main__.FrozenPipeline`` and then cannot be unpickled anywhere else.
"""

from __future__ import annotations

from typing import Any

from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.preprocessing import LabelEncoder

__all__ = ["FrozenPipeline"]


class FrozenPipeline(ClassifierMixin, BaseEstimator):
    """Pipeline wrapper that encodes labels on fit and decodes them on predict."""

    def __init__(self, pipeline: Any):
        self.pipeline = pipeline

    def fit(self, X, y):
        self._encoder = LabelEncoder()
        codes = self._encoder.fit_transform(y)
        self.pipeline.fit(X, codes)
        self.classes_ = self._encoder.classes_
        self.n_features_in_ = getattr(self.pipeline, "n_features_in_", None)
        return self

    def predict(self, X):
        return self._encoder.inverse_transform(self.pipeline.predict(X))

    def predict_proba(self, X):
        return self.pipeline.predict_proba(X)
