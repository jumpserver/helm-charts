#!/usr/bin/env python3
"""Offline Helm regression checks. Requires Helm 3 and PyYAML; no cluster access."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
HELM = os.environ.get("HELM", "helm")


class GraphicalSessions(unittest.TestCase):
    def render(self, app_version="v4.10.20", values=None):
        with tempfile.TemporaryDirectory() as directory:
            chart = Path(directory) / "jumpserver"
            shutil.copytree(ROOT / "charts/jumpserver", chart)
            metadata = yaml.safe_load((chart / "Chart.yaml").read_text())
            metadata["appVersion"] = app_version
            (chart / "Chart.yaml").write_text(yaml.safe_dump(metadata))
            config = {"core": {"config": {
                "secretKey": "test-only-secret-not-for-production",
                "bootstrapToken": "test-only-token-not-for-production",
            }}}
            for key, value in (values or {}).items():
                config[key] = value
            value_file = Path(directory) / "values.yaml"
            value_file.write_text(yaml.safe_dump(config))
            args = [str(chart), "-f", str(value_file)]
            subprocess.run([HELM, "lint", "--strict", *args], check=True, capture_output=True, text=True)
            output = subprocess.check_output([HELM, "template", "test", *args], text=True)
            return {(doc["kind"], doc["metadata"]["name"]): doc
                    for doc in yaml.safe_load_all(output) if doc}

    def lion(self, docs):
        return {key: value for key, value in docs.items() if "-jms-lion" in key[1]}

    def nginx(self, docs):
        return "\n".join(str(value) for (kind, _), doc in docs.items()
                         if kind == "ConfigMap" for value in doc.get("data", {}).values())

    def test_v4_default_and_semver_variants(self):
        for version in ("v4.10.20", "4.10.20", "v4.10.20-lts"):
            with self.subTest(version=version):
                docs = self.render(version)
                self.assertEqual({kind for kind, _ in self.lion(docs)},
                                 {"Deployment", "Service", "PersistentVolumeClaim"})
                deployment = docs["Deployment", "test-jumpserver-jms-lion"]
                container = deployment["spec"]["template"]["spec"]["containers"][0]
                self.assertEqual(container["image"], f"docker.io/jumpserver/lion:{version}-ce")
                self.assertIn("location /lion/", self.nginx(docs))
                pvc = docs["PersistentVolumeClaim", "test-jumpserver-jms-lion-data"]
                self.assertEqual(pvc["metadata"]["annotations"]["helm.sh/resource-policy"], "keep")
                self.assertEqual(pvc["spec"]["storageClassName"], "jumpserver-data")

    def test_v4_disabled(self):
        docs = self.render(values={"lion": {"enabled": False}})
        self.assertFalse(self.lion(docs))
        self.assertNotIn("location /lion/", self.nginx(docs))

    def test_v4_independent_of_koko(self):
        docs = self.render(values={"koko": {"enabled": False}})
        self.assertEqual(len(self.lion(docs)), 3)
        self.assertIn("location /lion/", self.nginx(docs))

    def test_v4_existing_claim(self):
        docs = self.render(values={"lion": {"persistence": {"existingClaim": "saved-lion-data"}}})
        self.assertNotIn(("PersistentVolumeClaim", "test-jumpserver-jms-lion-data"), docs)
        volumes = docs["Deployment", "test-jumpserver-jms-lion"]["spec"]["template"]["spec"]["volumes"]
        self.assertTrue(any(v.get("persistentVolumeClaim", {}).get("claimName") == "saved-lion-data" for v in volumes))

    def test_v4_storage_and_overrides(self):
        docs = self.render(values={"global": {"storageClass": "global-sc", "imageRegistry": "mirror.example", "imageOwner": "custom"},
                                   "lion": {"replicaCount": 2, "service": {"web": {"port": 8181}},
                                            "persistence": {"storageClassName": "lion-sc"},
                                            "env": {"CUSTOM_TEST": "preserved"}}})
        deployment = docs["Deployment", "test-jumpserver-jms-lion"]
        self.assertEqual(deployment["spec"]["replicas"], 2)
        container = deployment["spec"]["template"]["spec"]["containers"][0]
        self.assertEqual(container["image"], "mirror.example/custom/lion:v4.10.20-ce")
        self.assertIn({"name": "CUSTOM_TEST", "value": "preserved"}, container["env"])
        self.assertIn("jms-lion:8181", self.nginx(docs))
        self.assertEqual(docs["PersistentVolumeClaim", "test-jumpserver-jms-lion-data"]["spec"]["storageClassName"], "global-sc")
        docs = self.render(values={"lion": {"persistence": {"storageClassName": "lion-sc"}}})
        self.assertEqual(docs["PersistentVolumeClaim", "test-jumpserver-jms-lion-data"]["spec"]["storageClassName"], "lion-sc")

    def test_v5_never_deploys_lion(self):
        for version in ("v5.0.0", "v5.1.1", "v5.0.0-rc.1"):
            for enabled in (True, False):
                with self.subTest(version=version, enabled=enabled):
                    docs = self.render(version, {"lion": {"enabled": enabled}})
                    self.assertFalse(self.lion(docs))
                    self.assertNotIn("annotations", docs["Deployment", "test-jumpserver-jms-web"]["spec"]["template"]["metadata"])
                    self.assertNotIn("location /lion/", self.nginx(docs))
                    self.assertIn("location /koko/", self.nginx(docs))

    def test_v5_ignores_null_lion_config(self):
        self.assertFalse(self.lion(self.render("v5.1.1", {"lion": None})))

    def test_web_config_triggers_rollout(self):
        for version in ("v4.10.20", "v4.10.20-lts"):
            with self.subTest(version=version):
                first = self.render(version)
                changed = self.render(version, {"koko": {"service": {"web": {"port": 5999}}}})
                def checksum(docs):
                    return docs["Deployment", "test-jumpserver-jms-web"]["spec"]["template"]["metadata"]["annotations"]["checksum/config"]
                self.assertEqual(len(checksum(first)), 64)
                self.assertNotEqual(checksum(first), checksum(changed))
                self.assertEqual(checksum(first), checksum(self.render(version)))
        enabled = self.render()
        disabled = self.render(values={"lion": {"enabled": False}})
        self.assertNotEqual(checksum(enabled), checksum(disabled))

    def test_enterprise_video_storage(self):
        for version in ("v4.10.20", "v5.1.1"):
            with self.subTest(version=version):
                docs = self.render(version, {"xpack": {"enabled": True},
                                             "video": {"persistence": {"storageClassName": "video-sc"}}})
                self.assertEqual(docs["PersistentVolumeClaim", "test-jumpserver-jms-video-data"]["spec"]["storageClassName"], "video-sc")
                if version.startswith("v4"):
                    image = docs["Deployment", "test-jumpserver-jms-lion"]["spec"]["template"]["spec"]["containers"][0]["image"]
                    self.assertEqual(image, "docker.io/jumpserver/lion:v4.10.20-ee")


if __name__ == "__main__":
    unittest.main(verbosity=2)
