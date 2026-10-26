"""Validate persisted/imported trust without changing site approval or TLS policy.

Incident key identities: Mozilla's October 20, 2026 disclosure:
https://www.openwall.com/lists/oss-security/2026/10/20/1
SPKI matching also rejects cross-signed certificates using the same key.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
from pathlib import Path
import re
import ssl

from cryptography import x509
from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

def _incident_keys(values: tuple[str, ...]) -> frozenset[str]:
    """Fail closed on a malformed or duplicated SHA-256 policy entry."""
    if any(re.fullmatch(r"[0-9a-f]{64}", value) is None for value in values):
        raise ValueError("Incident key policy requires lowercase SHA-256 values")
    if len(set(values)) != len(values):
        raise ValueError("Incident key policy contains duplicate values")
    return frozenset(values)


BLOCKED_KEYS = _incident_keys((
    "bd153ed7b0434f6886b17bce8bbe84ed340c7132d702a8f4fa318f756ecbd6f3",
    "c619e4780ed8e0abeda24ad732567de4383a7ea941338f6d1a7d1b49ac792fe9",
    "8d417db2dd8bf5e3084d1e3f196d583849d81bdd4c00c70b9d39369e96b8c782",
    "e0254c7fcdc265e2f0f8a428dabb75ab4ae039b4872d62f5ee57f0877d5a8a41",
    "43bffa19d6ef651451f6841e019931e96f6f2eaeff28ab4b6f1ce4576de2717b",
    "ebed6475c2c2d80fcb199f3fe8dd6e6b3ce60b77eb15d4e42c3dec0c6f5b5105",
    "5c0660a2b164910d8ff589c18e14552e9e0ec237dcefe2cb736d41a4811f81a0",
    "63ecefee431d49523bc1136c4e72d0206a477086caf606cd5cf025686c109cf8",
    "49dd353dc2b919a3770645117d0e60c16115e7d1bc259eefe734b00ea434fe5f",
    "ec4ffa1ad0ac88081314b7aaffef6a91f97cd57291bb5ba686c5415f5eb4f6b6",
    "92c063d67e8f14db71d288e11266ffdaf69cbf115f7bab14f3bc2f68d25e0e30",
))
MAX_BUNDLE_BYTES = 4 * 1024 * 1024


def read_bundle(path: Path) -> bytes:
    with path.open("rb") as source:
        data = source.read(MAX_BUNDLE_BYTES + 1)
    if len(data) > MAX_BUNDLE_BYTES:
        raise ValueError("CA bundle exceeds size limit")
    return data


@lru_cache(maxsize=4)
def validate_bundle(data: bytes, *, imported: bool = False) -> None:
    if len(data) > MAX_BUNDLE_BYTES:
        raise ValueError("CA bundle exceeds size limit")
    remainder = re.sub(rb"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", b"", data, flags=re.DOTALL)
    if any(line.strip() and not line.lstrip().startswith(b"#") for line in remainder.splitlines()):
        raise ValueError("CA bundle contains non-certificate material")
    try:
        for certificate in x509.load_pem_x509_certificates(data):
            public_key = certificate.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
            if hashlib.sha256(public_key).hexdigest() in BLOCKED_KEYS:
                raise ValueError("CA bundle contains a distrusted incident key; refresh approved trust")
            if imported:
                try:
                    if not certificate.extensions.get_extension_for_class(x509.BasicConstraints).value.ca:
                        raise ValueError("Imported certificate is not a CA")
                    try:
                        if not certificate.extensions.get_extension_for_class(x509.KeyUsage).value.key_cert_sign:
                            raise ValueError("Imported CA cannot sign certificates")
                    except x509.ExtensionNotFound:
                        pass
                except x509.ExtensionNotFound as exc:
                    raise ValueError("Imported certificate lacks CA constraints") from exc
    except (UnsupportedAlgorithm, x509.InvalidVersion, x509.DuplicateExtension, x509.UnsupportedGeneralNameType) as exc:
        raise ValueError("CA bundle contains unsupported or invalid certificate data") from exc
    # Also require OpenSSL to accept the complete bundle, with verification on.
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(cadata=data.decode("ascii"))


def build_bundle(system: Path, approved_ca: Path, destination: Path) -> None:
    """Create a new candidate; never overwrite an existing/persisted bundle."""
    base, additional = read_bundle(system), read_bundle(approved_ca)
    validate_bundle(base)
    validate_bundle(additional, imported=True)
    combined = base.rstrip() + b"\n" + additional.rstrip() + b"\n"
    validate_bundle(combined)
    with destination.open("xb") as output:
        output.write(combined)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--system", type=Path, default=Path("/etc/ssl/certs/ca-certificates.crt"))
    parser.add_argument("--approved-ca", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    try:
        build_bundle(args.system, args.approved_ca, args.destination)
    except (OSError, ValueError):
        # Deliberately omit certificate subjects, local paths and raw exceptions.
        parser.exit(1, "Trust bundle rejected; use a corrected image and approved CA-only input.\n")
