"""Inspect the original PICO 4 Enterprise APK. This does not replace a headset test."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "unity-vr"
APK = PROJECT / "Builds/Android/Leichhardt-PICO4-Enterprise.apk"
ANDROID = Path("C:/Program Files/Unity/Hub/Editor/6000.6.9f1/Editor/Data/PlaybackEngines/AndroidPlayer")
TOOLS = ANDROID / "SDK/build-tools/36.0.0"
PROFILE = json.loads((PROJECT / "Builds/Android/PICO4-Enterprise-profile.json").read_text())
OUT = ROOT / f"output/vr/pico4-enterprise-{PROFILE['version']}"


def run(*args):
    return subprocess.run([str(a) for a in args], check=True, capture_output=True, text=True).stdout


def sha(path):
    return hashlib.file_digest(path.open("rb"), "sha256").hexdigest()


assert PROFILE["result"] == "PASS" and PROFILE["restoredOriginalSettings"]
assert set(PROFILE["enabledFeatures"]) == {"PICO4ControllerProfile", "LeichhardtPico4Support"}
assert PROFILE["targetPicoOS"] == "5.9.9" and PROFILE["requestedRefreshHz"] == 72
badging = run(TOOLS / "aapt.exe", "dump", "badging", APK)
manifest = run(TOOLS / "aapt.exe", "dump", "xmltree", APK, "AndroidManifest.xml")
assert "name='au.edu.evolve.framelab'" in badging
assert f"versionName='{PROFILE['version']}'" in badging
assert f"versionCode='{PROFILE['versionCode']}'" in badging
assert "native-code: 'arm64-v8a'" in badging and "sdkVersion:'29'" in badging
assert "com.unity3d.player.UnityPlayerActivity" in badging
assert re.search(r'pvr.app.type[^\n]*\n[^\n]*"vr"', manifest)
assert "org.khronos.openxr.runtime_broker" in manifest
assert "org.khronos.openxr.permission.OPENXR" in manifest
assert not re.search(r"pvr.sdk.version|pxr.sdk.version_code|com.oculus|tobservice|picovr", manifest, re.I)
package = next((PROJECT / "Library/PackageCache").glob("com.unity.xr.openxr@*"))
with zipfile.ZipFile(package / "RuntimeLoaders/android/openxr_loader.aar") as archive:
    loader = archive.read("jni/arm64-v8a/libopenxr_loader.so")
with zipfile.ZipFile(APK) as archive:
    assert archive.testzip() is None
    libraries = sorted(n for n in archive.namelist() if n.startswith("lib/"))
    assert all(n.startswith("lib/arm64-v8a/") for n in libraries)
    assert not any("pico" in n.lower() or "pxr" in n.lower() for n in libraries)
    assert archive.read("lib/arm64-v8a/libopenxr_loader.so") == loader
    assert b"LeichhardtPico4Support" in archive.read("assets/bin/Data/Managed/Metadata/global-metadata.dat")
    assert "assets/bin/Data/level0" in archive.namelist()

# Inspect the code emitted for this build: the shared default is 90, this variant must compile 72.
cpp = PROJECT / "Library/Bee/artifacts/Android/il2cppOutput/cpp/Assembly-CSharp.cpp"
assert re.search(r"Application_set_targetFrameRate_[^(]+\(\(\(int32_t\)72\), NULL\);", cpp.read_text())
java = ANDROID / "OpenJDK/bin/java.exe"
signer = TOOLS / "lib/apksigner.jar"
signature = run(java, "-jar", signer, "verify", "--verbose", "--print-certs", APK)
previous_signature = run(java, "-jar", signer, "verify", "--print-certs", PROJECT / "Builds/Android/Leichhardt-PICO.apk")
cert_pattern = r"certificate SHA-256 digest: ([0-9a-f]+)"
assert re.search(cert_pattern, signature)[1] == re.search(cert_pattern, previous_signature)[1]
assert "Verified using v2 scheme (APK Signature Scheme v2): true" in signature

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "apk-manifest.txt").write_text(manifest)
(OUT / "apk-badging.txt").write_text(badging)
(OUT / "apk-signature.txt").write_text(signature)
(OUT / "profile.json").write_text(json.dumps(PROFILE, indent=2))
report = {
    "result": "PASS", "scope": "Build profile, APK integrity, manifest, ARM64 libraries, standard loader, compiled 72 FPS target and matching development signature. Not an on-device test.",
    "timestamp": datetime.datetime.now().astimezone().isoformat(),
    "version": PROFILE["version"], "version_code": PROFILE["versionCode"],
    "target": PROFILE["device"], "target_pico_os": "5.9.9",
    "apk": APK.relative_to(ROOT).as_posix(), "bytes": APK.stat().st_size, "sha256": sha(APK),
    "native_libraries": libraries, "standard_openxr_loader_matches_unity": True,
    "newer_pico_native_libraries_absent": True, "signature_matches_existing_pico_apk": True,
    "compiled_target_fps": 72, "requested_display_refresh_hz": 72,
    "physical_device_validation": "NOT TESTED: no original PICO 4 Enterprise connected.",
    "reported_previous_crash": "Leichhardt-PICO.apk on PICO OS 5.9.9. Newer SDK/firmware mismatch identified; no crash log available to establish the exact cause.",
    "sources": ["https://developer.picoxr.com/document/native/release-notes/",
                "https://github.com/Pico-Developer/PICO-Unity-OpenXR-SDK/blob/3aa3e62bff41df618529eeb60ff02c29a515dafe/README.md"],
}
(OUT / "apk-validation.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
