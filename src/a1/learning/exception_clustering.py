"""Clustering algorithm for grouping similar exceptions."""

from collections import defaultdict
from dataclasses import dataclass
from typing import Any


@dataclass
class ExceptionCluster:
    """Represents a cluster of similar exceptions."""

    id: str
    center: dict[str, Any]
    members: list[dict[str, Any]]
    rule_id: str
    common_reason: str
    size: int

    def similarity_score(self, exception: dict[str, Any]) -> float:
        """Calculate similarity between exception and cluster center."""
        score = 0.0
        total_weight = 0.0

        # Compare features
        for key, center_value in self.center.items():
            if key in exception:
                weight = self._get_feature_weight(key)
                if isinstance(center_value, str):
                    score += weight if exception[key] == center_value else 0
                elif isinstance(center_value, int | float):
                    diff = abs(exception[key] - center_value)
                    score += weight * max(0, 1 - diff)
                total_weight += weight

        return score / total_weight if total_weight > 0 else 0

    def _get_feature_weight(self, feature: str) -> float:
        """Get weight for a feature in similarity calculation."""
        weights = {
            "file_path": 0.3,
            "user_intent": 0.3,
            "workflow_phase": 0.2,
            "developer_experience": 0.1,
            "time_pressure": 0.1,
        }
        return weights.get(feature, 0.1)

    def update_center(self) -> None:
        """Update cluster center based on members."""
        if not self.members:
            return

        new_center = {}
        for key in self.members[0]:
            values = [m[key] for m in self.members if key in m]

            if all(isinstance(v, str) for v in values):
                # For strings, use most common
                new_center[key] = max(set(values), key=values.count)
            elif all(isinstance(v, int | float) for v in values):
                # For numbers, use mean
                new_center[key] = sum(values) / len(values)

        self.center = new_center

    def get_common_override_reason(self) -> str:
        """Extract common override reason from members."""
        reasons = [m.get("override_reason", "") for m in self.members if m.get("override_reason")]

        if not reasons:
            return "No common reason found"

        # Simple approach: find common words
        word_freq = defaultdict(int)
        for reason in reasons:
            for word in reason.lower().split():
                if len(word) > 3:  # Skip short words
                    word_freq[word] += 1

        # Get top 3 most common words
        common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:3]
        return " ".join([word for word, _ in common_words])


class ExceptionClusterer:
    """Clusters similar exceptions to identify patterns."""

    def __init__(self, min_cluster_size: int = 3):
        self.min_cluster_size = min_cluster_size
        self.clusters: dict[str, ExceptionCluster] = {}

    def cluster_exceptions(self, exceptions: list[dict[str, Any]], rule_id: str) -> list[ExceptionCluster]:
        """Cluster similar exceptions using simple algorithm."""
        if len(exceptions) < self.min_cluster_size:
            return []

        # Initialize clusters
        clusters = []
        unassigned = list(exceptions)
        cluster_id = 0

        while unassigned:
            # Start new cluster with first unassigned exception
            seed = unassigned.pop(0)
            cluster = ExceptionCluster(
                id=f"{rule_id}_cluster_{cluster_id}",
                center=seed,
                members=[seed],
                rule_id=rule_id,
                common_reason="",
                size=1,
            )

            # Find similar exceptions
            threshold = 0.7  # Similarity threshold
            assigned = []

            for i, exc in enumerate(unassigned):
                if cluster.similarity_score(exc) >= threshold:
                    cluster.members.append(exc)
                    cluster.size += 1
                    assigned.append(i)

            # Remove assigned exceptions
            for i in reversed(assigned):
                unassigned.pop(i)

            # Update cluster if it meets minimum size
            if cluster.size >= self.min_cluster_size:
                cluster.update_center()
                cluster.common_reason = cluster.get_common_override_reason()
                clusters.append(cluster)
                cluster_id += 1

        return clusters

    def find_cluster_for_exception(self, exception: dict[str, Any], rule_id: str) -> ExceptionCluster | None:
        """Find the best matching cluster for an exception."""
        rule_clusters = [c for c in self.clusters.values() if c.rule_id == rule_id]

        if not rule_clusters:
            return None

        # Find cluster with highest similarity
        best_cluster = None
        best_score = 0.0
        threshold = 0.6

        for cluster in rule_clusters:
            score = cluster.similarity_score(exception)
            if score > best_score and score >= threshold:
                best_score = score
                best_cluster = cluster

        return best_cluster

    def update_clusters(self, new_exceptions: list[dict[str, Any]], rule_id: str) -> None:
        """Update existing clusters with new exceptions."""
        for exc in new_exceptions:
            cluster = self.find_cluster_for_exception(exc, rule_id)

            if cluster:
                # Add to existing cluster
                cluster.members.append(exc)
                cluster.size += 1
                cluster.update_center()
                cluster.common_reason = cluster.get_common_override_reason()
            else:
                # Try to form new cluster with unassigned exceptions
                unassigned = [exc]
                for other_exc in new_exceptions:
                    if other_exc != exc and not self.find_cluster_for_exception(other_exc, rule_id):
                        unassigned.append(other_exc)

                # Attempt clustering on unassigned
                new_clusters = self.cluster_exceptions(unassigned, rule_id)
                for cluster in new_clusters:
                    self.clusters[cluster.id] = cluster

    def get_cluster_insights(self, rule_id: str) -> dict[str, Any]:
        """Get insights about clusters for a rule."""
        rule_clusters = [c for c in self.clusters.values() if c.rule_id == rule_id]

        if not rule_clusters:
            return {"clusters": 0, "insights": []}

        insights = []
        for cluster in rule_clusters:
            # Analyze cluster characteristics
            insight = {
                "cluster_id": cluster.id,
                "size": cluster.size,
                "common_reason": cluster.common_reason,
                "characteristics": {},
            }

            # Find defining characteristics
            if "file_path" in cluster.center:
                path = cluster.center["file_path"]
                if "/test" in path:
                    insight["characteristics"]["type"] = "test_files"
                elif "/docs" in path:
                    insight["characteristics"]["type"] = "documentation"

            if "user_intent" in cluster.center:
                intent = cluster.center["user_intent"]
                insight["characteristics"]["intent"] = intent

            if "developer_experience" in cluster.center:
                exp = cluster.center["developer_experience"]
                if exp > 0.7:
                    insight["characteristics"]["experience"] = "senior"
                elif exp < 0.3:
                    insight["characteristics"]["experience"] = "junior"

            insights.append(insight)

        return {
            "clusters": len(rule_clusters),
            "total_exceptions": sum(c.size for c in rule_clusters),
            "insights": insights,
        }

    def suggest_rule_adjustments(self, rule_id: str) -> list[dict[str, Any]]:
        """Suggest rule adjustments based on clusters."""
        insights = self.get_cluster_insights(rule_id)
        suggestions = []

        for insight in insights.get("insights", []):
            chars = insight["characteristics"]

            # Suggest adjustments based on patterns
            if chars.get("type") == "test_files" and insight["size"] > 5:
                suggestions.append(
                    {
                        "type": "relax_for_context",
                        "context": "test_files",
                        "reason": f"High override rate ({insight['size']} cases) for test files",
                        "suggested_level": "INFORM",
                    }
                )

            if chars.get("experience") == "senior" and insight["size"] > 3:
                suggestions.append(
                    {
                        "type": "trust_experienced",
                        "context": "senior_developers",
                        "reason": f"Senior developers frequently override ({insight['size']} cases)",
                        "suggested_level": "WARN",
                    }
                )

            if "hotfix" in chars.get("intent", "").lower():
                suggestions.append(
                    {
                        "type": "emergency_exception",
                        "context": "hotfix",
                        "reason": "Hotfixes require faster execution",
                        "suggested_level": "INFORM",
                    }
                )

        return suggestions
